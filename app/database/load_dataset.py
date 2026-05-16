import sys
import os
import uuid

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from ai_engine.parser.resume_parser import (
    extract_text_from_pdf
)

from database.chroma_store import (
    store_resume
)


BASE_DIR = os.path.dirname(
    os.path.dirname(__file__)
)

RESUME_FOLDER = os.path.join(
    BASE_DIR,
    "data",
    "resumes"
)


def load_all_resumes():

    print(
        f"Reading resumes from: {RESUME_FOLDER}"
    )

    files = os.listdir(
        RESUME_FOLDER
    )

    print(
        f"Found {len(files)} files"
    )

    for file_name in files:

        if file_name.endswith(".pdf"):

            pdf_path = os.path.join(
                RESUME_FOLDER,
                file_name
            )

            print(
                f"Processing: {file_name}"
            )

            extracted_text = (
                extract_text_from_pdf(
                    pdf_path
                )
            )

            resume_id = str(
                uuid.uuid4()
            )

            store_resume(
                resume_id,
                extracted_text
            )

    print(
        "All resumes stored successfully!"
    )


if __name__ == "__main__":

    load_all_resumes()