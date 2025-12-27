import numpy as np
from services.indicator_service import IndicatorService


class IndicatorCacheService:
    def __init__(
        self,
        close: np.ndarray,
        high: np.ndarray | None = None,
        low: np.ndarray | None = None,
        volume: np.ndarray | None = None,
    ):
        # ===== RAW ARRAYS (PERMANENT) =====
        self.close = close.astype(float)
        self.high = high.astype(float) if high is not None else None
        self.low = low.astype(float) if low is not None else None
        self.volume = volume.astype(float) if volume is not None else None

        # ===== INDICATOR CACHES (LAZY) =====
        self._ema_cache = {}
        self._sma_cache = {}
        self._atr_cache = {}
        # future:
        # self._rsi_cache = {}
        # self._adx_cache = {}
        # self._macd_cache = {}

    # ================= EMA =================
    def get_ema(self, period: int):
        if period not in self._ema_cache:
            self._ema_cache[period] = np.asarray(
                IndicatorService.ema_series(self.close, period, use_ema_seed=True),
                dtype=float,
            )
        return self._ema_cache[period]

    # ================= ATR =================
    def get_atr(self, period: int):
        if period not in self._atr_cache:
            atr = IndicatorService.atr_series(self.prices, length=period)
            self._atr_cache[period] = np.asarray(atr, dtype=float)

        return self._atr_cache[period]

    # ================= SMA =================
    def get_sma(self, period: int):
        if period not in self._sma_cache:
            self._sma_cache[period] = np.asarray(
                IndicatorService.ma_series(self.series, period),
                dtype=float,
            )

        return self._sma_cache[period]

    # ================= RESET =================
    def reset(self):
        if self._ema_cache is not None:
            self._ema_cache.clear()
        if self._atr_cache is not None:
            self._atr_cache.clear()
        if self._sma_cache is not None:
            self._sma_cache.clear()
