from binance.client import Client
from libs.supabase import supabase
from libs.env import (
    BINANCE_API_KEY,
    BINANCE_API_SECRET,
    BINANCE_API_URL_TESTNET,
    BINANCE_API_URL,
)

from services.bot_action_service import BotActionService
from dto.bot_dto import BotResponseDTO, BotCreateDTO, BotUpdateDTO

import requests
import time
import asyncio


class BotEventService:
    _a = 0
