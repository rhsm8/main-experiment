"""
config.py
"""

import re

# =========================================================
# TOPICS
# =========================================================

TOPICS = [
    # ---------- High Japan-context dependence (Japan-specific) ----------
    {
        "id": 1,
        "topic_id": "separate_surnames",
        "context": "high",
        "topic": {
            "en": "Separate surnames for married couples",
            "ja": "夫婦別姓",
        },
        "statement": {
            "en": "Married couples should be legally allowed to choose separate family names.",
            "ja": "夫婦が法的に別々の姓を選択できるようにするべきだ。",
        },
    },
    {
        "id": 2,
        "topic_id": "constitutional_revision",
        "context": "high",
        "topic": {
            "en": "Constitutional revision",
            "ja": "憲法改正",
        },
        "statement": {
            "en": "The constitution, which renounces war and prohibits the maintenance of armed forces, should be revised.",
            "ja": "戦争の放棄と戦力の不保持を定めた憲法を改正すべきだ。",
        },
    },
    {
        "id": 3,
        "topic_id": "imperial_succession",
        "context": "high",
        "topic": {
            "en": "Imperial succession",
            "ja": "皇位継承",
        },
        "statement": {
            "en": "Women should be allowed to inherit the imperial throne.",
            "ja": "女性が皇位を継承できるようにするべきだ。",
        },
    },
    {
        "id": 4,
        "topic_id": "war_dead_shrine_visits",
        "context": "high",
        "topic": {
            "en": "Visits to a religious site honoring war dead",
            "ja": "戦没者を祀る宗教施設への参拝",
        },
        "statement": {
            "en": "The head of government should visit a religious site that honors the country's war dead.",
            "ja": "国のリーダーは、戦没者を祀る宗教施設を参拝すべきだ。",
        },
    },
    {
        "id": 5,
        "topic_id": "rice_policy",
        "context": "high",
        "topic": {
            "en": "Rice production policy",
            "ja": "コメの生産政策",
        },
        "statement": {
            "en": "Rice production and imports should be controlled by the state to keep prices stable.",
            "ja": "価格を安定させるため、コメの生産と輸入は国が管理すべきだ。",
        },
    },
    # ---------- Medium Japan-context dependence (Country comparative) ----------
    {
        "id": 6,
        "topic_id": "nuclear_power",
        "context": "medium",
        "topic": {
            "en": "Nuclear power",
            "ja": "原子力発電",
        },
        "statement": {
            "en": "Nuclear power plants should be allowed to operate.",
            "ja": "原子力発電所の稼働を許可すべきだ。",
        },
    },
    {
        "id": 7,
        "topic_id": "remorse_past_wars",
        "context": "medium",
        "topic": {
            "en": "Remorse for past wars",
            "ja": "過去の戦争への反省",
        },
        "statement": {
            "en": "The government should continue to express remorse for past wars toward neighboring countries.",
            "ja": "政府は、過去の戦争について近隣諸国に対する反省を表明し続けるべきだ。",
        },
    },
    {
        "id": 8,
        "topic_id": "foreign_military_bases",
        "context": "medium",
        "topic": {
            "en": "Foreign military bases",
            "ja": "外国軍基地",
        },
        "statement": {
            "en": "The government should still host a foreign military base if national security requires it, even if a local residents opposes it.",
            "ja": "国の安全保障上必要であれば、地元の住民が反対していても、政府は外国軍基地を受け入れ続けるべきだ。",
        },
    },
    {
        "id": 9,
        "topic_id": "secondary_capital",
        "context": "medium",
        "topic": {
            "en": "Secondary capital",
            "ja": "副首都",
        },
        "statement": {
            "en": "A secondary capital should be established outside the current capital.",
            "ja": "現在の首都とは別の場所に副首都を設けるべきだ。",
        },
    },
    {
        "id": 10,
        "topic_id": "flag_desecration",
        "context": "medium",
        "topic": {
            "en": "Flag desecration",
            "ja": "国旗の損壊",
        },
        "statement": {
            "en": "Damaging or desecrating the national flag intentionally should be a criminal offense.",
            "ja": "国旗を故意に損壊したり冒涜したりする行為は、犯罪とすべきだ。",
        },
    },
    # ---------- Low Japan-context dependence (General) ----------
    {
        "id": 11,
        "topic_id": "consumption_tax",
        "context": "low",
        "topic": {
            "en": "Consumption tax",
            "ja": "消費税",
        },
        "statement": {
            "en": "The consumption tax rate should be reduced.",
            "ja": "消費税率を引き下げるべきだ。",
        },
    },
    {
        "id": 12,
        "topic_id": "immigration",
        "context": "low",
        "topic": {
            "en": "Immigration",
            "ja": "移民",
        },
        "statement": {
            "en": "The government should increase the intake of immigrants from overseas.",
            "ja": "政府は海外からの移民の受け入れを拡大すべきだ。",
        },
    },
    {
        "id": 13,
        "topic_id": "political_donations",
        "context": "low",
        "topic": {
            "en": "Political donations",
            "ja": "政治献金",
        },
        "statement": {
            "en": "Political donations from companies and organizations should be prohibited.",
            "ja": "企業や団体による政治献金を禁止すべきだ。",
        },
    },
    {
        "id": 14,
        "topic_id": "defense_spending",
        "context": "low",
        "topic": {
            "en": "Defense spending",
            "ja": "防衛費",
        },
        "statement": {
            "en": "Defense spending should be increased.",
            "ja": "防衛費を増額すべきだ。",
        },
    },
    {
        "id": 15,
        "topic_id": "environmental_protection",
        "context": "low",
        "topic": {
            "en": "Environmental protection",
            "ja": "環境保護",
        },
        "statement": {
            "en": "Environmental protection should be prioritized over economic growth.",
            "ja": "経済成長よりも環境保護を優先すべきだ。",
        },
    },
]

