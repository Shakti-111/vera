# # Member B
# from sentence_transformers import SentenceTransformer
# from qdrant_client import QdrantClient
# from openai import OpenAI
# from dotenv import load_dotenv
# import os

# load_dotenv()

# # Step 1: Set up the embedding model and Qdrant connection (same as before)
# model = SentenceTransformer("all-MiniLM-L6-v2")
# client = QdrantClient(host="localhost", port=6333)

# # Step 2: Set up the NVIDIA client (using your free API)
# llm_client = OpenAI(
#     base_url="https://integrate.api.nvidia.com/v1",
#     api_key=os.getenv("NVIDIA_API_KEY")
# )

# # Step 3: Ask a question
# query = "What is Bluetooth used for?"

# # Step 4: Retrieve relevant chunks (same as search_test.py)
# query_embedding = model.encode(query).tolist()
# results = client.query_points(
#     collection_name="iot_notes",
#     query=query_embedding,
#     limit=3
# ).points

# # Step 5: Combine the retrieved chunks into context
# context = "\n\n".join([r.payload["text"] for r in results])

# print("--- Retrieved Context ---")
# print(context)
# print("\n--- Generating Answer ---\n")

# # Step 6: Ask the LLM to answer using ONLY the retrieved context
# prompt = f"""Answer the question using ONLY the information in the context below.
# If the context doesn't contain enough information to answer, say so clearly.

# Context:
# {context}

# Question: {query}

# Answer:"""

# response = llm_client.chat.completions.create(
#     model="meta/llama-3.3-70b-instruct",
#     messages=[{"role": "user", "content": prompt}],
#     max_tokens=300
# )

# answer = response.choices[0].message.content
# print("Question:", query)
# print("\nAnswer:", answer)






# #verification step
# import json

# # Step 7: Verify the answer against the context
# print("\n--- Verifying Answer ---\n")

# verification_prompt = f"""You are a strict fact-checking assistant. Your job is to check whether an answer is fully supported by the given context.

# Context:
# {context}

# Answer to verify:
# {answer}

# Check every claim in the answer against the context. Respond ONLY in this exact JSON format, with no other text:
# {{
#   "trust_score": <a number from 0 to 100, where 100 means fully supported by the context>,
#   "fully_supported": <true or false>,
#   "unsupported_claims": [<list any specific claims NOT found in the context, or empty list if none>],
#   "reasoning": "<one sentence explaining your score>"
# }}"""

# verification_response = llm_client.chat.completions.create(
#     model="meta/llama-3.3-70b-instruct",
#     messages=[{"role": "user", "content": verification_prompt}],
#     max_tokens=300
# )

# verification_text = verification_response.choices[0].message.content

# # Try to parse the JSON response
# try:
#     # Sometimes models wrap JSON in markdown code blocks, so we clean that up
#     cleaned = verification_text.strip().replace("```json", "").replace("```", "")
#     verification_result = json.loads(cleaned)

#     print(f"Trust Score: {verification_result['trust_score']}/100")
#     print(f"Fully Supported: {verification_result['fully_supported']}")
#     print(f"Reasoning: {verification_result['reasoning']}")
#     if verification_result['unsupported_claims']:
#         print(f"Unsupported Claims: {verification_result['unsupported_claims']}")
# except Exception as e:
#     print("Could not parse verification response as JSON. Raw response:")
#     print(verification_text)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#What This Code Block Actually Does
# This is the verification step — the part that takes the answer the AI just generated and asks a second, separate AI call to fact-check it against the source material, instead of just trusting the first answer blindly.



# from sentence_transformers import SentenceTransformer
# from qdrant_client import QdrantClient
# from openai import OpenAI
# from dotenv import load_dotenv
# import os
# import json

# load_dotenv()

# # Set up once, outside the function (so we don't reload the model every call)
# model = SentenceTransformer("all-MiniLM-L6-v2")
# client = QdrantClient(host="localhost", port=6333)
# # LLM_MODEL = "minimaxai/minimax-m3"
# # LLM_MODEL = "nvidia/nemotron-3-ultra-550b-a55b"
# # LLM_MODEL = "deepseek-ai/deepseek-v4-flash-0731"
# # LLM_MODEL = "meta/llama-3.1-8b-instruct"
# # LLM_MODEL = "nvidia/nemotron-3.5-lightning-30b-a3b"
# LLM_MODEL = "openai/gpt-oss-20b"
# # LLM_MODEL = "mistralai/mistral-7b-instruct-v0.3"
# llm_client = OpenAI(
#     base_url="https://integrate.api.nvidia.com/v1",
#     api_key=os.getenv("NVIDIA_API_KEY")
# )

# TRUST_THRESHOLD = 50  # below this, we retry


# def retrieve_chunks(query, limit=3):
#     query_embedding = model.encode(query).tolist()
#     results = client.query_points(
#         collection_name="iot_notes",
#         query=query_embedding,
#         limit=limit
#     ).points
#     return [r.payload["text"] for r in results]


# def generate_answer(query, chunks):
#     context = "\n\n".join(chunks)
#     prompt = f"""Answer the question using ONLY the information in the context below.
# If the context doesn't contain enough information to answer, say so clearly.

# Context:
# {context}

# Question: {query}

# Answer:"""
#     response = llm_client.chat.completions.create(
#         model=LLM_MODEL,
#         messages=[{"role": "user", "content": prompt}],
#         max_tokens=300
#     )
#     return response.choices[0].message.content, context


# def verify_answer(context, answer):
#     verification_prompt = f"""You are a strict fact-checking assistant. Your job is to check whether an answer is fully supported by the given context.

# Context:
# {context}

# Answer to verify:
# {answer}

