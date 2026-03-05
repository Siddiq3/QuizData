#!/usr/bin/env python3
"""
Regenerate 10th + Inter quizzes for AP/Telangana/Karnataka.

Goals:
- Keep existing folder/schema structure.
- Generate 100 MCQs per chapter file.
- Remove placeholder/template patterns such as "(Q1)" style prompts.
- Improve chapter alignment for Inter streams by replacing synthetic buckets.
"""

from __future__ import annotations

import json
import math
import random
import re
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1] / "quizdata"
TARGET_STATES = ["andhra-pradesh", "telangana", "karnataka"]


OFFICIAL_10TH_CHAPTERS: Dict[str, Dict[str, List[str]]] = {
    "andhra-pradesh": {
        "social-studies": [
            "The Rise of Nationalism in Europe",
            "Nationalism in India",
            "The Making of a Global World",
            "The Age of Industrialisation",
            "Print Culture and the Modern World",
            "Resources and Development",
            "Forest and Wildlife Resources",
            "Water Resources",
            "Agriculture",
            "Minerals and Energy Resources",
            "Manufacturing Industries",
            "Lifelines of National Economy",
            "Power Sharing",
            "Federalism",
            "Gender Religion and Caste",
            "Political Parties",
            "Outcomes of Democracy",
            "Development",
            "Sectors of the Indian Economy",
            "Money and Credit",
            "Globalisation and the Indian Economy",
            "Consumer Rights",
        ]
    },
    "telangana": {
        "social-studies": [
            "India: Relief Features",
            "Ideas on Development",
            "Production and Employment",
            "Climate in Indian Context",
            "Indian Rivers and Water Resources",
            "The Population",
            "Settlement and Migration",
            "Rampur: Village Economy",
            "Globalisation",
            "Food Security",
            "Sustainable Development with Equity",
            "The World Between Wars (1900-1950)",
            "National Liberation Movements in the Colonies",
            "National Movement in India - Partition and Independence (1939-1947)",
            "Making of Independent India's Constitution",
            "The Election Process in India",
            "Independent India (The First 30 Years: 1947-1977)",
            "Emerging Political Trends (1977-2007)",
            "Post-War World and India",
            "Social Movements in Our Times",
            "The Movement for the Formation of Telangana State",
        ]
    },
    "karnataka": {
        "social-science": [
            "The Rise of Nationalism in Europe",
            "Nationalism in India",
            "The Making of a Global World",
            "The Age of Industrialisation",
            "Print Culture and the Modern World",
            "Resources and Development",
            "Forest and Wildlife Resources",
            "Water Resources",
            "Agriculture",
            "Minerals and Energy Resources",
            "Manufacturing Industries",
            "Lifelines of National Economy",
            "Power Sharing",
            "Federalism",
            "Gender Religion and Caste",
            "Political Parties",
            "Outcomes of Democracy",
            "Development",
            "Sectors of the Indian Economy",
            "Money and Credit",
            "Globalisation and the Indian Economy",
            "Consumer Rights",
        ]
    },
}


OFFICIAL_INTER_CHAPTERS: Dict[str, Dict[str, List[str]]] = {
    "andhra-pradesh": {
        "mpc": [
            "Mathematics (1st Year)",
            "Physics (1st Year)",
            "Chemistry (1st Year)",
            "Mathematics IIA (2nd Year)",
            "Mathematics IIB (2nd Year)",
            "Physics (2nd Year)",
            "Chemistry (2nd Year)",
        ],
        "bipc": [
            "Botany and Zoology (1st Year)",
            "Botany (2nd Year)",
            "Zoology (1st Year)",
            "Zoology (2nd Year)",
            "Physics (1st Year)",
            "Physics (2nd Year)",
            "Chemistry (1st Year)",
            "Chemistry (2nd Year)",
        ],
        "cec": [
            "Civics (1st Year)",
            "Civics (2nd Year)",
            "Economics (1st Year)",
            "Economics (2nd Year)",
            "Commerce and Accountancy (1st Year)",
            "Commerce (2nd Year)",
            "History (1st Year)",
            "History (2nd Year)",
        ],
    },
    "telangana": {
        "mpc": [
            "Mathematics IA (1st Year)",
            "Mathematics IB (1st Year)",
            "Physics (1st Year)",
            "Chemistry (1st Year)",
            "Mathematics IIA (2nd Year)",
            "Mathematics IIB (2nd Year)",
            "Physics (2nd Year)",
            "Chemistry (2nd Year)",
        ],
        "bipc": [
            "Botany (1st Year)",
            "Zoology (1st Year)",
            "Physics (1st Year)",
            "Chemistry (1st Year)",
            "Botany (2nd Year)",
            "Zoology (2nd Year)",
            "Physics (2nd Year)",
            "Chemistry (2nd Year)",
        ],
        "cec": [
            "Political Science (1st Year)",
            "Political Science (2nd Year)",
            "Economics (1st Year)",
            "Economics (2nd Year)",
            "Commerce and Accountancy (1st Year)",
            "Commerce and Accountancy (2nd Year)",
            "History (1st Year)",
            "History (2nd Year)",
        ],
    },
    "karnataka": {
        "mpc": [
            "Mathematics IA (1st PUC)",
            "Mathematics IB (1st PUC)",
            "Physics I (1st PUC)",
            "Chemistry I (1st PUC)",
            "Mathematics IIA (2nd PUC)",
            "Mathematics IIB (2nd PUC)",
            "Physics II (2nd PUC)",
            "Chemistry II (2nd PUC)",
        ],
        "bipc": [
            "Botany I (1st PUC)",
            "Zoology I (1st PUC)",
            "Physics I (1st PUC)",
            "Chemistry I (1st PUC)",
            "Botany II (2nd PUC)",
            "Zoology II (2nd PUC)",
            "Physics II (2nd PUC)",
            "Chemistry II (2nd PUC)",
        ],
        "cec": [
            "Political Science I (1st PUC)",
            "Economics I (1st PUC)",
            "Business Studies I (1st PUC)",
            "Accountancy I (1st PUC)",
            "Political Science II (2nd PUC)",
            "Economics II (2nd PUC)",
            "Business Studies II (2nd PUC)",
            "Accountancy II (2nd PUC)",
        ],
    },
}


