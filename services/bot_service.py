import requests
import time
import logging
import multiprocessing

from libs.supabase import supabase

from datetime import datetime, timezone

from services.bot_session_service import BotSessionService
from services.market_service import MarketService
from services.indicator_service import IndicatorService
from services.data_loader_service import DataLoaderService
from services.backtest_service import BacktestService

from dtos.bot_dto import BotResponseDTO, BotCreateDTO, BotUpdateDTO, BotStatus
from dtos.bot_session_dto import BotSessionStatus as SessionStatus


class BotService:
    _table = "bots"
    _is_running = {}
    _processes = {}

    def __init__(self, market_service: MarketService):
        self.market = market_service

    # Private Method
    @staticmethod
    def change_status(id: str, target_status: BotStatus):
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
            logging.info("Error changing Bot Status : ", e)
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
            logging.info(f"Error in retrieve data: {str(e)}")
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
            logging.info(f"Error in retrieve data: {str(e)}")
            raise e

    @staticmethod
    def create(payload: BotCreateDTO) -> list[BotResponseDTO]:
        try:
            result = supabase.table(BotService._table).insert(payload).execute()
            return result.data

        except Exception as e:
            logging.info("Error creating Bot:", e)
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
            logging.info("Error updating Bot:", e)
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
            logging.info("Error deleting Bot:", e)
            raise e

    # CRUD #####

    ##### Bot Control #

    def check_connection(self):
        binance = self.market_service
        try:
            ping = requests.get(f"{binance.client.API_URL}/v3/ping", timeout=5)
            server_time = requests.get(f"{binance.client.API_URL}/v3/time", timeout=5)
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
                    "testnet": binance.testnet,
                    "ping_status": ping.status_code,
                    "serverTime": st["serverTime"],
                    "localTime": local_ts,
                    "offset_ms": offset_ms,
                }
            else:
                result = {
                    "status": "disconnected",
                    "testnet": binance.testnet,
                    "ping_status": ping.status_code,
                    "server_status": server_time.status_code,
                }

            return result

        except Exception as e:
            logging.info("❌ Connection check failed:", e)
            raise e

    def start(self, id: str):
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
            self.run(bot)

            # 5. Return
            return {"session": session}

        except Exception as e:
            logging.error("Bot starting error bro : %s", e)
            raise e

    def run(self, bot: dict):
        try:
            bot_id = bot.get("id")
            config = bot.get("config", {})
            ticker = config["ticker"]
            bot_name = bot.get("name")

            if not ticker:
                logging.error(f"[{bot_id}] No ticker found")
                return

            if BotService._is_running.get(bot_id):
                logging.info(f"[{bot_id}] Already running")
                return

            BotService._is_running[bot_id] = True

            p = multiprocessing.Process(
                target=BotService._worker_process,
                args=(bot_id, ticker, bot_name),
                daemon=True,
            )
            p.start()

            BotService._processes[bot_id] = p
            logging.info(f"[{bot_id}] Worker process started")

        except Exception as e:
            logging.error("Error running Bot : %s", e)
            raise e

    @staticmethod
    def _worker_process(bot_id, ticker, bot_name):
        market = MarketService()
        df = BacktestService.test()

        logging.info(f"[{bot_id}] Worker running for {ticker}")

        while True:
            try:
                # live_price = market.get_live_price(ticker)
                # klines = market.get_klines(ticker)
                # print(f"[{bot_name} - {ticker}] price = {live_price} - EMA13 = {ema13}")
                # print(f"[{bot_name} - {ticker}]\nEMA13 = {ema13[-10:]}")
                logging.info(f"{bot_name}")
            except Exception as e:
                logging.error(f"[{bot_id}] Error: {e}")

            time.sleep(1)

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
                    "status": SessionStatus.IDLE,
                    "end_time": end_time.isoformat(),
                    "uptime_seconds": uptime_seconds,
                },
            )

            return bot_stopped

        except Exception as e:
            logging.error("Error Stopping Bot : %s", e)
            raise e

    # Bot Control #####
