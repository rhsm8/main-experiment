"""
run.py

Design:
    15 topics
    x 3 agents (L / M / R)
    x 20 runs
    per model-language pair
    prompt: original x I3 (config.py)
    
Models: 
    openai/gpt-oss-20b
    google/gemma-4-31B-it-qat-w4a16-ct
    llm-jp/llm-jp-4.1-33b-thinking
    Qwen/Qwen3.6-27B-FP8
    plamo-3.1-prime

Command:
    <gpt, gemma, llm-jp, qwen>
    python run.py --provider mdx --model openai/gpt-oss-20b --language en --runs 20
    <plamo>
    python run.py --provider plamo --model plamo-3.1-prime --language ja --runs 20
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI

from config import TOPICS, AGENTS, get_topic, build_prompt, parse_response


DEFAULT_RUNS = 20
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 4048
DEFAULT_SLEEP = 0.5
DEFAULT_SEED = 42
MAX_RETRIES = 5

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "results"
OUTPUT_DIR.mkdir(exist_ok=True)

load_dotenv(BASE_DIR.parent / ".env")
load_dotenv(BASE_DIR / ".env")


# =========================================================
# CLIENT
# =========================================================
def make_client(provider: str):
    # if provider == "groq":
    #     api_key = os.getenv("GROQ_API_KEY")
    #     if not api_key:
    #         raise RuntimeError("GROQ_API_KEY is not set.")
    #     return Groq(api_key=api_key)

    # if provider == "openai":
    #     api_key = os.getenv("OPENAI_API_KEY")
    #     if not api_key:
    #         raise RuntimeError("OPENAI_API_KEY is not set.")
    #     return OpenAI(api_key=api_key)

    if provider == "mdx":
        api_key = os.getenv("MDX_API_KEY")
        base_url = os.getenv("MDX_BASE_URL")
        if not api_key:
            raise RuntimeError("MDX_API_KEY is not set.")
        if not base_url:
            raise RuntimeError("MDX_BASE_URL is not set. Set it in your .env file.")
        return OpenAI(base_url=base_url, api_key=api_key)

    if provider == "plamo":
        api_key = os.getenv("PLAMO_API_KEY")
        if not api_key:
            raise RuntimeError("PLAMO_API_KEY is not set.")
        return OpenAI(
            api_key=api_key,
            base_url="https://api.platform.preferredai.jp/v1",
        )

    raise ValueError(f"Unsupported provider: {provider}")


# =========================================================
# CALLING THE MODEL
# =========================================================
def extract_reasoning(message) -> str:
    """
    Reasoning / thinking text returned separately from the answer, if any.
    Field name differs by server: reasoning_content (vLLM etc.) or reasoning (Groq etc.).
    """
    for name in ("reasoning_content", "reasoning"):
        value = getattr(message, name, None)
        if value:
            return str(value)

    extra = getattr(message, "model_extra", None) or {}
    for name in ("reasoning_content", "reasoning"):
        if extra.get(name):
            return str(extra[name])

    return ""


def usage_to_dict(response) -> dict:
    usage = getattr(response, "usage", None)
    if usage is None:
        return {}
    try:
        return usage.model_dump()
    except Exception:
        return {}


def call_model(client, model, system, prompt, temperature, max_tokens):
    """
    Returns (text, latency, meta).
    system : persona (system message)
    prompt : statement + scale + output format (user message)
    """
    last_error = None

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ]

    for attempt in range(1, MAX_RETRIES + 1):
        start = time.perf_counter()
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_completion_tokens=max_tokens,
            )
            latency = time.perf_counter() - start

            choice = response.choices[0]
            text = (choice.message.content or "").strip()

            meta = {
                "reasoning": extract_reasoning(choice.message),
                "finish_reason": choice.finish_reason,
                "usage": usage_to_dict(response),
                "response_id": getattr(response, "id", None),
                "response_model": getattr(response, "model", None),
            }
            return text, latency, meta

        except Exception as exc:
            last_error = exc
            wait = min(2 ** (attempt - 1), 30)
            print(f"[WARN] API call failed ({attempt}/{MAX_RETRIES}): {exc}")
            if attempt < MAX_RETRIES:
                time.sleep(wait)

    raise RuntimeError(f"API call failed after retries: {last_error}")


# =========================================================
# OUTPUT
# =========================================================
CSV_FIELDS = [
    "timestamp_utc",
    "provider",
    "model",
    "language",
    "seed",
    "temperature",
    "max_tokens",
    "run",
    "id",
    "topic_id",
    "topic",
    "statement",
    "agent_id",
    "prompt",
    "response_raw",
    "finish_reason",
    "score",
    "parse_success",
    "latency_seconds",
    "error",
]


def sanitize_filename(value: str) -> str:
    return "".join(
        ch if ch.isalnum() or ch in ("-", "_", ".") else "_"
        for ch in value
    )


def make_output_paths(provider, model, language):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stem = f"{stamp}_{sanitize_filename(provider)}_{sanitize_filename(model)}_{language}"
    return OUTPUT_DIR / f"{stem}.csv", OUTPUT_DIR / f"{stem}.jsonl"


def append_csv(path: Path, row: dict):
    exists = path.exists()
    with path.open("a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerow({k: row.get(k, "") for k in CSV_FIELDS})


def append_jsonl(path: Path, row: dict):
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


# =========================================================
# MAIN EXPERIMENT LOOP
# =========================================================
def run_experiment(args):
    client = make_client(args.provider)
    language = args.language

    topics = [get_topic(t) for t in args.topics] if args.topics else TOPICS
    agents = [a for a in AGENTS if a["id"] in args.agents] if args.agents else AGENTS
    if not agents:
        raise ValueError(f"No matching agents: {args.agents}")

    jobs = [
        (topic, agent, run_no)
        for topic in topics
        for agent in agents
        for run_no in range(1, args.runs + 1)
    ]

    rng = random.Random(args.seed)
    rng.shuffle(jobs)

    csv_path, jsonl_path = make_output_paths(args.provider, args.model, language)

    print("=" * 70)
    print("EXPERIMENT (5-point scale, -2..+2)")
    print("=" * 70)
    print(f"Provider        : {args.provider}")
    print(f"Model           : {args.model}")
    print(f"Language        : {language}")
    print(f"Topics          : {len(topics)}")
    print(f"Agents          : {len(agents)}")
    print(f"Runs/condition  : {args.runs}")
    print(f"TOTAL API CALLS : {len(jobs)}")
    print(f"CSV             : {csv_path}")
    print(f"JSONL           : {jsonl_path}")
    print("=" * 70)

    for idx, (topic, agent, run_no) in enumerate(jobs, start=1):
        print(
            f"[{idx:04d}/{len(jobs)}] "
            f"{topic['topic_id']} | {agent['id']} | run={run_no}"
        )

        built = build_prompt(agent, topic, language)

        error = ""
        response_text = ""
        latency = None
        meta = {}
        score = None

        try:
            response_text, latency, meta = call_model(
                client=client,
                model=args.model,
                system=built["system"],
                prompt=built["prompt"],
                temperature=args.temperature,
                max_tokens=args.max_tokens,
            )
            score = parse_response(response_text)

        except Exception as exc:
            error = repr(exc)

        row = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "provider": args.provider,
            "model": args.model,
            "language": language,
            "seed": args.seed,
            "temperature": args.temperature,
            "max_tokens": args.max_tokens,
            "run": run_no,
            "id": topic["id"],
            "topic_id": topic["topic_id"],
            "topic": topic["topic"][language],
            "statement": topic["statement"][language],
            "agent_id": agent["id"],
            "system": built["system"],          # JSONL only
            "prompt": built["prompt"],
            "response_raw": response_text,
            # JSONL-only extras
            "reasoning": meta.get("reasoning", ""),
            "usage": meta.get("usage", {}),
            "response_id": meta.get("response_id", ""),
            "response_model": meta.get("response_model", ""),
            "finish_reason": meta.get("finish_reason", ""),
            "score": "" if score is None else score,
            "parse_success": int(score is not None),
            "latency_seconds": round(latency, 4) if latency is not None else "",
            "error": error,
        }

        append_csv(csv_path, row)
        append_jsonl(jsonl_path, row)

        print(f"  response={response_text!r} | score={score} | parsed={score is not None}")

        if args.sleep > 0:
            time.sleep(args.sleep)

    print("\nFinished.")
    print(f"CSV   : {csv_path}")
    print(f"JSONL : {jsonl_path}")


# =========================================================
# ENTRY POINT
# =========================================================
def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--provider",
        choices=["groq", "openai", "mdx", "plamo"],
        default="groq",
    )
    parser.add_argument("--model", default="llama-3.1-8b-instant")
    parser.add_argument("--language", choices=["en", "ja"], default="en")
    parser.add_argument("--runs", type=int, default=DEFAULT_RUNS)
    parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument("--sleep", type=float, default=DEFAULT_SLEEP)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)

    parser.add_argument(
        "--topics",
        nargs="*",
        default=None,
        help="Optional topic_id (or numeric id) subset. Example: --topics nuclear_power 3",
    )
    parser.add_argument(
        "--agents",
        nargs="*",
        default=None,
        help="Optional agent id subset. Example: --agents Agent_L Agent_R",
    )

    args = parser.parse_args()
    if args.topics:
        args.topics = [int(t) if t.isdigit() else t for t in args.topics]
    return args


if __name__ == "__main__":
    run_experiment(parse_args())