from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)

response = client.chat.completions.create(
    # model="meta/llama-3.3-70b-instruct",
    model="openai/gpt-oss-20b",
    # model="mistralai/mistral-7b-instruct-v0.3",
    messages=[
        {"role": "user", "content": "Say hello and confirm you're working, in one short sentence."}
    ],
    max_tokens=200
)

print(response.choices[0].message.content)