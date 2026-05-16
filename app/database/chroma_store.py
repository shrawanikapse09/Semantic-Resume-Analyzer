import chromadb

from sentence_transformers import (
    SentenceTransformer
)

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(
    path="app/chroma_db"
)

collection = client.get_or_create_collection(
    name="resumes"
)


def store_resume(
    resume_id,
    resume_text
):

    embedding = model.encode(
        resume_text
    ).tolist()

    collection.add(
        documents=[resume_text],
        embeddings=[embedding],
        ids=[resume_id]
    )


def search_resumes(
    job_description,
    top_k=10
):

    query_embedding = model.encode(
        job_description
    ).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results