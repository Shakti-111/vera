
#This will reuse the same PDF-reading, chunking, and embedding steps, but store the results in pgvector instead of Qdrant.

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import psycopg2

# Step 1: Read the PDF
reader = PdfReader("COMMUNICATION MODULES.pdf")
text = ""
for page in reader.pages:
    text += page.extract_text()

print("PDF loaded successfully.")
print(f"Total characters extracted: {len(text)}")

# Step 2: Split into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_text(text)
print(f"Total chunks created: {len(chunks)}")

# Step 3: Generate embeddings
print("\nLoading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(chunks)
print(f"Embeddings created: {len(embeddings)}")

# Step 4: Connect to pgvector (PostgreSQL)
print("\nConnecting to pgvector...")
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="postgres",
    user="postgres",
    password="vera123"
)
cur = conn.cursor()

# Enable the pgvector extension (only needs to happen once, safe to repeat)
cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

# Create a table to hold our chunks + embeddings (384 numbers each, same as before)
cur.execute("""
    DROP TABLE IF EXISTS iot_notes;
    CREATE TABLE iot_notes (
        id SERIAL PRIMARY KEY,
        content TEXT,
        embedding vector(384)
    );
""")

# Insert each chunk + embedding
for i, chunk in enumerate(chunks):
    cur.execute(
        "INSERT INTO iot_notes (content, embedding) VALUES (%s, %s)",
        (chunk, embeddings[i].tolist())
    )

conn.commit()
print(f"\n✅ Successfully stored {len(chunks)} chunks in pgvector table 'iot_notes'")

cur.close()
conn.close()