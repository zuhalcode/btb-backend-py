from dotenv import load_dotenv
import os

load_dotenv()  # otomatis baca .env di root project

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
BINANCE_API_URL = os.getenv("BINANCE_API_URL")
BINANCE_API_URL_TESTNET = os.getenv("BINANCE_API_URL_TESTNET")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

TESTNET = os.getenv("TESTNET")
