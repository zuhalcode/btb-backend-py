from binance.client import Client
from libs.supabase import supabase
from libs.env import (
    BINANCE_API_KEY,
    BINANCE_API_SECRET,
    BINANCE_API_URL_TESTNET,
    BINANCE_API_URL,
)

from datetime import datetime, timezone
from services.bot_session_service import BotSessionService
from dtos.bot_dto import BotResponseDTO, BotCreateDTO, BotUpdateDTO
from dtos.bot_session_dto import BotSessionStatus as Status

import requests
import time
import asyncio
import threading


class BotService:
    _table = "bots"
    _is_running = {}

    def __init__(self, testnet: bool = True):
        self.testnet = testnet
        self.client = Client(BINANCE_API_KEY, BINANCE_API_SECRET, testnet=testnet)
        self.client.REQUEST_RECVWINDOW = 5000
        self.client.API_URL = BINANCE_API_URL_TESTNET if testnet else BINANCE_API_URL

    # CRUD
    @staticmethod
    def find_all() -> list[BotResponseDTO]:
        try:
            result = (
                supabase.table(BotService._table)
                .select("id, name, config, status, created_at")
                .order("created_at", desc=True)
                .execute()
            )

            return result.data

        except Exception as e:
            print("Error in retrieve data:", str(e))
            raise e

    @staticmethod
    def find_one(id: str) -> BotResponseDTO:
        try:
            response = (
                supabase.table(BotService._table)
                .select("id, name, symbol, timeframe, config, created_at, updated_at")
                .eq("id", id)
                .execute()
            )

            data = response.data[0]

            return data

        except Exception as e:
            print("Error in retrieve data:", str(e))
            raise e

    @staticmethod
    def create(payload: BotCreateDTO) -> list[BotResponseDTO]:
        try:
            result = supabase.table(BotService._table).insert(payload).execute()
            return result.data

        except Exception as e:
            print("Error creating Bot:", e)
            raise e

    @staticmethod
    def update(id: str, payload: BotUpdateDTO) -> list[BotResponseDTO]:
        try:

            # ✅ Pastikan bot dengan ID tersebut ada
            existing = (
                supabase.table(BotService._table)
                .select("id")
                .eq("id", id)
                .limit(1)
                .execute()
            )

            if not existing.data:
                raise ValueError(f"Bot with id '{id}' not found")

            result = (
                supabase.table(BotService._table).update(payload).eq("id", id).execute()
            )

            return result.data

        except Exception as e:
            print("Error updating Bot:", e)
            raise e

    @staticmethod
    def delete(id: str) -> list[BotResponseDTO]:
        try:
            # ✅ Pastikan ID dikirim
            if not id:
                raise ValueError("Bot ID is required for deletion")

            # ✅ Cek apakah bot dengan ID tersebut ada
            existing = (
                supabase.table(BotService._table)
                .select("id")
                .eq("id", id)
                .limit(1)
                .execute()
            )

            if not existing.data:
                raise ValueError(f"Bot with id '{id}' not found")

            result = supabase.table(BotService._table).delete().eq("id", id).execute()
            return result.data

        except Exception as e:
            print("Error deleting Bot:", e)
            raise e

    # Bot Control
    def check_connection(self):
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

    @staticmethod
    def start(id: str):
        try:
            session = None

            # 1. Ambil bot
            bot = BotService.find_one(id)

            if not bot:
                raise ValueError(f"Bot {id} not found")

            # 2️⃣ Cek session terakhir ambil yg status = idle
            last_session = BotSessionService.find_one_by_bot_id_and_status(
                id, Status.IDLE
            )

            session = last_session or BotSessionService.create(id)

            if session and session["status"] == Status.RUNNING:
                raise ValueError(f"Bot {id} is already running")

            # 3️⃣ Update status ke running
            if session["status"] == Status.IDLE:
                session = BotSessionService.update(
                    session["id"],
                    {
                        "status": Status.RUNNING,
                        "start_time": datetime.now(timezone.utc).isoformat(),
                    },
                )

            # 🔥 Jalankan loop realtime di background
            BotService.run(bot, session)

            # 5. Return
            return {"session": session, "bot": bot}

        except Exception as e:
            print("Bot starting error : ", e)
            raise e

    @staticmethod
    def run(bot: dict):
        try:
            bot_id = bot["id"]

            # kalau sudah running, abaikan
            if BotService._is_running.get(bot_id):
                print(f"Bot {bot_id} is running")
                return

            BotService._is_running[bot_id] = True
            print("List bot running : ", BotService._is_running)

            def loop():
                print(f"[{bot_id}] starting real-time loop...")
                while BotService._is_running.get(bot_id, False):

                    # cek status di DB (fail-safe)
                    current_session = BotSessionService.find_one_by_status(
                        bot_id, Status.RUNNING
                    )

                    if not current_session:
                        print(f"[{bot_id}] no running session, stop loop.")
                        break

                    print(f"[{bot['name']}] is running... ")

                    # jalankan logika utama (misal: ambil harga, evaluasi, entry/exit)
                    # BotEventService.record_event(bot_id, "tick", "executed one cycle")

                    time.sleep(1)

                print(f"[{bot_id}] stopped loop.")

            thread = threading.Thread(target=loop, daemon=True)
            thread.start()

        except Exception as e:
            print("Error running Bot : ", e)
            raise e

    @staticmethod
    def stop(id: str):
        try:
            BotService._is_running[id] = False
            session = BotSessionService.find_one_by_bot_id_and_status(
                id, Status.RUNNING
            )

            if not session:
                raise ValueError(f"No running session found for bot {id}")

            start_time = datetime.fromisoformat(session["start_time"])
            end_time = datetime.now(timezone.utc)
            uptime_seconds = int((end_time - start_time).total_seconds())

            bot_stopped = BotSessionService.update(
                session["id"],
                {
                    "status": Status.STOPPED,
                    "end_time": end_time.isoformat(),
                    "uptime_seconds": uptime_seconds,
                },
            )

            return bot_stopped

        except Exception as e:
            print("Error Stopping Bot : ", e)
            raise e
