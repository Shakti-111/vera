from sentence_transformers import SentenceTransformer
import psycopg2

# Load the same embedding model used during ingestion
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to pgvector
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="postgres",
    user="postgres",
    password="vera123"
)
cur = conn.cursor()

# Ask the same test question we used with Qdrant, for a fair comparison
query = "What is Bluetooth used for?"
query_embedding = model.encode(query).tolist()

# Search pgvector for the most similar chunks using cosine distance
cur.execute("""
    SELECT content, 1 - (embedding <=> %s::vector) AS similarity
    FROM iot_notes
    ORDER BY embedding <=> %s::vector
    LIMIT 3;
""", (query_embedding, query_embedding))

results = cur.fetchall()

print(f"Question: {query}\n")
print("--- Top matching chunks (pgvector) ---\n")
for i, (content, similarity) in enumerate(results):
    print(f"Match {i+1} (similarity score: {similarity:.3f}):")
    print(content)
    print()

cur.close()
conn.close()