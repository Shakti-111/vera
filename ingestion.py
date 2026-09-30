import io
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client.models import VectorParams, Distance, PointStruct

from generate_answer import model as embedding_model, client as qdrant_client

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def ingest_pdf(file_bytes, collection_name="uploaded_doc"):
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    if not text.strip():
        raise ValueError("No readable text found in this PDF. It may be a scanned, image-only document.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = splitter.split_text(text)
    embeddings = embedding_model.encode(chunks)

    if qdrant_client.collection_exists(collection_name):
        qdrant_client.delete_collection(collection_name)

    qdrant_client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=len(embeddings[0]), distance=Distance.COSINE),
    )

    points = [
        PointStruct(id=i, vector=embeddings[i].tolist(), payload={"text": chunks[i]})
        for i in range(len(chunks))
    ]
    qdrant_client.upsert(collection_name=collection_name, points=points)

    return {"pages": len(reader.pages), "chunks": len(chunks)}