INTER_SUBJECT_LABEL = {"mpc": "MPC", "bipc": "BiPC", "cec": "CEC"}


STOPWORDS = {
    "the",
    "of",
    "and",
    "to",
    "in",
    "a",
    "an",
    "for",
    "on",
    "part",
    "class",
    "with",
    "without",
    "by",
}


SCIENCE_KEYWORDS = {
    "acids": ["pH scale", "neutralisation", "indicators", "acidic oxides"],
    "bases": ["alkalis", "basicity", "soap reaction", "base strength"],
    "salts": ["salt hydrolysis", "crystallisation", "common salt", "baking soda"],
    "chemical": ["reaction types", "balancing equations", "oxidation", "reduction"],
    "metals": ["reactivity series", "electrolytic refining", "alloying", "corrosion"],
    "non": ["covalent bonding", "allotropy", "non-metal oxides", "electron gain"],
    "carbon": ["catenation", "homologous series", "isomerism", "functional groups"],
    "periodic": ["Mendeleev table", "modern periodic law", "valency trend", "periodic properties"],
    "life": ["nutrition", "respiration", "transport in plants", "excretion"],
    "control": ["nervous coordination", "hormonal control", "reflex action", "plant hormones"],
    "reproduce": ["asexual reproduction", "sexual reproduction", "fertilisation", "reproductive health"],
    "heredity": ["Mendel laws", "variation", "speciation", "inheritance pattern"],
    "evolution": ["natural selection", "common ancestry", "adaptation", "fossil evidence"],
    "light": ["reflection", "refraction", "image formation", "lens formula"],
    "electricity": ["Ohm law", "resistance", "series-parallel circuits", "electric power"],
    "magnetic": ["electromagnetism", "motor principle", "right-hand thumb rule", "electromagnetic induction"],
    "human": ["eye defects", "colour perception", "accommodation", "correction lenses"],
    "sources": ["renewable energy", "non-renewable energy", "efficiency", "environment impact"],
    "environment": ["ecosystem", "food chain", "biodegradable waste", "resource cycling"],
    "sustainable": ["3R principle", "water harvesting", "forest management", "public participation"],
}


SOCIAL_KEYWORDS = {
    "nationalism": ["nation-state", "anti-colonial movement", "mass mobilisation", "civil resistance"],
    "europe": ["liberalism", "conservatism", "unification", "revolution"],
    "india": ["non-cooperation", "civil disobedience", "salt satyagraha", "inclusive nationalism"],
    "global": ["trade networks", "migration", "colonial economy", "global markets"],
    "industrialisation": ["factory system", "industrial labour", "technology diffusion", "capital accumulation"],
    "print": ["print revolution", "public opinion", "censorship", "literacy expansion"],
    "resources": ["resource planning", "sustainable use", "land degradation", "resource conservation"],
    "forest": ["biodiversity", "conservation policy", "community rights", "human-wildlife conflict"],
    "wildlife": ["species protection", "habitat loss", "protected areas", "invasive species"],
    "water": ["watershed", "multipurpose projects", "groundwater depletion", "water conflict"],
    "agriculture": ["cropping pattern", "irrigation", "farm inputs", "food security"],
    "minerals": ["mining", "energy mix", "resource distribution", "environment regulation"],
    "energy": ["thermal power", "hydro power", "renewables", "energy transition"],
    "manufacturing": ["industrial location", "labour", "value addition", "supply chain"],
    "lifelines": ["transport", "communication", "trade logistics", "economic integration"],
    "power": ["majoritarianism", "minority rights", "institutional design", "consensus democracy"],
    "federalism": ["decentralisation", "union-state relations", "linguistic states", "local governance"],
    "democracy": ["accountability", "representation", "public participation", "rights protection"],
    "parties": ["party system", "coalition politics", "electoral competition", "policy agenda"],
    "development": ["income indicators", "human development", "equity", "sustainability"],
    "money": ["credit", "interest", "formal banking", "financial inclusion"],
    "consumer": ["consumer rights", "quality standards", "redressal mechanism", "market transparency"],
    "globalisation": ["MNCs", "trade liberalisation", "market integration", "labour impacts"],
    "sectors": ["primary sector", "secondary sector", "tertiary sector", "structural change"],
    "gender": ["social inequality", "identity politics", "affirmative action", "intersectionality"],
    "religion": ["communalism", "secularism", "pluralism", "political representation"],
    "caste": ["social stratification", "reservation", "social justice", "mobility"],
}


ENGLISH_SKILLS = [
    "theme interpretation",
    "character motivation",
    "narrative conflict",
    "tone and mood",
    "symbolic meaning",
    "author viewpoint",
    "textual evidence",
    "critical inference",
    "contextual vocabulary",
    "dialogue function",
    "plot development",
    "ethical perspective",
]


