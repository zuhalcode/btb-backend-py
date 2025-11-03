# controllers/trading_controller.py
from fastapi import (
    HTTPException,
    Request,
    WebSocket,
    WebSocketDisconnect,
    HTTPException,
    Request,
)
from services.trading_service import TradingService

from utils.response import ResponseHandler

import asyncio


class TradingController:
    async def check_connection(req: Request):
        try:
            temp_bot = TradingService()
            result = await temp_bot.check_connection()
            return ResponseHandler.success(result, "Binance connection OK")

        except Exception as e:
            return ResponseHandler.error(e, "Failed to connect to Binance")

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
