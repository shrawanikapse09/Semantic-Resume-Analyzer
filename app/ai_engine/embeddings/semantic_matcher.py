from sentence_transformers import (
    SentenceTransformer,
    util
)

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def calculate_semantic_similarity(
    resume_text,
    job_description
):

    embedding_1 = model.encode(
        resume_text,
        convert_to_tensor=True
    )

    embedding_2 = model.encode(
        job_description,
        convert_to_tensor=True
    )

    similarity = util.pytorch_cos_sim(
        embedding_1,
        embedding_2
    )

    similarity_score = round(
        similarity.item() * 100,
        2
    )

    return similarity_score