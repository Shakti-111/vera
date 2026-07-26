from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

# Load the same embedding model used during ingestion
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to Qdrant
client = QdrantClient(host="localhost", port=6333)

# Ask a test question
# query = "What is Bluetooth used for?"
query = "How far can Wi-Fi signals travel?"

# Convert the question into an embedding
query_embedding = model.encode(query).tolist()

# Search Qdrant for the most similar chunks (newer method name)
results = client.query_points(
    collection_name="iot_notes",
    query=query_embedding,
    limit=3
).points

print(f"Question: {query}\n")
print("--- Top matching chunks ---\n")
for i, result in enumerate(results):
    print(f"Match {i+1} (similarity score: {result.score:.3f}):")
    print(result.payload["text"])
    print()