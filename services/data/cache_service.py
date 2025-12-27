from .data_service import DataService
from services.indicator_service import IndicatorService


class CacheService:
    _ema_cache = None

    @classmethod
    def get_ema_cache(cls):
        # Jika sudah pernah dihitung, langsung return
        if cls._ema_cache is not None:
            return cls._ema_cache

        df = DataService.df_1h  # ambil close dari DF master
        closes = df["close"]

        # Precompute 1–100 EMA sekali saja
        cls._ema_cache = {
            n: IndicatorService.ema_series(closes, n) for n in range(1, 101)
        }

        return cls._ema_cache