# Check every claim in the answer against the context. Respond ONLY in this exact JSON format, with no other text:
# {{
#   "trust_score": <a number from 0 to 100, where 100 means fully supported by the context>,
#   "fully_supported": <true or false>,
#   "unsupported_claims": [<list any specific claims NOT found in the context, or empty list if none>],
#   "reasoning": "<one sentence explaining your score>"
# }}"""
#     response = llm_client.chat.completions.create(
#         model=LLM_MODEL,
#         messages=[{"role": "user", "content": verification_prompt}],
#         max_tokens=300
#     )

#     content = response.choices[0].message.content
#     if content is None:
#         raise Exception("Empty response from model - likely a transient issue")
#     cleaned = content.strip().replace("```json", "").replace("```", "")
#     return json.loads(cleaned)

# def ask_vera(query):
#     """
#     The main function: retrieve, generate, verify, and retry if needed.
#     Returns a dictionary with the answer, trust score, and supporting info.
#     """
#     print(f"\nQuestion: {query}")

#     # First attempt with top 3 chunks
#     chunks = retrieve_chunks(query, limit=5)
#     answer, context = generate_answer(query, chunks)
#     verification = verify_answer(context, answer)

#     print(f"\nFirst attempt trust score: {verification['trust_score']}/100")

#     # If trust score is too low, retry with more chunks
#     if verification["trust_score"] < TRUST_THRESHOLD:
#         print("Trust score too low — retrying with more context (top 5 chunks)...")
#         chunks = retrieve_chunks(query, limit=5)
#         answer, context = generate_answer(query, chunks)
#         verification = verify_answer(context, answer)
#         print(f"Second attempt trust score: {verification['trust_score']}/100")

#     return {
#         "question": query,
#         "answer": answer,
#         "trust_score": verification["trust_score"],
#         "fully_supported": verification["fully_supported"],
#         "reasoning": verification["reasoning"],
#         "unsupported_claims": verification["unsupported_claims"],
#         "sources": chunks
#     }


# # Test it out
# if __name__ == "__main__":
#     result = ask_vera("What is Bluetooth used for?")
#     # result = ask_vera("What is the maximum transmission distance and frequency range across all the wireless modules mentioned?")
#     # result = ask_vera("What security encryption protocols does each wireless module use?")
#     print("\n--- Final Result ---")
#     print(f"Answer: {result['answer']}")
#     print(f"Trust Score: {result['trust_score']}/100")
#     print(f"Reasoning: {result['reasoning']}")

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

# Set up once, outside the function (so we don't reload the model every call)
model = SentenceTransformer("all-MiniLM-L6-v2")
client = QdrantClient(host="localhost", port=6333)
# LLM_MODEL = "minimaxai/minimax-m3"
# LLM_MODEL = "nvidia/nemotron-3-ultra-550b-a55b"
# LLM_MODEL = "deepseek-ai/deepseek-v4-flash-0731"
# LLM_MODEL = "meta/llama-3.1-8b-instruct"
# LLM_MODEL = "nvidia/nemotron-3.5-lightning-30b-a3b"
LLM_MODEL = "openai/gpt-oss-20b"
# LLM_MODEL = "mistralai/mistral-7b-instruct-v0.3"
llm_client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)

TRUST_THRESHOLD = 50  # below this, we retry


def retrieve_chunks(query, limit=3, collection_name="iot_notes"):
    query_embedding = model.encode(query).tolist()
    results = client.query_points(
        collection_name=collection_name,
        query=query_embedding,
        limit=limit
    ).points
    return [r.payload["text"] for r in results]


def generate_answer(query, chunks):
    context = "\n\n".join(chunks)
    prompt = f"""Answer the question using ONLY the information in the context below.
If the context doesn't contain enough information to answer, say so clearly.

Context:
{context}

Question: {query}

Answer:"""
    response = llm_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    return response.choices[0].message.content, context


def verify_answer(context, answer):
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
    response = llm_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": verification_prompt}],
        max_tokens=300
    )

    content = response.choices[0].message.content
    if content is None:
        raise Exception("Empty response from model - likely a transient issue")
    cleaned = content.strip().replace("```json", "").replace("```", "")
    return json.loads(cleaned)


def ask_vera(query, collection_name="iot_notes"):
    """
    The main function: retrieve, generate, verify, and retry if needed.
    Returns a dictionary with the answer, trust score, and supporting info.
    """
    print(f"\nQuestion: {query}")

    # First attempt with top 5 chunks
    chunks = retrieve_chunks(query, limit=5, collection_name=collection_name)
    answer, context = generate_answer(query, chunks)
    verification = verify_answer(context, answer)

    print(f"\nFirst attempt trust score: {verification['trust_score']}/100")

    # If trust score is too low, retry with more chunks
    if verification["trust_score"] < TRUST_THRESHOLD:
        print("Trust score too low — retrying with more context (top 5 chunks)...")
        chunks = retrieve_chunks(query, limit=5, collection_name=collection_name)
        answer, context = generate_answer(query, chunks)
        verification = verify_answer(context, answer)
        print(f"Second attempt trust score: {verification['trust_score']}/100")

    return {
        "question": query,
        "answer": answer,
        "trust_score": verification["trust_score"],
        "fully_supported": verification["fully_supported"],
        "reasoning": verification["reasoning"],
        "unsupported_claims": verification["unsupported_claims"],
        "sources": chunks
    }


# Test it out
if __name__ == "__main__":
    result = ask_vera("What is Bluetooth used for?")
    # result = ask_vera("What is the maximum transmission distance and frequency range across all the wireless modules mentioned?")
    # result = ask_vera("What security encryption protocols does each wireless module use?")
    print("\n--- Final Result ---")
    print(f"Answer: {result['answer']}")
    print(f"Trust Score: {result['trust_score']}/100")
    print(f"Reasoning: {result['reasoning']}")