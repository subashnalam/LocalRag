import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from the project root directory
env_path = Path(__file__).parents[2] / '.env'
load_dotenv(env_path)

class Settings:
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
