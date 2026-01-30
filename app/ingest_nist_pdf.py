from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

PDF_PATH = "data/NIST.CSWP.29.pdf"
VECTOR_DIR = "data/nist_vectors"

print("Loading NIST CSF PDF...")
loader = PyPDFLoader(PDF_PATH)
documents = loader.load()

print("Splitting text...")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=200
)
chunks = splitter.split_documents(documents)

print("Creating embeddings...")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

print("Persisting vectors...")
db = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=VECTOR_DIR
)
db.persist()

print("✅ NIST CSF PDF INGESTED SUCCESSFULLY")
