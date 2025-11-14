from typing import Literal
from pydantic import BaseModel, Field
from schemas.bot_enum import BotStatus


class GridTradingConfig(BaseModel):
    strategy: Literal["grid-trading"] = "grid-trading"
    ticker: str
    grid_spacing_pct: float = Field(..., gt=0, description="Grid Spacing percentage")
    num_grids: int = Field(10, gt=0)


class MeanReversalConfig(BaseModel):
    strategy: Literal["mean-reversal"] = "mean-reversal"
    ticker: str
    moving_average_period: int = Field(20, gt=0)
    std_dev_multiplier: float = Field(2.0, gt=0)


class BreakoutMomentumConfig(BaseModel):
    strategy: Literal["breakout-moment"] = "breakout-moment"
    ticker: str
    lookback_period: int = Field(50, gt=0)
    volume_threshold: float = Field(1000.0, gt=0)
