import asyncio
from workers.bot_worker import BotWorker


async def run():
    worker = BotWorker()
    await worker.start()


if __name__ == "__main__":
    asyncio.run(run())
