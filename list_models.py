
import os
from google import genai

# Your NEW key
KEY = "AIzaSyCIcBPhshJzBbtQT6rIpj-MozwDTfF7SAk"

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
