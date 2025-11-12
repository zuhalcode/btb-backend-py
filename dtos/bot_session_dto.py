from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel
from datetime import datetime


class BotSessionStatus(str, Enum):
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    IDLE = "IDLE"
    CRASHED = "CRASHED"

    def __str__(self):
        return self.value


class BotSessionDTO(BaseModel):
    bot_id: str
    status: str = "idle"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    uptime_seconds: Optional[int] = None
    error_message: Optional[str] = None


class BotSessionCreateDTO(BaseModel):
    bot_id: str
    status: Optional[str] = "idle"
    start_time: Optional[datetime] = None


class BotSessionUpdateDTO(BaseModel):
    status: Optional[BotSessionStatus]
    end_time: Optional[datetime]
    uptime_seconds: Optional[int]
    error_message: Optional[str]


class BotSessionResponseDTO(BotSessionDTO):
    id: str
