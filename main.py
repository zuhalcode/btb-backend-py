from fastapi import FastAPI
from routes.api import router as trading_router
from routes.ws import router as ws_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Testnet Grid Trading API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Masukkan router
app.include_router(trading_router)
app.include_router(ws_router)
