from fastapi import FastAPI, WebSocket
from routes.api import router as trading_router
from routes.ws import router as ws_router

app = FastAPI(title="Testnet Grid Trading API")

# Masukkan router
app.include_router(trading_router)
app.include_router(ws_router)