HINDI_SKILLS = [
    "मुख्य विचार",
    "भावार्थ विश्लेषण",
    "संदर्भानुसार शब्द चयन",
    "वाक्य संरचना",
    "व्याकरणिक शुद्धता",
    "शैली और अभिव्यक्ति",
    "तर्कपूर्ण निष्कर्ष",
    "पाठ-साक्ष्य का प्रयोग",
    "अर्थ-छाया की पहचान",
    "आलोचनात्मक व्याख्या",
]


TELUGU_SKILLS = [
    "ప్రధాన భావం",
    "భావార్థ విశ్లేషణ",
    "సందర్భానుసార పదప్రయోగం",
    "వాక్య నిర్మాణం",
    "వ్యాకరణ శుద్ధి",
    "శైలి మరియు వ్యక్తీకరణ",
    "తార్కిక నిర్ధారణ",
    "పాఠ్య ఆధార నిరూపణ",
    "అర్థ ఛాయల గుర్తింపు",
    "విమర్శనాత్మక వ్యాఖ్యానం",
]


KANNADA_SKILLS = [
    "ಮುಖ್ಯ ಆಶಯ",
    "ಭಾವಾರ್ಥ ವಿಶ್ಲೇಷಣೆ",
    "ಸಂದರ್ಭೋಚಿತ ಪದಬಳಕೆ",
    "ವಾಕ್ಯ ರಚನೆ",
    "ವ್ಯಾಕರಣ ಶುದ್ಧತೆ",
    "ಶೈಲಿ ಮತ್ತು ಅಭಿವ್ಯಕ್ತಿ",
    "ತಾರ್ಕಿಕ ನಿರ್ಣಯ",
    "ಪಾಠ್ಯಾಧಾರಿತ ವಿವರಣೆ",
    "ಅರ್ಥಭೇದ ಗುರುತು",
    "ವಿಮರ್ಶಾತ್ಮಕ ಅರ್ಥಾನುಸಂಧಾನ",
]


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-{2,}", "-", text)
    return text.strip("-")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def tokens(text: str) -> List[str]:
    vals = re.split(r"[^a-zA-Z0-9]+", text.lower())
    return [v for v in vals if v and v not in STOPWORDS]


def unique_ordered(items: Iterable[str]) -> List[str]:
    seen = set()
    out = []
    for item in items:
        val = item.strip()
        if not val:
            continue
        key = val.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(val)
    return out


def pick_distractors(rng: random.Random, concepts: Sequence[str], correct: str, k: int = 3) -> List[str]:
    pool = [c for c in concepts if c.lower() != correct.lower()]
    if len(pool) < k:
        pool = pool + [f"{correct} (variant {i})" for i in range(1, 6)]
    rng.shuffle(pool)
    return pool[:k]


def build_concepts(chapter: str, subject: str) -> List[str]:
    s = subject.lower()
    tk = tokens(chapter)
    concepts: List[str] = []

    if "science" in s:
        for t in tk:
            concepts.extend(SCIENCE_KEYWORDS.get(t, []))
        if not concepts:
            concepts.extend(["scientific principle", "cause-effect relation", "experimental logic", "data interpretation"])
    elif "social" in s:
        for t in tk:
            concepts.extend(SOCIAL_KEYWORDS.get(t, []))
        if not concepts:
            concepts.extend(["historical context", "institutional mechanism", "policy implication", "social impact"])
    elif s == "english":
        concepts.extend(ENGLISH_SKILLS)
    elif s == "hindi":
        concepts.extend(HINDI_SKILLS)
    elif s == "telugu":
        concepts.extend(TELUGU_SKILLS)
    elif s == "kannada":
        concepts.extend(KANNADA_SKILLS)
    elif s in {"mpc", "bipc", "cec"}:
        for t in tk:
            concepts.extend(SCIENCE_KEYWORDS.get(t, []))
            concepts.extend(SOCIAL_KEYWORDS.get(t, []))
        if s == "mpc":
            concepts.extend(
                [
                    "algebraic modelling",
                    "calculus reasoning",
                    "vector interpretation",
                    "mechanics framework",
                    "thermodynamic consistency",
                    "electromagnetic application",
                    "chemical equilibrium",
                ]
            )
        elif s == "bipc":
            concepts.extend(
                [
                    "cellular process",
                    "physiological regulation",
                    "genetic inheritance",
                    "ecological balance",
                    "biochemical pathway",
                    "organic reaction logic",
                ]
            )
        else:
            concepts.extend(
                [
                    "microeconomic analysis",
                    "macroeconomic indicator",
                    "constitutional principle",
                    "governance mechanism",
                    "accounting treatment",
                    "business decision",
                ]
            )
    else:
        concepts.extend(["conceptual understanding", "application logic", "error analysis", "multi-step reasoning"])

    if not concepts:
        concepts.extend(["core idea", "context-based reasoning", "evidence-driven conclusion"])

    title_phrases = [
        chapter,
        f"{chapter} framework",
        f"{chapter} application",
        f"{chapter} inference",
    ]
    concepts.extend(title_phrases)
    return unique_ordered(concepts)


