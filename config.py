from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY   = os.getenv("GROQ_API_KEY")
GMAIL_USER     = os.getenv("GMAIL_USER")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
NOTIFY_EMAIL   = os.getenv("NOTIFY_EMAIL")