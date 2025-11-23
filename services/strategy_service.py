import pandas as pd

from typing import Literal, Union

from services.data_loader_service import DataLoaderService
from services.indicator_service import IndicatorService


class StrategyService:
    _df_1h = DataLoaderService.load_by_tf("1h")
    _df_4h = DataLoaderService.load_by_tf("4h")
    _df_1d = DataLoaderService.load_by_tf("1d")
    _df_1w = DataLoaderService.load_by_tf("1w")

    @staticmethod
    def ema_cross():
        print("USE EMA CROSS STRATEGY")
        df = StrategyService._df_1h.copy()
        closes = df["close"]

        # Backtesting
        ema13 = IndicatorService.ema_series(closes, 13)
        ema21 = IndicatorService.ema_series(closes, 21)

        df["ema13"] = ema13
        df["ema21"] = ema21

        df["buy"] = (df["ema13"].shift(1) < df["ema21"].shift(1)) & (
            df["ema13"] > df["ema21"]
        )
        df["sell"] = (df["ema13"].shift(1) > df["ema21"].shift(1)) & (
            df["ema13"] < df["ema21"]
        )

        signal_df = df[(df["buy"]) | (df["sell"])]
        signal_df = signal_df.reset_index(drop=True)

        return df

    @staticmethod
    def ema_filter_multi_tf():
        print("USE EMA FILTER MULTI TIMEFRAME STRATEGY")
        df_1h = StrategyService._df_1h.copy()
        df_4h = StrategyService._df_4h.copy()
        df_1d = StrategyService._df_1d.copy()

        df_1h["open_time"] = pd.to_datetime(df_1h["open_time"]).dt.tz_convert(
            "Asia/Jakarta"
        )
        df_4h["open_time"] = pd.to_datetime(df_4h["open_time"]).dt.tz_convert(
            "Asia/Jakarta"
        )
        df_1d["open_time"] = pd.to_datetime(df_1d["open_time"]).dt.tz_convert(
            "Asia/Jakarta"
        )

        closes_1h = df_1h["close"]
        closes_4h = df_4h["close"]
        closes_1d = df_1d["close"]

        # Backtesting
        df_1h["ema13"] = IndicatorService.ema_series(closes_1h, 13)
        df_1h["ema21"] = IndicatorService.ema_series(closes_1h, 21)
        df_1h["ema50"] = IndicatorService.ema_series(closes_1h, 50)
        df_1h["ema100"] = IndicatorService.ema_series(closes_1h, 100)

        df_4h["ema50"] = IndicatorService.ema_series(closes_4h, 50)
        df_4h["ema100"] = IndicatorService.ema_series(closes_4h, 100)

        df_1d["ema50"] = IndicatorService.ema_series(closes_1d, 50)
        df_1d["ema100"] = IndicatorService.ema_series(closes_1d, 100)

        # Bullish jika EMA50 > EMA100
        df_4h["trend"] = df_4h["ema50"] > df_4h["ema100"]
        df_1d["trend"] = df_1d["ema50"] > df_1d["ema100"]

        # Pastikan sorted by open_time
        df_1h = df_1h.sort_values("open_time")
        df_4h = df_4h.sort_values("open_time")
        df_1d = df_1d.sort_values("open_time")

        # Merge trend higher timeframe ke df_1h menggunakan merge_asof
        df_1h = pd.merge_asof(
            df_1h,
            df_4h[["open_time", "trend"]].rename(columns={"trend": "trend_4h"}),
            on="open_time",
            direction="backward",
        )

        df_1h = pd.merge_asof(
            df_1h,
            df_1d[["open_time", "trend"]].rename(columns={"trend": "trend_1d"}),
            on="open_time",
            direction="backward",
        )

        df = df_1h

        # Buy: EMA13 cross EMA21 ke atas & trend bullish di 4H & 1D
        df["buy"] = (
            (df["ema13"].shift(1) < df["ema21"].shift(1))
            & (df["ema13"] > df["ema21"])
            & (df["trend_4h"] == True)
            & (df["trend_1d"] == True)
        )

        # Sell: EMA13 cross EMA21 ke bawah & trend bearish di 4H & 1D
        df["sell"] = (
            (df["ema13"].shift(1) > df["ema21"].shift(1))
            & (df["ema13"] < df["ema21"])
            & (df["trend_4h"] == False)
            & (df["trend_1d"] == False)
        )

        # Ambil bar yang ada sinyal buy atau sell
        signal_df = df[(df["buy"]) | (df["sell"])]
        signal_df = signal_df.reset_index(drop=True)

        # Optional: tampilkan tail 20 bar
        # print(
        #     df_1h[
        #         ["open_time", "close", "ema13", "ema21", "trend_4h", "trend_1d"]
        #     ].tail(20)
        # )

        return df_1h

    @staticmethod
    def rsi_moment():
        print("USE RSI MOMENT STRATEGY")
        df = StrategyService._df_1h.copy()
        closes = df["close"]

        df["rsi"] = IndicatorService.rsi_series(closes)

        rsi_oversold = 30
        rsi_overbought = 70

        # Entry signals
        df["buy"] = df["rsi"] < rsi_oversold
        df["sell"] = df["rsi"] > rsi_overbought

        # Hanya ambil bar dimana buy/sell terjadi
        signal_df = df[(df["buy"]) | (df["sell"])]
        signal_df = signal_df.reset_index(drop=True)

        return df

    @staticmethod
    def bollinger_bands_moment():
        print("USE BOLLINGER BANDS MOMENT STRATEGY")
        df = StrategyService._df_1h.copy()
        closes = df["close"]

        upper_band, lower_band = IndicatorService.bollinger_bands_series(closes)

        # Masukkan hasil ke df_1h
        df["BB_upper"] = upper_band
        df["BB_lower"] = lower_band

        # Cek hasil
        # print(df[["open_time", "close", "BB_upper", "BB_lower"]].tail(10))

        df["buy"] = (df["close"].shift(1) > df["BB_lower"].shift(1)) & (
            df["close"] < df["BB_lower"]
        )
        df["sell"] = (df["close"].shift(1) < df["BB_upper"].shift(1)) & (
            df["close"] > df["BB_upper"]
        )

        signal_df = df[(df["buy"]) | (df["sell"])]
        signal_df = signal_df.reset_index(drop=True)

        return df

    @staticmethod
    def stoch_moment(k_length: int = 14, k_smoothing: int = 1, d_smoothing: int = 3):
        print("USE STOCHASTIC MOMENT STRATEGY")
        df = StrategyService._df_1h.copy()

        smoothed_k, d_list = IndicatorService.stochastic_series(
            closes=df["close"],
            highs=df["high"],
            lows=df["low"],
            k_length=k_length,
            k_smoothing=k_smoothing,
            d_smoothing=d_smoothing,
        )

        df["%K"] = smoothed_k
        df["%D"] = d_list

        # Entry signals berdasarkan cross %K dan %D
        df["buy"] = (df["%K"].shift(1) < df["%D"].shift(1)) & (df["%K"] > df["%D"])
        df["sell"] = (df["%K"].shift(1) > df["%D"].shift(1)) & (df["%K"] < df["%D"])

        # Hanya ambil bar dimana buy/sell terjadi
        df[(df["buy"]) | (df["sell"])].reset_index(drop=True)
        print(f"USING STOCH({k_length},{k_smoothing},{d_smoothing})")

        return df

    def macd_moment(
        method: Union[
            Literal["classic"], Literal["hist_shift"], Literal["zero_break"]
        ] = "classic",
    ):
        print(f"USE MACD MOMENT STRATEGY ({method})")
        df = StrategyService._df_1h.copy()
        closes = df["close"]

        macd_line, signal_line, histogram = IndicatorService.macd_series(closes)

        df["MACD"] = macd_line
        df["MACD_signal"] = signal_line
        df["Histogram"] = histogram

        # ===== BUY / SELL SIGNALS berdasarkan method =====
        buy = [False] * len(df)
        sell = [False] * len(df)

        for i in range(1, len(df)):
            m, s, h = (
                df["MACD"].iloc[i],
                df["MACD_signal"].iloc[i],
                df["Histogram"].iloc[i],
            )
            pm, ps, ph = (
                df["MACD"].iloc[i - 1],
                df["MACD_signal"].iloc[i - 1],
                df["Histogram"].iloc[i - 1],
            )

            # Skip None
            if any(v is None for v in [m, s, h, pm, ps, ph]):
                continue

            # === METHOD 1: CLASSIC CROSS ===
            if method == "classic":
                if pm < ps and m > s:
                    buy[i] = True
                if pm > ps and m < s:
                    sell[i] = True

            # === METHOD 2: HISTOGRAM MOMENTUM SHIFT ===
            elif method == "hist_shift":
                if h > ph and m > pm:
                    buy[i] = True
                if h < ph and m < pm:
                    sell[i] = True

            # === METHOD 3: ZERO LINE BREAK ===
            elif method == "zero_break":
                if pm < 0 and m > 0:
                    buy[i] = True
                if pm > 0 and m < 0:
                    sell[i] = True

            else:
                raise ValueError("method harus classic, hist_shift, zero_break")

        df["buy"] = buy
        df["sell"] = sell

        # Hanya bar yang memicu buy / sell
        return df[(df["buy"]) | (df["sell"])].reset_index(drop=True)

    @staticmethod
    def scalp_1h(use_ema200=False, conservative=True):
        print(
            f"\nUSE SCALP MOMENT STRATEGY use EMA200 : {use_ema200}, conservative : {conservative}"
        )

        df = StrategyService._df_1h.copy()
        closes = df["close"]

        # Siapkan OHLC untuk ATR
        prices = [
            {"high": h, "low": l, "close": c}
            for h, l, c in zip(df["high"], df["low"], df["close"])
        ]

        df["atr"] = IndicatorService.atr_series(prices, length=14)

        # ==========================
        # MACD
        # ==========================
        macd_line, signal_line, histogram = IndicatorService.macd_series(closes)
        df["macd"] = macd_line
        df["macd_signal"] = signal_line
        df["macd_hist"] = histogram
        df["macd_hist_diff"] = df["macd_hist"].diff()

        # ==========================
        # EMA
        # ==========================
        df["ema13"] = IndicatorService.ema_series(closes, 13)
        df["ema21"] = IndicatorService.ema_series(closes, 21)
        df["ema50"] = IndicatorService.ema_series(closes, 50)
        df["ema200"] = IndicatorService.ema_series(closes, 200)

        # ATR filter: volatilitas harus "aktif"
        atr = df["atr"]
        atr_sma = atr.rolling(14).mean()
        df["atr_ok"] = (atr > atr_sma) & atr.notna()
        df["atr_pct"] = (atr / df["close"]) * 100

        # print(df[["open_time", "open", "macd_hist", "macd_hist_diff"]].tail(10))

        # Trend Filter
        df["trend_ok"] = df["close"] > df["ema50"]

        # Compression / retrace HL
        df["compression"] = (df["ema13"] < df["ema21"]) & df["trend_ok"]

        if use_ema200:
            df["long_trend_ok"] = df["close"] > df["ema200"]
        else:
            df["long_trend_ok"] = True  # tidak pakai filter EMA200

        # Momentum naik / turun
        df["momentum_ok"] = df["macd_hist_diff"] > 0
        df["momentum_fail"] = df["macd_hist_diff"] < 0
        df["macd_positive"] = df["macd_hist"] > 0  # Conservative Way

        # ==========================
        # SIGNALS
        # ==========================
        if conservative:
            df["buy"] = (
                df["atr_ok"]
                & df["trend_ok"]
                & df["compression"]
                & df["momentum_ok"]
                & df["macd_positive"]
                & df["long_trend_ok"]
            )
        else:
            df["buy"] = (
                df["atr_ok"]
                & df["trend_ok"]
                & df["compression"]
                & df["momentum_ok"]
                & df["long_trend_ok"]
            )

        df["sell"] = (
            df["momentum_fail"] | (df["close"] < df["ema50"]) | (df["macd_hist"] < 0)
        )

        # RETURN hanya bar yang ada sinyal
        return df[(df["buy"]) | (df["sell"])].reset_index(drop=True)
