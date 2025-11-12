from typing import Any, Optional
from pydantic import BaseModel
from schemas.bot_enum import BotStatus


class BotDTO(BaseModel):
    name: str
    status: BotStatus
    config: Optional[Any] = {}


class BotCreateDTO(BotDTO):
    pass


class BotUpdateDTO(BaseModel):
    name: Optional[str]
    status: Optional[str]
    config: Optional[Any]


class BotResponseDTO(BotDTO):
    id: str
