from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import (
    getSampleStyleSheet
)

from reportlab.lib.pagesizes import (
    letter
)


def generate_report(

    ats_score,

    semantic_score,

    matched_skills,

    missing_skills,

    recommendations
):

    pdf_path = "ATS_Report.pdf"

    doc = SimpleDocTemplate(

        pdf_path,

        pagesize=letter
    )

    styles = getSampleStyleSheet()

    elements = []

    elements.append(

        Paragraph(

            "AI Resume Analysis Report",

            styles['Title']
        )
    )

    elements.append(
        Spacer(1, 20)
    )

    elements.append(

        Paragraph(

            f"ATS Score: {ats_score}%",

            styles['BodyText']
        )
    )

    elements.append(

        Paragraph(

            f"Semantic Similarity: {semantic_score}%",

            styles['BodyText']
        )
    )

    elements.append(
        Spacer(1, 20)
    )

    elements.append(

        Paragraph(

            "Matched Skills:",

            styles['Heading2']
        )
    )

    for skill in matched_skills:

        elements.append(

            Paragraph(

                f"• {skill}",

                styles['BodyText']
            )
        )

    elements.append(
        Spacer(1, 15)
    )

    elements.append(

        Paragraph(

            "Missing Skills:",

            styles['Heading2']
        )
    )

    for skill in missing_skills:

        elements.append(

            Paragraph(

                f"• {skill}",

                styles['BodyText']
            )
        )

    elements.append(
        Spacer(1, 15)
    )

    elements.append(

        Paragraph(

            "AI Recommendations:",

            styles['Heading2']
        )
    )

    for rec in recommendations:

        elements.append(

            Paragraph(

                f"• {rec}",

                styles['BodyText']
            )
        )

    doc.build(elements)

    return pdf_path