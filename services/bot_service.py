from typing import Optional
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
from services.market_service import MarketService

from dtos.bot_dto import BotResponseDTO, BotCreateDTO, BotUpdateDTO, BotStatus
from dtos.bot_session_dto import BotSessionStatus as SessionStatus

import requests
import time
import threading


class BotService:
    _table = "bots"
    _is_running = {}

    def __init__(self, testnet: bool = True):
        self.testnet = testnet
        self.client = Client(BINANCE_API_KEY, BINANCE_API_SECRET, testnet=testnet)
        self.client.REQUEST_RECVWINDOW = 5000
        self.client.API_URL = BINANCE_API_URL_TESTNET if testnet else BINANCE_API_URL

    # Private Method
    @staticmethod
    def _change_status(id: str, target_status: BotStatus):
        try:
            bot = BotService.find_one(id)
            if not bot:
                raise ValueError(f"Bot {id} not found")

            # Cari sesi yang sedang RUNNING untuk bot ini
            running_session = BotSessionService.find_one_by_bot_id_and_status(
                id, SessionStatus.RUNNING
            )

            # Jika ada sesi RUNNING
            if running_session:
                raise ValueError(
                    f"Cannot change status '{bot['name'].capitalize()}'. "
                    f"It is currently running on session {running_session['id']}."
                )

            # 2. 🚦 Pengecekan Status Sama
            current_status = bot["status"]
            if current_status == target_status:
                # Gunakan capitalize untuk format pesan yang baik
                status_name = target_status.value

                # Melempar error karena status sudah sesuai target
                raise ValueError(
                    f"{bot['name'].capitalize()} is already {status_name}. Status change aborted."
                )

            # 3. Lanjutkan proses update jika status berbeda
            return BotService.update(id, {"status": target_status})
        except Exception as e:
            print("Error changing Bot Status : ", e)
            raise e

    ##### CRUD #

    @staticmethod
    def find_all() -> list[BotResponseDTO]:
        try:
            result = (
                supabase.table(BotService._table)
                .select("*")
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
                supabase.table(BotService._table).select("*").eq("id", id).execute()
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

    # CRUD #####

    ##### Bot Control #

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

            # 2️⃣ Cek apakah bot sudah ACTIVE
            if bot["status"] != BotStatus.ACTIVE:
                raise ValueError(f"Bot {id} is not active. Please activate it first.")

            # 3️⃣ PRIORITAS: Cek apakah SUDAH ADA sesi yang RUNNING
            running_session = BotSessionService.find_one_by_bot_id_and_status(
                id, SessionStatus.RUNNING
            )

            if running_session:
                raise ValueError(
                    f"{bot['name'].capitalize()} is already running on session {running_session['id']}"
                )

            # 2️⃣ Cek session terakhir ambil yg status = idle
            last_session = BotSessionService.find_one_by_bot_id_and_status(
                id, SessionStatus.IDLE
            )

            session = last_session or BotSessionService.create(id)

            if session and session["status"] == SessionStatus.RUNNING:
                raise ValueError(f"Bot {id} is already running")

            # 3️⃣ Update status ke running
            if session["status"] == SessionStatus.IDLE:
                session = BotSessionService.update(
                    session["id"],
                    {
                        "status": SessionStatus.RUNNING,
                        "start_time": datetime.now(timezone.utc).isoformat(),
                    },
                )

            # 🔥 Jalankan loop realtime di background
            BotService.run(bot)

            # 5. Return
            return {"session": session, "bot": bot}

        except Exception as e:
            print("Bot starting error : ", str(e))
            raise e

    @staticmethod
    def run(bot: dict):
        try:
            bot_id = bot["id"]
            config = bot.get("config", {})
            print(config)

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
                        bot_id, SessionStatus.RUNNING
                    )

                    if not current_session:
                        print(f"[{bot_id}] no running session, stop loop.")
                        break

                    print(f"[{bot['name']}] is running... ")

                    # Jalankan get live price disini
                    # live_price = market_service.get_live_price()

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
                id, SessionStatus.RUNNING
            )

            if not session:
                raise ValueError(f"No running session found for bot {id}")

            start_time = datetime.fromisoformat(session["start_time"])
            end_time = datetime.now(timezone.utc)
            uptime_seconds = int((end_time - start_time).total_seconds())

            bot_stopped = BotSessionService.update(
                session["id"],
                {
                    "status": SessionStatus.STOPPED,
                    "end_time": end_time.isoformat(),
                    "uptime_seconds": uptime_seconds,
                },
            )

            return bot_stopped

        except Exception as e:
            print("Error Stopping Bot : ", e)
            raise e

    @staticmethod
    def force_stop_all_running_sessions():
        """Menghentikan secara paksa semua sesi yang berstatus RUNNING saat shutdown."""
        print(
            "\n[SHUTDOWN HOOK] Initiating force stop and cleanup for all active bots..."
        )

        # 1. Hentikan flag in-memory untuk semua bot yang sedang berjalan
        for bot_id in BotService._is_running:
            BotService._is_running[bot_id] = False
            print(f"[{bot_id}] Flag in-memory set to False.")

        # 2. Update semua sesi RUNNING di DB menjadi ERROR/STOPPED (penting!)
        try:
            BotSessionService.force_stop()
            print("✅ Database cleanup: All RUNNING sessions marked as FORCE_STOP.")
        except Exception as e:
            print(f"❌ Database cleanup failed: {e}")

    # Bot Control #####
