from pydantic import BaseModel


class StartTradingRequest(BaseModel):
    symbol: str = "ETHUSDT"
    budget: float = 1000
    entry_alloc: float = 1
    grid_spacing_pct: float = 0.01
    num_grids: int = 10
    fee_rate: float = 0.1
    profit_target_pct: float = 7
