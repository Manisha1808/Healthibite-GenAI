import chromadb
from sentence_transformers import SentenceTransformer

# Load data
with open("data/health_docs.txt", "r") as f:
    text = f.read()

def split_text(text, chunk_size=200, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

docs = split_text(text)

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# ✅ USE THIS
chroma_client = chromadb.PersistentClient(path="./chroma_db")

collection = chroma_client.get_or_create_collection(name="health_data")

# Store embeddings
for i, doc in enumerate(docs):
    embedding = model.encode(doc).tolist()
    collection.add(
        documents=[doc],
        embeddings=[embedding],
        ids=[str(i)]
    )

print("✅ Embeddings created and saved permanently!")