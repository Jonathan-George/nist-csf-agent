from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

VECTOR_DIR = "data/nist_vectors"

# Load embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Load vector database
db = Chroma(
    persist_directory=VECTOR_DIR,
    embedding_function=embeddings
)

def nist_lookup(query: str, k: int = 5) -> str:
    """
    Retrieve authoritative NIST CSF text from the PDF.
    """
    results = db.similarity_search(query, k=k)
    return "\n\n".join([r.page_content for r in results])
