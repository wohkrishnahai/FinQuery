from dotenv import load_dotenv
import os
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

print("1. API key loaded:", bool(api_key))

if not api_key:
    raise RuntimeError("GEMINI_API_KEY is missing")

print("2. Creating Gemini client...")

client = genai.Client(
    api_key=api_key
)

print("3. Gemini client created")

print("4. Sending request...")

try:
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents="Reply with exactly: Gemini connection successful",
    )

    print("5. Response received")
    print(response.text)

except Exception as e:
    print("\n--- GEMINI ERROR ---")
    print(type(e).__name__)
    print(str(e))
    print("--------------------")
