from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 1) Embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 2) Cargar documentos (PDF + TXT)
docs = []

pdf_loader = DirectoryLoader("documentos", glob="**/*.pdf", loader_cls=PyPDFLoader)
txt_loader = DirectoryLoader("documentos", glob="**/*.txt", loader_cls=TextLoader)

docs.extend(pdf_loader.load())
docs.extend(txt_loader.load())

print(f"Documentos crudos: {len(docs)}")

# 3) Partir en trozos (chunking)
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
docs_split = splitter.split_documents(docs)

print(f"Chunks generados: {len(docs_split)}")

# 4) Crear índice FAISS y guardar
db = FAISS.from_documents(docs_split, embeddings)
db.save_local("faiss_index")

print("✅ Índice FAISS creado en 'faiss_index'")
