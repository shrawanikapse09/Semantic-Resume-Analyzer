import spacy

nlp = spacy.load(
    "en_core_web_sm"
)

SKILLS = [

    # TECH
    "python",
    "sql",
    "docker",
    "fastapi",
    "machine learning",
    "tensorflow",
    "pandas",
    "scikit-learn",
    "apis",
    "git",
    "mongodb",
    "kubernetes",
    "mlops",

    # CHILDCARE
    "childcare",
    "counseling",
    "special needs",
    "education",
    "activity planning",
    "client management",
    "volunteer management",
    "teaching",
    "coordination",
    "communication",

    # BUSINESS
    "leadership",
    "management",
    "teamwork",
    "organizational skills",
    "problem-solving",

    # HEALTHCARE
    "healthcare",
    "patient care",
    "clinical support",

    # FINANCE
    "accounting",
    "financial analysis",
    "budgeting",
    "taxation",

    # MARKETING
    "digital marketing",
    "seo",
    "content creation"
]


def extract_skills(text):

    doc = nlp(text.lower())

    found_skills = set()

    for token in doc:

        for skill in SKILLS:
            if skill.lower() in token.text.lower():
                found_skills.add(skill)

    return list(found_skills)