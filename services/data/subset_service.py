import numpy as np

from .data_service import DataService
from services.indicator_service import IndicatorService


class SubsetService:
    @staticmethod
    def subset_detection():
        print(f"\nUSE SUBSET DETECTION")

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
