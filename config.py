import os
from dotenv import load_dotenv
load_dotenv()  # Carrega variáveis do .env

DATABASE_URL = "postgres://uas8ulgphgk6um:p2678d698162c89550ed965286842fe34da8c45a48d040db374cb5862b94250e3@cd5gks8n4kb20g.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/ddf6eu4nbjhhp2"
SECRET_KEY = "12345"

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

NEWS_API_KEY = "1bf2e80f4fdc46d58184aead28a3c66e"
BASE_URL = "https://newsapi.org/v2/top-headlines"
