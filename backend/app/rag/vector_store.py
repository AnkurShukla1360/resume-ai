
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


# Local embedding model: no separate paid API required.
_embeddings = None


def get_embeddings():
    global _embeddings

    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

    return _embeddings


def build_resume_vector_store(
    resume_text: str,
    analysis_id: str,
):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100,
    )

    documents = splitter.create_documents(
        [resume_text],
        metadatas=[{"source": "resume"}],
    )

    if not documents:
        raise ValueError("No resume text available for indexing.")

    # In-memory collection for this analysis.
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=get_embeddings(),
        collection_name=f"resume_{analysis_id.replace('-', '')}",
    )

    return vector_store


def retrieve_resume_evidence(
    vector_store,
    query: str,
    k: int = 3,
) -> list[str]:
    documents = vector_store.similarity_search(query, k=k)
    return [doc.page_content for doc in documents]
