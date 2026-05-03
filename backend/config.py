import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
# Watson AI configuration
WATSON_API_KEY = os.environ["WATSON_API_KEY"]
WATSON_DEPLOYMENT_URL = os.environ["WATSON_DEPLOYMENT_URL"]

# Legacy/optional keys
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

BRAIN_PATH = Path(os.environ.get("BRAIN_PATH", "./brain"))
NOTES_DIR = BRAIN_PATH / "notes"
INDEX_PATH = BRAIN_PATH / "index.json"
NOTES_DIR.mkdir(parents=True, exist_ok=True)
