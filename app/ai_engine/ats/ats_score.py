from ai_engine.parser.skill_extractor import (
    extract_skills
)


def calculate_ats_score(
    resume_text,
    job_description
):

    resume_text = resume_text.lower()

    job_description = (
        job_description.lower()
    )

    resume_skills = set(
        extract_skills(resume_text)
    )

    jd_skills = set(
        extract_skills(job_description)
    )

    matched_skills = []

    for skill in jd_skills:

        for resume_skill in resume_skills:

            if (
                skill.lower()
                in
                resume_skill.lower()
            ) or (
                resume_skill.lower()
                in
                skill.lower()
            ):

                matched_skills.append(
                    skill
                )

                break

    matched_skills = set(
        matched_skills
    )

    missing_skills = (
        jd_skills - matched_skills
    )

    if len(jd_skills) == 0:

        return (
            0,
            [],
            []
        )

    score = (
        len(matched_skills)
        /
        len(jd_skills)
    ) * 100

    return (

        round(score, 2),

        sorted(
            list(matched_skills)
        ),

        sorted(
            list(missing_skills)
        )
    )