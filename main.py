from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.api import router as trading_router
from routes.ws import router as ws_router
from managers.bot_manager import BotManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ===== STARTUP =====
    BotManager.create()

    yield

    # ===== SHUTDOWN =====
    BotManager.stop()


app = FastAPI(title="Testnet Grid Trading API", lifespan=lifespan)

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
