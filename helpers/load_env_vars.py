from dotenv import load_dotenv
import os

def load():
    """Loads environment variables from a .env file in the project root."""
    load_dotenv()

    groq_api_key = os.getenv("GROQ_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")