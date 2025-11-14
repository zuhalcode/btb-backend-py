from typing import Any, Optional
from pydantic import BaseModel, Field
from schemas.bot_enum import BotStatus
from typing import Union

from schemas.strategy import (
    GridTradingConfig,
    MeanReversalConfig,
    BreakoutMomentumConfig,
)


StrategyConfig = Union[GridTradingConfig, MeanReversalConfig, BreakoutMomentumConfig]


class BotDTO(BaseModel):
    name: str
    capital: float = Field(70.0, ge=0, description="Modal awal, default 70.")
    status: BotStatus = Field(
        BotStatus.INACTIVE, description="Status operasional bot, default INACTIVE."
    )
    config: StrategyConfig


class BotCreateDTO(BotDTO):
    pass


class BotUpdateDTO(BaseModel):
    name: Optional[str]
    status: Optional[str]
    config: Optional[Any]


class BotResponseDTO(BotDTO):
    id: str
