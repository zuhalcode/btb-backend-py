from binance.client import Client
from libs.env import BINANCE_API_KEY, BINANCE_API_SECRET
from services.bot_action_service import BotActionService

import requests
import time
import asyncio


class TradingService:
    _trading_instance = None  # single bot

    def __init__(self, symbol: str = "BTCUSDT", testnet: bool = True):
        self.symbol = symbol
        self.asset = symbol.replace("USDT", "")

        self.current_price = 0
        self.stable = "USDT"

        self.balances = {
            self.asset: {"free": 0.0, "locked": 0.0},
            self.stable: {"free": 0.0, "locked": 0.0},
        }

        self.testnet = testnet

        self.client = Client(BINANCE_API_KEY, BINANCE_API_SECRET, testnet=testnet)
        self.client.REQUEST_RECVWINDOW = 60000

        self.is_running = False
        self._task: asyncio.Task | None = None

        self.action = BotActionService(self.client, self.symbol)

        if self.testnet:
            self.client.API_URL = "https://testnet.binance.vision/api"
        else:
            self.client.API_URL = "https://api.binance.com/api"

    @classmethod
    def get_instance(cls):
        return cls._trading_instance

    @classmethod
    def set_instance(cls, instance):
        cls._trading_instance = instance

    # Bot Execution
    async def _grid_trading_loop(self):
        try:
            while self.is_running:
                print(f"Bot is Running : {self.is_running}")
                try:
                    await asyncio.gather(
                        self._update_current_price(),
                        self._update_balance(),
                    )
                    await asyncio.sleep(5)

                except Exception as e:
                    print("Trading Failed :", e)

                for _ in range(5):
                    if not self.is_running:
                        break
                    await asyncio.sleep(1)
        except asyncio.CancelledError:
            print("Bot task cancelled")

    async def check_connection(self):
        """Cek koneksi dan waktu server Binance"""
        try:
            ping = requests.get(f"{self.client.API_URL}/v3/ping", timeout=5)
            server_time = requests.get(f"{self.client.API_URL}/v3/time", timeout=5)
            ping.raise_for_status()
            server_time.raise_for_status()
            st = server_time.json()

            local_ts = int(time.time() * 1000)
            offset_ms = st["serverTime"] - local_ts

            if ping.status_code == 200 and server_time.status_code == 200:
                st = server_time.json()
                local_ts = int(time.time() * 1000)
                offset_ms = st["serverTime"] - local_ts

                result = {
                    "status": "connected",
                    "testnet": self.testnet,
                    "ping_status": ping.status_code,
                    "serverTime": st["serverTime"],
                    "localTime": local_ts,
                    "offset_ms": offset_ms,
                }
            else:
                result = {
                    "status": "disconnected",
                    "testnet": self.testnet,
                    "ping_status": ping.status_code,
                    "server_status": server_time.status_code,
                }

            return result

        except Exception as e:
            print("❌ Connection check failed:", e)
            raise e

    async def start_grid_trading(self):
        self.is_running = True

        self._task = asyncio.create_task(self._grid_trading_loop())

        result = {"status": "started", "symbol": self.symbol}
        return result

    async def stop_grid_trading(self):
        self.is_running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        self._task = None
        return {"status": "stopped", "running": self.is_running}

    def get_snapshot(self):
        return {
            "symbol": self.symbol,
            "current_price": self.current_price,
            "balances": self.balances,
            "running": self.is_running,
        }

    # Trading Execution
    async def _update_current_price(self):
        try:
            price = await self.action.get_current_price()
            self.current_price = price
        except Exception as e:
            print("[ERROR] get_current_price:", e)

    async def _update_balance(self):
        try:
            account_data = await self.action.get_balance()
            self.balances = self._format_balances(account_data)
        except Exception as e:
            print("[ERROR] get_balance:", e)

    # Clean Format Data
    def _format_balances(self, raw_account_data):
        try:
            balances = raw_account_data.get("account", {}).get("balances", [])
            assets_needed = {self.asset, self.stable}
            simplified = {}

            for b in balances:
                asset = b["asset"]
                if asset in assets_needed:
                    simplified[asset] = {
                        "free": float(b.get("free", 0)),
                        "locked": float(b.get("locked", 0)),
                    }

            # fallback kalau salah satu gak ketemu
            for a in assets_needed:
                simplified.setdefault(a, {"free": 0.0, "locked": 0.0})

            return simplified
        except Exception as e:
            print("[ERROR] extract balance:", e)
            return {}