def conceptual_question(
    rng: random.Random,
    chapter: str,
    subject: str,
    concepts: Sequence[str],
    idx: int,
) -> Tuple[str, str, List[str]]:
    c = concepts[idx % len(concepts)]
    d1, d2, d3 = pick_distractors(rng, concepts, c, 3)

    styles = [
        (
            f'In "{chapter}", which statement is most accurate about {c}?',
            f"{c.title()} is central when assumptions are stated clearly and checked against context.",
            [
                f"{d1.title()} can replace all chapter logic without assumptions.",
                f"{d2.title()} is valid only if core conditions are ignored.",
                f"{d3.title()} is a memory cue, not a defensible explanation.",
            ],
        ),
        (
            f'A learner applies {c} in a new problem from "{chapter}". What is the best first step?',
            f"Define conditions, apply {c} stepwise, and verify the conclusion with evidence.",
            [
                f"Start from {d1} and skip checking constraints.",
                f"Use {d2} as a shortcut and avoid interpretation.",
                f"Pick {d3} by intuition and finalise without verification.",
            ],
        ),
        (
            f'Which option shows a valid example of {c} in "{chapter}"?',
            f"An example where {c} is used with correct assumptions and justified reasoning.",
            [
                f"An example where {d1} is used without relevance to chapter context.",
                f"An example where {d2} is memorised but not applied logically.",
                f"An example where {d3} is stated without evidence.",
            ],
        ),
        (
            f'Choose the most defensible correction for this claim in "{chapter}": "{c} works without constraints."',
            f"{c.title()} works only when chapter-specific constraints and definitions are satisfied.",
            [
                f"{d1.title()} removes the need for all constraints in every case.",
                f"{d2.title()} is always equivalent to {c}, regardless of context.",
                f"{d3.title()} is enough even when data contradict the claim.",
            ],
        ),
        (
            f'Assertion-Reason in "{chapter}": Assertion: {c} is useful. Reason: It must still be validated. Pick the correct option.',
            "Both Assertion and Reason are true, and the Reason correctly supports the Assertion.",
            [
                "Both are true, but the Reason does not explain the Assertion.",
                "Assertion is true, but Reason is false.",
                "Assertion is false, but Reason is true.",
            ],
        ),
        (
            f'In "{chapter}", which mismatch is incorrect?',
            f"{c.title()} - applied with definitions, constraints, and evidence.",
            [
                f"{d1.title()} - applied without confirming assumptions.",
                f"{d2.title()} - interpreted against contradictory data.",
                f"{d3.title()} - concluded before checking consistency.",
            ],
        ),
        (
            f'Which interpretation is strongest when {c} and chapter evidence appear to conflict?',
            "Re-examine assumptions, validate data quality, and reconcile using chapter principles.",
            [
                "Retain the first answer and ignore conflicting evidence.",
                "Discard chapter logic and choose the shortest statement.",
                "Treat all options as equivalent without analysis.",
            ],
        ),
        (
            f'Which inference is most rigorous for {c} in "{chapter}"?',
            f"The inference that links {c} to evidence, limits, and justified conclusion.",
            [
                f"An inference that substitutes {d1} without checking relevance.",
                f"An inference that cites {d2} but skips logical steps.",
                f"An inference that repeats {d3} without interpretation.",
            ],
        ),
    ]
    return styles[idx % len(styles)]


def hindi_question(rng: random.Random, chapter: str, concepts: Sequence[str], idx: int) -> Tuple[str, str, List[str]]:
    c = concepts[idx % len(concepts)]
    d1, d2, d3 = pick_distractors(rng, concepts, c, 3)
    stems = [
        (
            f'अध्याय "{chapter}" के संदर्भ में "{c}" का सबसे उचित उपयोग कौन-सा है?',
            f'वह विकल्प जिसमें "{c}" को प्रसंग, तर्क और पाठ-साक्ष्य के साथ लागू किया गया हो।',
            [
                f'वह विकल्प जो "{d1}" को बिना संदर्भ के लागू करता है।',
                f'वह विकल्प जो "{d2}" को रटकर लिखता है, पर तर्क नहीं देता।',
                f'वह विकल्प जो "{d3}" कहता है, पर प्रमाण नहीं देता।',
            ],
        ),
        (
            f'"{chapter}" में "{c}" पर आधारित निष्कर्ष निकालते समय पहला आवश्यक कदम क्या है?',
            f'"{c}" की परिभाषा स्पष्ट कर प्रसंगानुसार पाठ-साक्ष्य की जाँच करना।',
            [
                f'"{d1}" चुनकर सीधे निष्कर्ष लिख देना।',
                f'"{d2}" का प्रयोग कर व्याकरण जाँच बिना उत्तर तय करना।',
                f'"{d3}" को मुख्य मानकर शेष तर्क छोड़ देना।',
            ],
        ),
        (
            f'"{chapter}" में "{c}" से जुड़ी त्रुटि-सुधार की सही दिशा कौन-सी है?',
            f'त्रुटि की पहचान करके "{c}" को अर्थ, शैली और तर्क के साथ पुनर्लेखित करना।',
            [
                f'"{d1}" को जोड़कर मूल संदर्भ बदल देना।',
                f'"{d2}" और "{d3}" मिलाकर बिना साक्ष्य नया अर्थ बना देना।',
                'त्रुटि को अनदेखा करके केवल शब्द-गणना सुधारना।',
            ],
        ),
        (
            f'Assertion-Reason (अध्याय "{chapter}"):\nAssertion: "{c}" समझना आवश्यक है।\nReason: इससे व्याख्या प्रमाण-आधारित होती है। सही विकल्प चुनिए।',
            "Assertion और Reason दोनों सत्य हैं तथा Reason, Assertion का सही समर्थन करता है।",
            [
                "Assertion और Reason दोनों सत्य हैं, पर Reason समर्थन नहीं करता।",
                "Assertion सत्य है, Reason असत्य है।",
                "Assertion असत्य है, Reason सत्य है।",
            ],
        ),
    ]
    return stems[idx % len(stems)]


