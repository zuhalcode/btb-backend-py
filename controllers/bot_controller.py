import asyncio

from fastapi import (
    HTTPException,
    Request,
    WebSocket,
    WebSocketDisconnect,
    HTTPException,
    Request,
)

from services.trading_service import TradingService
from services.bot import BotService
from services.market_service import MarketService

from managers.bot_manager import BotManager

from fastapi.responses import JSONResponse
from utils.response import ResponseHandler
from dtos.bot_dto import BotCreateDTO, BotUpdateDTO, BotStatus


class BotController:

    # CRUD
    def find_all() -> JSONResponse:
        try:
            result = BotService.find_all()
            return ResponseHandler.success(result, "Bot Retrieved Successfully")
        except Exception as e:
            return ResponseHandler.error(e, "Retrieve Bot data failed")

    async def find_one(id: str) -> JSONResponse:
        try:
            result = await BotService.find_one(id)
            return ResponseHandler.success(result, "Bot Retrieved Successfully")
        except Exception as e:
            return ResponseHandler.error(e, "Retrieve Bot data failed")

    async def create(req: Request) -> JSONResponse:
        try:
            body = await req.json()
            payload = BotCreateDTO(**body).model_dump()
            result = BotService.create(payload)
            return ResponseHandler.success(result, "New Bot created successfully")

        except Exception as e:
            return ResponseHandler.error(e, "Create new Bot Failed")

    async def update(id: str, req: Request) -> JSONResponse:
        try:
            body = await req.json()
            payload = BotUpdateDTO(**body).model_dump(exclude_unset=True)
            result = BotService.update(id, payload)
            return ResponseHandler.success(result, "Updated Bot Successfullt")

        except Exception as e:
            return ResponseHandler.error(e, "Update Bot data failed")

    async def delete(id: str) -> JSONResponse:
        try:
            result = BotService.delete(id)
            return ResponseHandler.success(result, "Bot Deleted Successfully")
        except Exception as e:
            return ResponseHandler.error(e, "Delete Bot Failed")

    # Bot Control
    def check_connection():
        try:
            worker = BotManager.get()

            if worker is None:
                return ResponseHandler.error(None, "No bot worker running")

            result = worker.service.check_connection()
            return ResponseHandler.success(result, "Binance connection OK")

        except Exception as e:
            return ResponseHandler.error(e, "Failed to connect to Binance")

    def activate(id: str) -> JSONResponse:
        try:
            worker = BotManager.get()

            if worker is None:
                return ResponseHandler.error(None, "No bot worker running")

            result = worker.service.change_status(id, BotStatus.ACTIVE)
            return ResponseHandler.success(result, "Bot activated Successfully")
        except Exception as e:
            return ResponseHandler.error(e, "Bot activated Failure")

    def deactivate(id: str) -> JSONResponse:
        try:
            worker = BotManager.get()

            if worker is None:
                return ResponseHandler.error(None, "No bot worker running")

            result = worker.service.change_status(id, BotStatus.INACTIVE)
            return ResponseHandler.success(result, "Bot deactivated Successfully")
        except Exception as e:
            return ResponseHandler.error(e, "Bot deactivated Failure")

    def start(id: str) -> JSONResponse:
        try:
            worker = BotManager.get()

            if worker is None:
                return ResponseHandler.error(None, "No bot worker running")

            bot_data = worker.service.start(id)

            if not bot_data:
                return ResponseHandler.error(None, f"Bot with id {id} not found")

            return ResponseHandler.success(bot_data, "Bot Started Successfully")
        except Exception as e:
            return ResponseHandler.error(e, "Bot Starting failed")

    def stop(id: str) -> JSONResponse:
        try:
            worker = BotManager.get()

            if worker is None:
                return ResponseHandler.error(None, "No bot worker running")

            bot_data = worker.service.stop(id)

            if not bot_data:
                return ResponseHandler.error(None, f"Bot with id {id} not found")

            return ResponseHandler.success(bot_data, "Bot Stopped Successfully")
        except Exception as e:
            return ResponseHandler.error(e, "Bot Stopping failed")

    # Grid Strategy
    async def start_grid_trading(req: Request):
        try:
            bot = TradingService.get_instance()
            if bot is not None:
                raise HTTPException(status_code=400, detail="Bot Already Running")

            # Inisialisasi bot baru
            bot = TradingService()
            TradingService.set_instance(bot)

            # cek koneksi Binance
            connection_status = await bot.check_connection()
            if connection_status.get("status") != "connected":
                TradingService.set_instance(None)
                raise HTTPException(
                    status_code=500, detail="Failed to connect to Binance"
                )

            # mulai trading loop (async placeholder)
            result = await bot.start_grid_trading()

            # return response sukses
            return ResponseHandler.success(result, "Trading started successfully")

        except Exception as e:
            return ResponseHandler.error(e, "Failed to start trading")

    async def stop_grid_trading(req: Request, timeout: float = 5.0):
        try:
            bot = TradingService.get_instance()
            if bot is None:
                raise HTTPException(status_code=400, detail="No trading bot is running")

            # hentikan loop trading dengan timeout
            try:
                result = await asyncio.wait_for(
                    bot.stop_grid_trading(), timeout=timeout
                )

            except asyncio.TimeoutError:
                # kalau timeout terjadi, paksa stop task
                if bot._task:
                    bot._task.cancel()
                result = {"status": "stopped_with_timeout"}

            # hapus global instance supaya bisa start ulang
            TradingService.set_instance(None)

            return ResponseHandler.success(result, "Trading stopped successfully")

        except Exception as e:
            return ResponseHandler.error(e, "Failed to stop trading")

    # ===========================
    # 🔌 WEBSOCKET HANDLER
    # ===========================

    @staticmethod
    async def websocket_trading(ws: WebSocket):
        await ws.accept()
        bot = TradingService.get_instance()
        if bot is None:
            await ws.send_json({"error": "No bot instance running"})
            await ws.close()
            return

        try:
            while True:
                snapshot = bot.get_snapshot()  # ambil state terbaru
                await ws.send_json(snapshot)
                await asyncio.sleep(1)  # interval 1 detik
        except WebSocketDisconnect:
            print("Client disconnected")
        except Exception as e:
            print("WS error:", e)
            await ws.close()
