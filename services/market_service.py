import requests
from binance.client import Client
from libs.env import (
    BINANCE_API_KEY,
    BINANCE_API_SECRET,
    BINANCE_API_URL_TESTNET,
    BINANCE_API_URL,
)


class MarketService:

    def __init__(self, testnet: bool = True):
        self.testnet = testnet
        self.client = Client(BINANCE_API_KEY, BINANCE_API_SECRET, testnet=testnet)
        self.client.REQUEST_RECVWINDOW = 5000
        self.client.API_URL = BINANCE_API_URL_TESTNET if testnet else BINANCE_API_URL

    @staticmethod
    def get_live_price(symbol: str) -> float:
        """Ambil harga live dari Binance"""
        try:
            res = requests.get(
                f"{MarketService.BASE_URL}/api/v3/ticker/price?symbol={symbol.upper()}"
            )
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