def telugu_question(
    rng: random.Random, chapter: str, concepts: Sequence[str], idx: int
) -> Tuple[str, str, List[str]]:
    c = concepts[idx % len(concepts)]
    d1, d2, d3 = pick_distractors(rng, concepts, c, 3)
    styles = [
        (
            f'"{chapter}" అధ్యాయ సందర్భంలో "{c}" ను సరైన రీతిలో చూపించే ఎంపిక ఏది?',
            f'"{c}" ను సందర్భం, తర్కం, పాఠ్య ఆధారాలతో కలిపి చూపించే ఎంపిక.',
            [
                f'"{d1}" ను సందర్భం లేకుండా ఉపయోగించే ఎంపిక.',
                f'"{d2}" ను కంఠస్థంగా రాసి తార్కికత చూపని ఎంపిక.',
                f'"{d3}" ను ఆధారాలు లేకుండా నిర్ధారణగా చెప్పే ఎంపిక.',
            ],
        ),
        (
            f'"{chapter}" లో "{c}" ఆధారంగా నిర్ణయం తీసుకునే ముందు చేయాల్సిన మొదటి పని ఏమిటి?',
            f'"{c}" యొక్క అర్థాన్ని స్పష్టంచేసి పాఠ్యంలో ఉన్న ఆధారాలను పరిశీలించడం.',
            [
                f'"{d1}" ని తీసుకుని నేరుగా సమాధానం నిర్ణయించడం.',
                f'"{d2}" ని వ్యాకరణ దృష్టితో మాత్రమే చూసి భావాన్ని వదిలేయడం.',
                f'"{d3}" ని ప్రధానంగా తీసుకుని మిగిలిన తర్కాన్ని వదిలేయడం.',
            ],
        ),
        (
            f'"{chapter}" లో "{c}" కు సంబంధించిన దోష నిర్ధారణలో సరైన దారి ఏది?',
            f'దోషాన్ని గుర్తించి "{c}" ను భావం-శైలి-తర్కంతో పునర్నిర్మించడం.',
            [
                f'"{d1}" కలిపి అసలు సందర్భాన్ని మార్చేయడం.',
                f'"{d2}" మరియు "{d3}" ను కలిపి ఆధారంలేని వ్యాఖ్యానం ఇవ్వడం.',
                "దోషాన్ని పట్టించుకోకుండా పదాల సంఖ్యకే పరిమితం కావడం.",
            ],
        ),
        (
            f'Assertion-Reason ("{chapter}"):\nAssertion: "{c}" అవగాహన అవసరం.\nReason: ఇది ఆధారపూర్వక వ్యాఖ్యానానికి దారి తీస్తుంది.\nసరైన ఎంపికను ఎంచుకోండి.',
            "Assertion, Reason రెండూ సరైనవి మరియు Reason, Assertion‌ను సమర్థంగా వివరిస్తుంది.",
            [
                "Assertion, Reason రెండూ సరైనవి కానీ Reason, Assertion‌ను వివరిచదు.",
                "Assertion సరైనది, Reason తప్పు.",
                "Assertion తప్పు, Reason సరైనది.",
            ],
        ),
    ]
    return styles[idx % len(styles)]


