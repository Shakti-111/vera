# from pypdf import PdfReader

# # Step 1: Read the PDF
# reader = PdfReader("COMMUNICATION MODULES.pdf")

# text = ""
# for page in reader.pages:
#     text += page.extract_text()

# print("PDF loaded successfully.")
# print(f"Total pages: {len(reader.pages)}")
# print(f"Total characters extracted: {len(text)}")
# print("\n--- First 300 characters ---")
# print(text[:300])

#..............................CHUNKING.............................................

# from pypdf import PdfReader
# from langchain_text_splitters import RecursiveCharacterTextSplitter

# # Step 1: Read the PDF
# reader = PdfReader("COMMUNICATION MODULES.pdf")

# text = ""
# for page in reader.pages:
#     text += page.extract_text()

# print("PDF loaded successfully.")
# print(f"Total pages: {len(reader.pages)}")
# print(f"Total characters extracted: {len(text)}")

# # Step 2: Split the text into chunks
# splitter = RecursiveCharacterTextSplitter(
#     chunk_size=500,      # roughly how many characters per chunk
#     chunk_overlap=50     # slight overlap so context isn't lost between chunks
# )

# chunks = splitter.split_text(text)

# print(f"\nTotal chunks created: {len(chunks)}")
# print("\n--- First chunk ---")
# print(chunks[0])
# print("\n--- Second chunk ---")
# print(chunks[1])


#...................................EMBEDDING.....................................................

# from pypdf import PdfReader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from sentence_transformers import SentenceTransformer

# # Step 1: Read the PDF
# reader = PdfReader("COMMUNICATION MODULES.pdf")

# text = ""
# for page in reader.pages:
#     text += page.extract_text()

# print("PDF loaded successfully.")
# print(f"Total pages: {len(reader.pages)}")
# print(f"Total characters extracted: {len(text)}")

# # Step 2: Split the text into chunks
# splitter = RecursiveCharacterTextSplitter(
#     chunk_size=500,
#     chunk_overlap=50
# )
# chunks = splitter.split_text(text)
# print(f"\nTotal chunks created: {len(chunks)}")

# # Step 3: Convert chunks into embeddings
# print("\nLoading embedding model... (this may take a minute the first time)")
# model = SentenceTransformer("all-MiniLM-L6-v2")

# embeddings = model.encode(chunks)

# print(f"\nEmbeddings created: {len(embeddings)}")
# print(f"Each embedding has {len(embeddings[0])} numbers")
# print("\n--- First 10 numbers of chunk 1's embedding ---")
# print(embeddings[0][:10])


#.................................ACTUALLY SAVE THE CHUNKS INTO QDRANT ...................................

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

# Step 1: Read the PDF
reader = PdfReader("COMMUNICATION MODULES.pdf")

text = ""
for page in reader.pages:
    text += page.extract_text()

print("PDF loaded successfully.")
print(f"Total pages: {len(reader.pages)}")
print(f"Total characters extracted: {len(text)}")

# Step 2: Split the text into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
chunks = splitter.split_text(text)
print(f"\nTotal chunks created: {len(chunks)}")

# Step 3: Convert chunks into embeddings
print("\nLoading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(chunks)
print(f"Embeddings created: {len(embeddings)}")

# Step 4: Store chunks + embeddings in Qdrant
print("\nConnecting to Qdrant...")
client = QdrantClient(host="localhost", port=6333)

collection_name = "iot_notes"

# Create a collection (like a "table") if it doesn't already exist
client.recreate_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

# Prepare the data points (each chunk + its embedding)
points = [
    PointStruct(
        id=i,
        vector=embeddings[i].tolist(),
        payload={"text": chunks[i]}
    )
    for i in range(len(chunks))
]

# Upload them into Qdrant
client.upsert(collection_name=collection_name, points=points)

print(f"\n✅ Successfully stored {len(chunks)} chunks in Qdrant collection '{collection_name}'")