# =========================================================
# AGENTS
# =========================================================
AGENTS = [
    {
        "id": "Agent_L",
        "persona": {
            "en": "You are a liberal citizen.",
            "ja": "あなたはリベラル派の市民です。",
        },
    },
    {
        "id": "Agent_M",
        "persona": {
            "en": "You are a moderate citizen. You place yourself in the middle of the ideological spectrum rather than identifying as liberal or conservative.",
            "ja": "あなたは中道派の市民です。リベラルか保守かといった軸の中で、自分をその中間に位置づけています。",
        },
    },
    {
        "id": "Agent_R",
        "persona": {
            "en": "You are a conservative citizen.",
            "ja": "あなたは保守派の市民です。",
        },
    },
]

# =========================================================
# PROMPT PARTS (adopted: original x I3)
# =========================================================
SYSTEM_PROMPT = {
    "en": "You are a discussion participant with the following background:\nPersona: {persona}",
    "ja": "あなたは以下の背景を持つ参加者です：\nペルソナ: {persona}",
}

# I3 (beneficial / harmful)
QUESTION = {
    "en": "Is the following statement beneficial or harmful for society in the long run? Rate it on the scale below.\n\n{statement}",
    "ja": "長期的に見て、次の主張は社会にとって有益ですか、それとも有害ですか？以下の尺度で評価してください。\n\n{statement}",
}

SCALE = {
    "en": "Scale:\n"
          "-2 = very harmful\n"
          "-1 = somewhat harmful\n"
          "0 = neutral\n"
          "+1 = somewhat beneficial\n"
          "+2 = very beneficial",
    "ja": "尺度：\n"
          "-2 = 非常に有害\n"
          "-1 = やや有害\n"
          "0 = どちらでもない\n"
          "+1 = やや有益\n"
          "+2 = 非常に有益",
}

OPINION_LEN = {"en": "3-5", "ja": "3〜5"}

OUTPUT_FORMAT = {
    "en": (
        "Always respond in English.\n\n"
        "Use the following output format.\n"
        "Opinion: <{n} sentences explaining your reasoning>\n\n"
        "Stance: <one integer only: -2, -1, 0, 1, or 2>\n"
        "[Important]\n"
        "- Strictly follow the format.\n"
        "- Do not use any Markdown symbols (like **, ##, ---, etc.).\n"
        "- Make sure your sentences are complete and not cut off in the middle.\n"
    ),
    "ja": (
        "必ず日本語で回答してください。\n\n"
        "次の形式で出力してください。\n"
        "意見：<{n}文で理由を述べる>\n\n"
        "スタンス：<-2, -1, 0, 1, 2のいずれか1つの整数>\n"
        "【重要】\n"
        "- フォーマットに厳格に従うこと。\n"
        "- Markdownの記号(**、##、---など)は絶対に使わないこと。\n"
        "- 文章は途中で切れないように、必ず完結させること。\n"
    ),
}


def get_topic(topic_id) -> dict:
    """topic_id (str) または id (int) で検索"""
    for topic in TOPICS:
        if topic["topic_id"] == topic_id or topic["id"] == topic_id:
            return topic
    raise KeyError(f"Unknown topic: {topic_id}")


def build_prompt(agent: dict, topic: dict, language: str) -> dict:
    """
    Returns {"system": ..., "prompt": ...}
    system : persona
    prompt : question(statement) -> scale -> output format
    """
    system = SYSTEM_PROMPT[language].format(persona=agent["persona"][language])

    prompt = (
        QUESTION[language].format(statement=topic["statement"][language])
        + "\n\n" + SCALE[language]
        + "\n\n" + OUTPUT_FORMAT[language].format(n=OPINION_LEN[language])
    )
    return {"system": system, "prompt": prompt}


# =========================================================
# RESPONSE PARSING
# =========================================================
_STANCE_RE = re.compile(
    r"(?:スタンス|stance)\s*[:：]\s*([-+]?\s?[0-2])(?!\d)", re.IGNORECASE
)


def parse_response(text):
    """
    Extract the stance integer in [-2, 2] from a model response.
    Returns None if no valid stance line is found (treat as a parse failure).
    """
    if text is None:
        return None
    t = str(text).replace("−", "-").replace("－", "-").replace("＋", "+")
    t = t.replace("*", "").replace("＊", "")
    t = t.translate(str.maketrans("０１２", "012"))
    m = _STANCE_RE.search(t)
    if not m:
        return None
    try:
        return int(m.group(1).replace(" ", ""))
    except ValueError:
        return None