from typing import Any, Optional
from pydantic import BaseModel, Field
from schemas.bot_enum import BotStatus


class BotConfig(BaseModel):
    symbol: str = Field(..., description="Pair like BTCUSDT")
    initial_price: float = Field(..., gt=0)
    grid_spacing_pct: float = Field(..., gt=0, description="Grid Spacing percentage")
    fee_rate: float = Field(0.001, ge=0)
    entry_alloc: float = Field(0.1, ge=0, le=1)
    num_grids: int = Field(10, gt=0)
    budget: float = Field(70, gt=0)


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