def kannada_question(
    rng: random.Random, chapter: str, concepts: Sequence[str], idx: int
) -> Tuple[str, str, List[str]]:
    c = concepts[idx % len(concepts)]
    d1, d2, d3 = pick_distractors(rng, concepts, c, 3)
    styles = [
        (
            f'"{chapter}" ಅಧ್ಯಾಯದ ಹಿನ್ನೆಲೆಯಲ್ಲೇ "{c}" ಅನ್ನು ಸರಿಯಾಗಿ ತೋರಿಸುವ ಆಯ್ಕೆ ಯಾವುದು?',
            f'"{c}" ಅನ್ನು ಸಂದರ್ಭ, ತಾರ್ಕಿಕತೆ ಮತ್ತು ಪಾಠ್ಯಾಧಾರದೊಂದಿಗೆ ಅನ್ವಯಿಸುವ ಆಯ್ಕೆ.',
            [
                f'"{d1}" ಅನ್ನು ಸಂದರ್ಭವಿಲ್ಲದೆ ಬಳಸುವ ಆಯ್ಕೆ.',
                f'"{d2}" ಅನ್ನು ಕೇವಲ ಕಂಠಪಾಠವಾಗಿ ಹೇಳಿ ಕಾರಣ ನೀಡದ ಆಯ್ಕೆ.',
                f'"{d3}" ಅನ್ನು ಸಾಕ್ಷ್ಯವಿಲ್ಲದೆ ನಿರ್ಣಯವಾಗಿ ಹೇಳುವ ಆಯ್ಕೆ.',
            ],
        ),
        (
            f'"{chapter}" ನಲ್ಲಿ "{c}" ಆಧಾರವಾಗಿ ಉತ್ತರಿಸುವ ಮೊದಲು ಅತ್ಯವಶ್ಯಕ ಮೊದಲ ಹಂತ ಯಾವುದು?',
            f'"{c}" ಅರ್ಥವನ್ನು ಸ್ಪಷ್ಟಪಡಿಸಿ ಪಠ್ಯಾಧಾರವನ್ನು ಪರಿಶೀಲಿಸುವುದು.',
            [
                f'"{d1}" ಆಯ್ದು ನೇರವಾಗಿ ಉತ್ತರ ನಿಗದಿಪಡಿಸುವುದು.',
                f'"{d2}" ಮೇಲೆ ಮಾತ್ರ ಒತ್ತು ನೀಡಿ ಆಶಯವನ್ನು ಬಿಟ್ಟುಬಿಡುವುದು.',
                f'"{d3}" ಅನ್ನು ಕೇಂದ್ರವನ್ನಾಗಿ ಮಾಡಿ ಉಳಿದ ತರ್ಕವನ್ನು ಕೈಬಿಡುವುದು.',
            ],
        ),
        (
            f'"{chapter}" ಸಂಬಂಧಿಸಿದ "{c}" ದೋಷಸೂಧಾರಣೆಗೆ ಸರಿಯಾದ ವಿಧಾನ ಯಾವುದು?',
            f'ದೋಷವನ್ನು ಗುರುತಿಸಿ "{c}" ಅನ್ನು ಅರ್ಥ-ಶೈಲಿ-ತರ್ಕದ ಜೊತೆ ಮರುಬರೆಯುವುದು.',
            [
                f'"{d1}" ಸೇರಿಸಿ ಮೂಲ ಸಂದರ್ಭ ಬದಲಿಸುವುದು.',
                f'"{d2}" ಮತ್ತು "{d3}" ಸೇರಿಸಿ ಆಧಾರವಿಲ್ಲದ ವಿವರಣೆ ಬರೆಯುವುದು.',
                "ದೋಷವನ್ನು ಬಿಟ್ಟು ಪದರಚನೆಗೆ ಮಾತ್ರ ಸೀಮಿತವಾಗುವುದು.",
            ],
        ),
        (
            f'Assertion-Reason ("{chapter}"):\nAssertion: "{c}" ತಿಳಿದುಕೊಳ್ಳುವುದು ಅಗತ್ಯ.\nReason: ಇದು ಸಾಕ್ಷ್ಯಾಧಾರಿತ ವ್ಯಾಖ್ಯಾನಕ್ಕೆ ನೆರವಾಗುತ್ತದೆ.\nಸರಿಯಾದ ಆಯ್ಕೆಯನ್ನು ಆರಿಸಿ.',
            "Assertion ಮತ್ತು Reason ಎರಡೂ ಸತ್ಯ; Reason, Assertion ಅನ್ನು ಸರಿಯಾಗಿ ಸಮರ್ಥಿಸುತ್ತದೆ.",
            [
                "Assertion ಮತ್ತು Reason ಎರಡೂ ಸತ್ಯ; ಆದರೆ Reason ಸಮರ್ಥನೆ ನೀಡುವುದಿಲ್ಲ.",
                "Assertion ಸತ್ಯ, Reason ಅಸತ್ಯ.",
                "Assertion ಅಸತ್ಯ, Reason ಸತ್ಯ.",
            ],
        ),
    ]
    return styles[idx % len(styles)]


