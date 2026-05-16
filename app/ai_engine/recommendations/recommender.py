def generate_recommendations(
    missing_skills
):

    recommendations = []

    skill_map = {

        "python":
        "Improve Python programming skills.",

        "sql":
        "Practice SQL queries and database management.",

        "fastapi":
        "Learn FastAPI backend development.",

        "docker":
        "Gain hands-on Docker container experience.",

        "machine learning":
        "Study ML algorithms and AI concepts.",

        "git":
        "Learn Git and GitHub workflows.",

        "mongodb":
        "Practice NoSQL database management.",

        "apis":
        "Understand REST APIs and integrations.",

        "communication":
        "Improve communication and teamwork skills."
    }

    for skill in missing_skills:

        skill_lower = skill.lower()

        if skill_lower in skill_map:

            recommendations.append(
                skill_map[skill_lower]
            )

    return recommendations