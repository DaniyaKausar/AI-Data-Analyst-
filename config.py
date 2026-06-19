import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Model
GROQ_MODEL = "llama-3.3-70b-versatile"

# Database
DB_PATH = "sql/insightiq.db"
TABLE_NAME = "superstore"

# Dataset
DEFAULT_DATASET = "clean_superstore.csv"

# App
APP_TITLE = "InsightIQ — AI Business Intelligence Assistant"
APP_ICON = "📊"