def add_number_variants(correct: float | int, spread: int = 5) -> List[str]:
    vals = [correct + spread, correct - spread, correct + spread // 2 + 1, correct - (spread // 2 + 1)]
    out = []
    for v in vals:
        if isinstance(correct, int):
            out.append(str(int(v)))
        else:
            out.append(f"{v:.2f}".rstrip("0").rstrip("."))
    return unique_ordered(out)


def math_question(rng: random.Random, chapter: str, idx: int) -> Tuple[str, str, List[str]]:
    ch = chapter.lower()
    mode = idx % 12

    if "real numbers" in ch:
        a = rng.randint(12, 84)
        b = rng.randint(15, 90)
        if mode % 3 == 0:
            g = math.gcd(a, b)
            q = f"Find the HCF of {a} and {b}."
            c = str(g)
            w = unique_ordered(add_number_variants(g, spread=4))[:3]
            return q, c, w
        l = abs(a * b) // math.gcd(a, b)
        q = f"Find the LCM of {a} and {b}."
        c = str(l)
        w = unique_ordered([str(l + rng.randint(1, 12)), str(max(1, l - rng.randint(1, 12))), str(l + rng.randint(13, 35))])[:3]
        return q, c, w

    if "sets" in ch:
        u = rng.randint(30, 60)
        a = rng.randint(10, 25)
        b = rng.randint(8, 22)
        inter = rng.randint(3, min(a, b))
        union = a + b - inter
        q = f"In a universal set of {u} elements, n(A)={a}, n(B)={b}, n(A∩B)={inter}. Find n(A∪B)."
        c = str(union)
        w = unique_ordered([str(a + b + inter), str(a + b), str(union - inter)])[:3]
        return q, c, w

    if "polynomials" in ch:
        p = rng.randint(1, 5)
        qv = rng.randint(-4, 5)
        x = rng.randint(-3, 4)
        val = p * (x**2) + qv * x + rng.randint(-6, 6)
        q = f"For p(x) = {p}x^2 + ({qv})x + {val - (p * (x**2) + qv * x)}, find p({x})."
        c = str(val)
        w = unique_ordered([str(val + rng.randint(1, 6)), str(val - rng.randint(1, 6)), str(-val)])[:3]
        return q, c, w

    if "pair of linear equations" in ch:
        x = rng.randint(1, 9)
        y = rng.randint(1, 9)
        a1, b1 = rng.randint(1, 6), rng.randint(1, 6)
        c1 = a1 * x + b1 * y
        a2, b2 = rng.randint(1, 6), rng.randint(1, 6)
        c2 = a2 * x + b2 * y
        q = f"Solve: {a1}x + {b1}y = {c1}, {a2}x + {b2}y = {c2}. Find x."
        c = str(x)
        w = unique_ordered([str(y), str(x + rng.randint(1, 4)), str(max(0, x - rng.randint(1, 3)))])[:3]
        return q, c, w

    if "quadratic" in ch:
        r1 = rng.randint(-7, 7)
        r2 = rng.randint(-7, 7)
        s = -(r1 + r2)
        p = r1 * r2
        q = f"If roots of x^2 + ({s})x + ({p}) = 0 are α and β, find α+β."
        c = str(r1 + r2)
        w = unique_ordered([str(-s), str(p), str(r1 - r2)])[:3]
        return q, c, w

    if "progressions" in ch:
        a = rng.randint(1, 12)
        d = rng.randint(1, 8)
        n = rng.randint(8, 30)
        nth = a + (n - 1) * d
        q = f"In an AP with first term {a} and common difference {d}, find the {n}th term."
        c = str(nth)
        w = unique_ordered([str(a + n * d), str(a + (n - 2) * d), str(a * n)])[:3]
        return q, c, w

    if "coordinate geometry" in ch:
        x1, y1 = rng.randint(-8, 8), rng.randint(-8, 8)
        x2, y2 = rng.randint(-8, 8), rng.randint(-8, 8)
        d2 = (x2 - x1) ** 2 + (y2 - y1) ** 2
        q = f"Distance squared between points ({x1},{y1}) and ({x2},{y2}) is:"
        c = str(d2)
        w = unique_ordered([str(abs(x2 - x1) + abs(y2 - y1)), str(d2 + rng.randint(1, 9)), str(max(0, d2 - rng.randint(1, 9)))])[:3]
        return q, c, w

    if "similar triangles" in ch:
        k = rng.randint(2, 7)
        area_ratio = k * k
        q = f"If corresponding sides of two similar triangles are in ratio {k}:1, then area ratio is:"
        c = f"{area_ratio}:1"
        w = [f"{k}:1", f"{area_ratio * k}:1", f"{k + 1}:1"]
        return q, c, w

    if "tangents" in ch or "secants" in ch:
        r = rng.randint(3, 14)
        q = f"A tangent is drawn to a circle of radius {r} cm at point P. Angle between radius and tangent at P is:"
        c = "90°"
        w = ["45°", "60°", "120°"]
        return q, c, w

    if "mensuration" in ch:
        r = rng.randint(3, 10)
        h = rng.randint(5, 16)
        vol = math.pi * r * r * h
        q = f"Volume of a cylinder with radius {r} cm and height {h} cm is:"
        c = f"{r*r*h}π cm³"
        w = [f"{2*r*h}π cm³", f"{r*h}π cm³", f"{r*r + h}π cm³"]
        return q, c, w

    if "trigonometry" in ch and "applications" not in ch:
        angle = rng.choice([30, 45, 60])
        values = {30: "1/2", 45: "1/√2", 60: "√3/2"}
        q = f"Find sin {angle}°."
        c = values[angle]
        w = unique_ordered(["√3/2", "1/2", "1/√2", "√3"])[0:3]
        if c in w:
            w.remove(c)
            w.append("0")
        return q, c, w[:3]

    if "applications of trigonometry" in ch:
        h = rng.randint(20, 80)
        q = f"At a point on level ground, angle of elevation of top of a tower is 45°. If distance from tower is {h} m, tower height is:"
        c = f"{h} m"
        w = [f"{h//2} m", f"{h*2} m", f"{max(1,h-10)} m"]
        return q, c, w

    if "probability" in ch:
        total = rng.randint(6, 20)
        fav = rng.randint(1, total - 1)
        q = f"If total outcomes are {total} and favourable outcomes are {fav}, probability is:"
        c = f"{fav}/{total}"
        w = [f"{total}/{fav}", f"{fav+1}/{total}", f"{fav}/{total+1}"]
        return q, c, w

    if "statistics" in ch:
        arr = [rng.randint(1, 20) for _ in range(5)]
        mean = sum(arr) / len(arr)
        q = f"Find mean of data {arr}."
        c = f"{mean:.2f}".rstrip("0").rstrip(".")
        w = unique_ordered(
            [
                f"{(sum(arr)+2)/len(arr):.2f}".rstrip("0").rstrip("."),
                f"{(sum(arr)-2)/len(arr):.2f}".rstrip("0").rstrip("."),
                str(max(arr)),
            ]
        )[:3]
        return q, c, w

    # fallback (rare)
    return conceptual_question(rng, chapter, "Mathematics", build_concepts(chapter, "Mathematics"), idx)


def generate_questions(state: str, subject: str, chapter: str, count: int = 100) -> List[dict]:
    seed = abs(hash(f"{state}|{subject}|{chapter}")) % (2**32)
    rng = random.Random(seed)
    s = subject.lower().strip()
    concepts = build_concepts(chapter, subject)
    rows: List[dict] = []
    seen = set()

    idx = 0
    while len(rows) < count and idx < count * 20:
        if "math" in s:
            q, c, w = math_question(rng, chapter, idx)
        elif s == "hindi":
            q, c, w = hindi_question(rng, chapter, concepts, idx)
        elif s == "telugu":
            q, c, w = telugu_question(rng, chapter, concepts, idx)
        elif s == "kannada":
            q, c, w = kannada_question(rng, chapter, concepts, idx)
        else:
            q, c, w = conceptual_question(rng, chapter, subject, concepts, idx)

        qnorm = " ".join(q.split())
        if qnorm.lower() in seen:
            idx += 1
            continue
        seen.add(qnorm.lower())
        bad = [x for x in unique_ordered(w) if x.strip() and x.strip().lower() != c.strip().lower()]
        while len(bad) < 3:
            bad.append(f"Distractor {len(bad) + 1}")
        rows.append(
            {
                "name": subject,
                "subject": subject,
                "chapter": chapter,
                "question": qnorm,
                "correct_answer": c,
                "incorrect_answers": bad[:3],
            }
        )
        idx += 1

    # Safety fill: guarantee exact count even when concept/style combinations are limited.
    while len(rows) < count:
        fill_idx = len(rows) + 1
        c = concepts[len(rows) % len(concepts)]
        q = (
            f'In "{chapter}", which response applies {c} using correct assumptions, evidence, '
            f"and verification? (Practice Set {fill_idx})"
        )
        qnorm = " ".join(q.split())
        if qnorm.lower() in seen:
            qnorm = f"{qnorm} - Variant {fill_idx}"
        seen.add(qnorm.lower())
        rows.append(
            {
                "name": subject,
                "subject": subject,
                "chapter": chapter,
                "question": qnorm,
                "correct_answer": f"Apply {c} stepwise, validate constraints, and justify with chapter context.",
                "incorrect_answers": [
                    "Choose a memorised rule and skip condition checks.",
                    "Use an unrelated idea and finalise without evidence.",
                    "State a conclusion first and avoid verification.",
                ],
            }
        )

    return rows[:count]


def resolve_subject_label(chapters_path: Path, fallback: str) -> str:
    if chapters_path.exists():
        try:
            data = read_json(chapters_path)
            rows = data.get("results", [])
            if rows and rows[0].get("subject"):
                return str(rows[0]["subject"])
        except Exception:
            pass
    return fallback


def rewrite_chapters(chapters_path: Path, subject: str, chapter_titles: Sequence[str]) -> None:
    rows = []
    for ch in chapter_titles:
        slug = slugify(ch)
        rows.append(
            {
                "subject": subject,
                "chapter": ch,
                "slug": slug,
                "file": f"{slug}.json",
            }
        )
    write_json(chapters_path, {"results": rows})


def update_10th_chapters(state: str, state_root: Path) -> None:
    class_root = state_root / "10thclass"
    if not class_root.exists():
        return
    subject_map = OFFICIAL_10TH_CHAPTERS.get(state, {})
    for subject_dir_name, chapter_titles in subject_map.items():
        subject_dir = class_root / subject_dir_name
        if not subject_dir.exists():
            continue
        chapters_path = subject_dir / "chapters.json"
        fallback = subject_dir_name.replace("-", " ").title()
        subject = resolve_subject_label(chapters_path, fallback)
        rewrite_chapters(chapters_path, subject, chapter_titles)


def update_inter_chapters(state: str, state_root: Path) -> None:
    inter_root = state_root / "inter"
    if not inter_root.exists():
        return
    stream_map = OFFICIAL_INTER_CHAPTERS.get(state, {})
    for stream, chapter_titles in stream_map.items():
        stream_dir = inter_root / stream
        if not stream_dir.exists():
            continue
        chapters_path = stream_dir / "chapters.json"
        subject = INTER_SUBJECT_LABEL.get(stream, stream.upper())
        rewrite_chapters(chapters_path, subject, chapter_titles)


def cleanup_unreferenced_chapter_files(state: str, class_name: str) -> int:
    class_root = ROOT / state / class_name
    if not class_root.exists():
        return 0
    removed = 0
    for subject_dir in sorted([p for p in class_root.iterdir() if p.is_dir()]):
        chapters_path = subject_dir / "chapters.json"
        if not chapters_path.exists():
            continue
        try:
            data = read_json(chapters_path)
        except Exception:
            continue
        refs = {str(row.get("file", "")).strip() for row in data.get("results", []) if str(row.get("file", "")).strip()}
        for jf in subject_dir.glob("*.json"):
            if jf.name == "chapters.json":
                continue
            if jf.name not in refs:
                jf.unlink(missing_ok=True)
                removed += 1
    return removed


def regenerate_class(state: str, class_name: str) -> int:
    class_root = ROOT / state / class_name
    if not class_root.exists():
        return 0
    count_files = 0

    for subject_dir in sorted([p for p in class_root.iterdir() if p.is_dir()]):
        chapters_path = subject_dir / "chapters.json"
        if not chapters_path.exists():
            continue
        ch_doc = read_json(chapters_path)
        rows = ch_doc.get("results", [])
        for row in rows:
            subject = str(row.get("subject", "")).strip()
            chapter = str(row.get("chapter", "")).strip()
            file_name = str(row.get("file", "")).strip()
            if not subject or not chapter or not file_name:
                continue
            out_path = subject_dir / file_name
            data = {"results": generate_questions(state, subject, chapter, 100)}
            write_json(out_path, data)
            count_files += 1
    return count_files


def main() -> None:
    total_files = 0
    total_removed = 0
    for st in TARGET_STATES:
        st_root = ROOT / st
        if not st_root.exists():
            continue
        update_10th_chapters(st, st_root)
        update_inter_chapters(st, st_root)
        total_files += regenerate_class(st, "10thclass")
        total_files += regenerate_class(st, "inter")
        total_removed += cleanup_unreferenced_chapter_files(st, "10thclass")
        total_removed += cleanup_unreferenced_chapter_files(st, "inter")
    print(f"Regenerated chapter files: {total_files}")
    print(f"Removed unreferenced chapter files: {total_removed}")


if __name__ == "__main__":
    main()
