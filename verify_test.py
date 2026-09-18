from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

llm_client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)

# Same context as before (Bluetooth section)
context = """• Bluetooth is a short-range wireless technology
standard that is used for exchanging data between
fixed and mobile devices over short distances and
building personal area networks (PANs).
- In the most widely used mode, transmission power is
limited to 2.5 milliwatts, giving it a very short range of
up to 10 metres (33 ft). It employs UHF radio waves in
the ISM bands, from 2.402 GHz to 2.48 GHz."""

# Deliberately WRONG answer - claims Bluetooth has 100km range (false!)
wrong_answer = "Bluetooth is used for long-range communication and can transmit data up to 100 kilometers, making it ideal for satellite communication."

verification_prompt = f"""You are a strict fact-checking assistant. Your job is to check whether an answer is fully supported by the given context.

Context:
{context}

Answer to verify:
{wrong_answer}

Check every claim in the answer against the context. Respond ONLY in this exact JSON format, with no other text:
{{
  "trust_score": <a number from 0 to 100, where 100 means fully supported by the context>,
  "fully_supported": <true or false>,
  "unsupported_claims": [<list any specific claims NOT found in the context, or empty list if none>],
  "reasoning": "<one sentence explaining your score>"
}}"""

response = llm_client.chat.completions.create(
    model="minimaxai/minimax-m3",
    # model="meta/llama-3.3-70b-instruct",
    messages=[{"role": "user", "content": verification_prompt}],
    max_tokens=300
)

result_text = response.choices[0].message.content
cleaned = result_text.strip().replace("```json", "").replace("```", "")
result = json.loads(cleaned)

print("Testing a DELIBERATELY WRONG answer:\n")
print(f"Answer being checked: {wrong_answer}\n")
print(f"Trust Score: {result['trust_score']}/100")
print(f"Fully Supported: {result['fully_supported']}")
print(f"Reasoning: {result['reasoning']}")
print(f"Unsupported Claims: {result['unsupported_claims']}")