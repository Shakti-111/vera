from anthropic import Anthropic
from dotenv import load_dotenv
import os

# Load your API key from the .env file
load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=200,
    messages=[
        {"role": "user", "content": "Say hello and confirm you're working, in one short sentence."}
    ]
)

print(response.content[0].text)