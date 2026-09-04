import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-3.1-flash-lite",
    contents="Reply with exactly: Model test successful."
)

print("=" * 60)
print("MODEL TEST")
print("=" * 60)
print(response.text)
print("=" * 60)