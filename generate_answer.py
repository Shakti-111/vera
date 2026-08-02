# Member B
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Step 1: Set up the embedding model and Qdrant connection (same as before)
model = SentenceTransformer("all-MiniLM-L6-v2")
client = QdrantClient(host="localhost", port=6333)

# Step 2: Set up the NVIDIA client (using your free API)
llm_client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)

# Step 3: Ask a question
query = "What is Bluetooth used for?"

# Step 4: Retrieve relevant chunks (same as search_test.py)
query_embedding = model.encode(query).tolist()
results = client.query_points(
    collection_name="iot_notes",
    query=query_embedding,
    limit=3
).points

# Step 5: Combine the retrieved chunks into context
context = "\n\n".join([r.payload["text"] for r in results])

print("--- Retrieved Context ---")
print(context)
print("\n--- Generating Answer ---\n")

# Step 6: Ask the LLM to answer using ONLY the retrieved context
prompt = f"""Answer the question using ONLY the information in the context below.
If the context doesn't contain enough information to answer, say so clearly.

Context:
{context}

Question: {query}

Answer:"""

response = llm_client.chat.completions.create(
    model="meta/llama-3.3-70b-instruct",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=300
)

answer = response.choices[0].message.content
print("Question:", query)
print("\nAnswer:", answer)






#verification step
import json

# Step 7: Verify the answer against the context
print("\n--- Verifying Answer ---\n")

verification_prompt = f"""You are a strict fact-checking assistant. Your job is to check whether an answer is fully supported by the given context.

Context:
{context}

Answer to verify:
{answer}

Check every claim in the answer against the context. Respond ONLY in this exact JSON format, with no other text:
{{
  "trust_score": <a number from 0 to 100, where 100 means fully supported by the context>,
  "fully_supported": <true or false>,
  "unsupported_claims": [<list any specific claims NOT found in the context, or empty list if none>],
  "reasoning": "<one sentence explaining your score>"
}}"""

verification_response = llm_client.chat.completions.create(
    model="meta/llama-3.3-70b-instruct",
    messages=[{"role": "user", "content": verification_prompt}],
    max_tokens=300
)

verification_text = verification_response.choices[0].message.content

# Try to parse the JSON response
try:
    # Sometimes models wrap JSON in markdown code blocks, so we clean that up
    cleaned = verification_text.strip().replace("```json", "").replace("```", "")
    verification_result = json.loads(cleaned)

    print(f"Trust Score: {verification_result['trust_score']}/100")
    print(f"Fully Supported: {verification_result['fully_supported']}")
    print(f"Reasoning: {verification_result['reasoning']}")
    if verification_result['unsupported_claims']:
        print(f"Unsupported Claims: {verification_result['unsupported_claims']}")
except Exception as e:
    print("Could not parse verification response as JSON. Raw response:")
    print(verification_text)