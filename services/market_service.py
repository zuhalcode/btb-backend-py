import requests
import logging

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
        self.client = Client(
            BINANCE_API_KEY,
            BINANCE_API_SECRET,
            testnet=self.testnet,
            ping=False,
        )
        self.client.REQUEST_RECVWINDOW = 5000
        self.client.API_URL = BINANCE_API_URL_TESTNET if TESTNET else BINANCE_API_URL

        # Logging environment
        env = "TESTNET" if self.testnet else "MAINNET"
        print(f"ini env : {env} karena testnet = {self.testnet}")
        logging.warning(
            f"[MarketService] Running on {env} — URL = {self.client.API_URL}"
        )

    def get_live_price(self, symbol: str) -> float:
        try:
            base_url = self.client.API_URL
            api_endpoint = f"{base_url}/v3/ticker/price?symbol={symbol}"

            res = requests.get(api_endpoint)
            res.raise_for_status()
            return float(res.json()["price"])
        except Exception as e:
            print(f"[MarketService] Error get_live_price({symbol}): {e} \n")
            return None

    def get_orderbook(self, symbol: str, limit: int = 20):
        try:
            r = requests.get(
                f"{self.client.API_URL}/v3/depth?symbol={symbol}&limit={limit}"
            )
            r.raise_for_status()
            return r.json()  # contain bids/asks
        except Exception as e:
            logging.error(f"[MarketService] get_orderbook error: {e}")
            return None

    def get_fee(self, symbol: str):
        try:
            fees = self.client.get_trade_fee()
            # for f in fees:
            #     if f["symbol"] == symbol:
            #         return {
            #             "maker": float(f["makerCommission"]),
            #             "taker": float(f["takerCommission"]),
            #         }
            return fees
        except Exception as e:
            logging.error(f"[MarketService] get_fee error: {e}")
            return None

    def get_klines(self, symbol: str, interval: str = "1m", limit: int = 200):
        try:
            # pakai Binance python client
            klines = self.client.get_klines(
                symbol=symbol, interval=self.client.KLINE_INTERVAL_1DAY
            )

            print("total klines 1d : ", len(klines))

            # format: [open_time, open, high, low, close, volume, ...]
            closes = [float(k[4]) for k in klines]
            return closes

        except Exception as e:
            logging.error(f"[MarketService] get_klines error: {e}")
            return None
