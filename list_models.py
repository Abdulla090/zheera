import os
from google import genai

# Load API key from environment variable (never hardcode keys in source)
KEY = os.environ.get("GEMINI_API_KEY", "")

if not KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

try:
    client = genai.Client(api_key=KEY)
    print("--- Available Gemini Models ---")
    for m in client.models.list(config={"page_size": 100}):
        # Filter for generateContent models (chat/text)
        if "generateContent" in m.supported_generation_methods:
            # Look for the latest ones
            if "gemini" in m.name:
                print(f"ID: {m.name} | Display: {m.display_name}")
except Exception as e:
    print(f"Error listing models: {e}")