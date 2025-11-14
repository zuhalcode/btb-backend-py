import requests
from binance.client import Client
from libs.env import (
    BINANCE_API_KEY,
    BINANCE_API_SECRET,
    BINANCE_API_URL_TESTNET,
    BINANCE_API_URL,
    TESTNET,
)


class MarketService:

    def __init__(self):
        self.testnet = TESTNET
        self.client = Client(BINANCE_API_KEY, BINANCE_API_SECRET, testnet=TESTNET)
        self.client.REQUEST_RECVWINDOW = 5000
        self.client.API_URL = BINANCE_API_URL_TESTNET if TESTNET else BINANCE_API_URL

    def get_live_price(self, symbol: str) -> float:
        try:
            base_url = self.client.API_URL
            api_endpoint = f"{base_url}/api/v3/ticker/price?symbol={symbol.upper()}"

            res = requests.get(api_endpoint)
            res.raise_for_status()
            return float(res.json()["price"])
        except Exception as e:
            print(f"[MarketService] Error get_live_price({symbol}): {e}")
            return None

    @staticmethod
    def get_klines(symbol: str, interval="1m", limit=100):
        """Ambil historical candlestick"""
        try:
            res = requests.get(
                f"{MarketService.BASE_URL}/api/v3/klines",
                params={"symbol": symbol.upper(), "interval": interval, "limit": limit},
            )
            res.raise_for_status()
            return res.json()
        except Exception as e:
            print(f"[MarketService] Error get_klines({symbol}): {e}")
            return []
