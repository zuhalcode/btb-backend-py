import asyncio
import logging

from services.bot import BotService, BotSessionService
from services.market_service import MarketService

logging.basicConfig(level=logging.INFO)


class BotWorker:
    def __init__(self):
        self._stop_event = asyncio.Event()
        self.service = BotService(market_service=MarketService())

    async def start(self):
        logging.info("[Worker] running...")

        # ambil semua bot yang statusnya RUNNING
        running_bots = BotSessionService.find_all_running()

        for session in running_bots:
            bot = BotService.find_one(session["bot_id"])
            if bot:
                self.service.run(bot)

        # Logic Bot Here
        while not self._stop_event.is_set():
            await asyncio.sleep(0.5)

        logging.info("[Worker] Stopping...")
        logging.info("[Worker] Stopped cleanly...")

    def stop(self):
        logging.info("[Worker] Stop signal received...")
        self._stop_event.set()


async def main():
    worker = BotWorker()
    await worker.start()


if __name__ == "__main__":
    asyncio.run(main())
