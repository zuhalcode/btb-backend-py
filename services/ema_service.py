import numpy as np
import pandas as pd

from services.data import DataService
from services.indicator_cache_service import IndicatorCacheService
from services.indicator_service import IndicatorService


class EMAService:
    _cache = None
    _full_close = None

    @classmethod
    def init(cls):
        full_df = DataService.get_df_1h()  # HARUS FULL DATASET
        full_df["open_time"] = pd.to_datetime(full_df["open_time"])

        cls._cache = IndicatorCacheService(
            close=full_df["close"].values,
            high=full_df["high"].values,
            low=full_df["low"].values,
            volume=full_df["volume"].values,
        )

        cls._full_time = full_df["open_time"].values

        print("EMAService INIT OK")
        print("LEN close:", len(cls._cache.close))
        print("LEN time :", len(cls._full_time))

    @classmethod
    def ema_tuning(cls, ema_fast: int, ema_slow: int):

        # ✅ AUTO INIT JIKA BELUM ADA
        if cls._cache is None:
            cls.init()

        train_df = DataService.get_train()
        idx = train_df.index.values

        ema_f = EMAService._cache.get_ema(ema_fast)[idx]
        ema_s = EMAService._cache.get_ema(ema_slow)[idx]

        closes = train_df["close"].values
        open_time = train_df["open_time"].values

        cross = ema_f - ema_s
        cross_prev = np.roll(cross, 1)
        cross_prev[0] = 0.0

        buy = (cross_prev < 0) & (cross > 0)
        sell = (cross_prev > 0) & (cross < 0)

        return {
            "close": closes,
            "open_time": open_time,
            "buy": buy,
            "sell": sell,
        }

    @classmethod
    def ema_tuning_subset(cls, ema_fast: int, ema_slow: int, start_date, end_date):

        # ✅ AUTO INIT
        if cls._cache is None:
            cls.init()

        start_date = (
            start_date.tz_localize(None)
            if start_date.tzinfo is not None
            else start_date
        )

        end_date = (
            end_date.tz_localize(None) if end_date.tzinfo is not None else end_date
        )

        full_time = cls._full_time  # FULL index
        mask = (full_time >= start_date) & (full_time <= end_date)

        if mask.sum() < 50:
            print("SKIPPED: block too small")
            return None

        ema_f_full = cls._cache.get_ema(ema_fast)
        ema_s_full = cls._cache.get_ema(ema_slow)

        ema_f = ema_f_full[mask]
        ema_s = ema_s_full[mask]

        closes = cls._cache.close[mask]
        open_time = full_time[mask]

        # ✅ SIGNAL
        cross = ema_f - ema_s
        cross_prev = np.roll(cross, 1)
        cross_prev[0] = 0.0

        buy = (cross_prev < 0) & (cross > 0)
        sell = (cross_prev > 0) & (cross < 0)

        return {
            "close": closes,
            "open_time": open_time,
            "buy": buy,
            "sell": sell,
        }

    @staticmethod
    def regime_detection():
        df = DataService.get_train()

        print(len(df))
        print(df.tail(5))

        # =========================================================
        # 1️⃣ DEFINISI RETURN (LOG RETURN)
        # r_t = ln(P_t / P_{t-1})
        # =========================================================
        df["log_return"] = np.log(df["close"] / df["close"].shift(1))
        df = df.dropna()

        # =========================================================
        # 2️⃣ ESTIMASI TREND (DRIFT) VIA EMA SLOPE
        # EMA_t = alpha * P_t + (1-alpha) * EMA_{t-1}
        # slope = (EMA_t - EMA_{t-k}) / k
        # slope_norm = slope / P_t
        # =========================================================
        EMA_LEN = 200
        SLOPE_WIN = 20

        df["ema200"] = IndicatorService.ema_series(df["close"], EMA_LEN)
        df["ema_slope"] = (df["ema200"] - df["ema200"].shift(SLOPE_WIN)) / SLOPE_WIN
        df["ema_slope_norm"] = df["ema_slope"] / df["close"]

        # =========================================================
        # 3️⃣ ESTIMASI VOLATILITY VIA ATR NORMALIZED
        # ATR_t = mean(TR)
        # nVol = ATR / Close
        # =========================================================
        ATR_LEN = 14
        # Siapkan OHLC untuk ATR
        prices = [
            {"high": h, "low": l, "close": c}
            for h, l, c in zip(df["high"], df["low"], df["close"])
        ]

        df["atr"] = IndicatorService.atr_series(prices, ATR_LEN)

        df["nvol"] = df["atr"] / df["close"]

        # =========================================================
        # 4️⃣ THRESHOLD BERBASIS DISTRIBUSI TRAINING (ANTI LEAKAGE)
        # theta_mu  = Q(|slope|)
        # theta_vol = Q(nvol)
        # =========================================================
        theta_mu = df["ema_slope_norm"].abs().quantile(0.70)
        theta_vol = df["nvol"].quantile(0.70)

        # =========================================================
        # 5️⃣ KLASIFIKASI TREND (BULL / BEAR / SIDE)
        # =========================================================
        df["trend"] = np.where(
            df["ema_slope_norm"] > theta_mu,
            "bull",
            np.where(df["ema_slope_norm"] < -theta_mu, "bear", "sideways"),
        )

        # =========================================================
        # 6️⃣ KLASIFIKASI VOLATILITY (HIGH / LOW)
        # =========================================================
        df["vol"] = np.where(df["nvol"] > theta_vol, "high", "low")

        # =========================================================
        # 7️⃣ FUSI MENJADI 6 REGIME FINAL
        # Regime = Trend × Vol
        # =========================================================
        df["regime"] = df["trend"] + "_" + df["vol"]

        # =========================================================
        # 8️⃣ BERSIHKAN DATA AWAL (NaN DARI EMA/ATR)
        # =========================================================
        df = df.dropna().reset_index(drop=True)

        # =========================================================
        # 9️⃣ RINGKASAN DISTRIBUSI REGIME (OPSIONAL, UNTUK DEBUG)
        # =========================================================
        regime_dist = df["regime"].value_counts(normalize=True)
        print(regime_dist)

        # 1. Deteksi perubahan regime antar bar
        df["regime_change"] = df["regime"] != df["regime"].shift()

        # 2. Nomor blok fase
        df["regime_block"] = df["regime_change"].cumsum()

        # 3. Rekap per BLOK KONTINU
        regime_blocks = (
            df.groupby(["regime_block", "regime"])["open_time"]
            .agg(start="min", end="max", count="size")
            .reset_index()
        )

        regime_blocks.to_csv("train_with_regime.csv", index=False)

        print(regime_blocks.tail(20))

        return df
