import os
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis do .env

DATABASE_URL = "postgresql://postgres:Fe151206@localhost:5432/noticias"
SECRET_KEY = "12345"

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

NEWS_API_KEY = "1bf2e80f4fdc46d58184aead28a3c66e"
BASE_URL = "https://newsapi.org/v2/top-headlines"
