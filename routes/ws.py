# routes/ws.py (WebSocket)
from fastapi import APIRouter, WebSocket
from controllers.trading_controller import TradingController

router = APIRouter(prefix="/ws/trading")


@router.websocket("/account")
async def websocket_trading(ws: WebSocket):
    await TradingController.websocket_trading(ws)
