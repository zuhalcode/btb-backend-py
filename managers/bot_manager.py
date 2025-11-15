# managers/bot_manager.py
import asyncio
import logging

from workers.bot_worker import BotWorker
from services.market_service import MarketService


class BotManager:
    _instance: BotWorker | None = None

    @classmethod
    def get(cls) -> BotWorker | None:
        return cls._instance

    @classmethod
    def create(cls) -> BotWorker:
        logging.info("[Server] Bot worker started")
        if cls._instance is None:
            cls._instance = BotWorker()
            asyncio.create_task(cls._instance.start())
        return cls._instance

    @classmethod
    def stop(cls):
        if cls._instance:
            cls._instance.stop()
            cls._instance = None
            logging.info("[Server] Bot worker stopped")
