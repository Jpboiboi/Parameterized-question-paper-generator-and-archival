import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Set API key
openai.api_key = os.getenv("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")

# Test the API key
try:
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": "Generate a multiple choice question about Python programming."}
        ]
    )
    print("✅ Success! Here's a response from OpenAI:\n")
    print(response.choices[0].message.content)  # ✅ Correct object-based access
except Exception as e:
    print("❌ Error occurred:")
    print(e)
