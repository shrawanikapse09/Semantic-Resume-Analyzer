
import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from database.chroma_store import (
    search_resumes
)


job_query = """
Looking for a Python Developer with
skills in Python, SQL, FastAPI,
APIs, Machine Learning, Docker, and Git.
"""

results = search_resumes(
    job_query
)

print(results)