import pdfplumber


def extract_text_from_pdf(pdf_path):

    text = ""

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            extracted_text = (
                page.extract_text()
            )

            if extracted_text:

                text += (
                    extracted_text + "\n"
                )

    return text