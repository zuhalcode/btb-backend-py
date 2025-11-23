from typing import List, Sequence, Optional, Dict


class IndicatorService:
    @staticmethod
    def ema_series(
        prices: Sequence[float], period: int, use_ema_seed: bool = False
    ) -> List[Optional[float]]:

        prices = list(prices)
        ema = [None] * len(prices)
        k = 2 / (period + 1)

        # ===== MODE 1: Binance/TradingView =====
        # EMA seeded dari harga pertama
        if use_ema_seed:
            ema[0] = prices[0]
            for i in range(1, len(prices)):
                ema[i] = prices[i] * k + ema[i - 1] * (1 - k)
            return ema

        # ===== MODE 2: EMA dengan SMA seed (kode lama kamu) =====
        if len(prices) < period:
            raise ValueError("Data kurang dari period")

        sma = sum(prices[:period]) / period
        ema[period - 1] = sma

        for i in range(period, len(prices)):
            ema[i] = prices[i] * k + ema[i - 1] * (1 - k)

        return ema

    @staticmethod
    def stochastic_series(
        closes: Sequence[float],
        highs: Sequence[float],
        lows: Sequence[float],
        k_length: int = 14,
        k_smoothing: int = 3,
        d_smoothing: int = 3,
    ) -> tuple[List[Optional[float]], List[Optional[float]]]:

        closes = list(closes)
        highs = list(highs)
        lows = list(lows)
        n = len(closes)

        raw_k = [None] * n
        smoothed_k = [None] * n
        d_list = [None] * n

        # Hitung raw %K
        for i in range(k_length - 1, n):
            low_min = min(lows[i - k_length + 1 : i + 1])
            high_max = max(highs[i - k_length + 1 : i + 1])
            raw_k[i] = (
                100 * (closes[i] - low_min) / (high_max - low_min)
                if high_max != low_min
                else 0
            )

        # Smooth %K
        for i in range(k_length - 1 + k_smoothing - 1, n):
            smoothed_k[i] = sum(raw_k[i - k_smoothing + 1 : i + 1]) / k_smoothing

        # Hitung %D dari smoothed %K
        for i in range(k_length - 1 + k_smoothing - 1 + d_smoothing - 1, n):
            d_list[i] = sum(smoothed_k[i - d_smoothing + 1 : i + 1]) / d_smoothing

        return smoothed_k, d_list

    @staticmethod
    def rsi_series(prices: Sequence, period: int = 14) -> List[Optional[float]]:
        prices = list(prices)
        rsi: List[Optional[float]] = [None] * len(prices)
        if len(prices) < period:
            return rsi

        gains = [0.0] * len(prices)
        losses = [0.0] * len(prices)
        for i in range(1, len(prices)):
            delta = prices[i] - prices[i - 1]
            gains[i] = max(delta, 0)
            losses[i] = max(-delta, 0)

        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        rsi[period] = 100 - (100 / (1 + avg_gain / avg_loss)) if avg_loss != 0 else 100

        for i in range(period + 1, len(prices)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            rs = avg_gain / avg_loss if avg_loss != 0 else float("inf")
            rsi[i] = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def bollinger_bands_series(
        prices: Sequence[float], period=20, std_dev=2
    ) -> List[Optional[float]]:
        prices = list(prices)
        n = len(prices)
        upper_band: List[Optional[float]] = [None] * n
        lower_band: List[Optional[float]] = [None] * n

        for i in range(period - 1, n):
            window = prices[i - period + 1 : i + 1]
            sma = sum(window) / period
            variance = sum((p - sma) ** 2 for p in window) / period
            std = variance**0.5
            upper_band[i] = sma + std_dev * std
            lower_band[i] = sma - std_dev * std

        return upper_band, lower_band

    @staticmethod
    def macd_series(
        prices: Sequence[float], fast: int = 12, slow: int = 26, signal: int = 9
    ) -> tuple[List[Optional[float]], List[Optional[float]], List[Optional[float]]]:

        # EMA Binance-style
        ema_fast = IndicatorService.ema_series(prices, fast, use_ema_seed=True)
        ema_slow = IndicatorService.ema_series(prices, slow, use_ema_seed=True)

        macd = [ema_fast[i] - ema_slow[i] for i in range(len(prices))]

        # Signal line (juga Binance EMA)
        signal_line = IndicatorService.ema_series(macd, signal, use_ema_seed=True)

        histogram = [macd[i] - signal_line[i] for i in range(len(prices))]

        return macd, signal_line, histogram

    @staticmethod
    def atr_series(
        prices: Sequence[Dict[str, float]], length: int = 14
    ) -> List[Optional[float]]:
        """
        Menghitung ATR dari sequence OHLC
        prices: list of dict dengan key: high, low, close
        return: list ATR (None sebelum cukup data)
        """

        n = len(prices)
        if n == 0:
            return []

        # Helper: compute True Range for each bar
        tr = [0.0] * n
        prev_close = None
        for i, p in enumerate(prices):
            h = float(p["high"])
            l = float(p["low"])
            c = float(p["close"])
            if prev_close is None:
                tr[i] = h - l
            else:
                tr[i] = max(h - l, abs(h - prev_close), abs(l - prev_close))
            prev_close = c

        atr = [None] * n

        # If not enough data to compute first ATR, return initial None's
        if n < length:
            return atr

        # First ATR value = SMA of first 'length' TR values (Wilder original)
        first_atr = sum(tr[0:length]) / float(length)
        atr[length - 1] = first_atr

        # Wilder smoothing: ATR[i] = (ATR[i-1] * (length - 1) + TR[i]) / length
        prev_atr = first_atr
        for i in range(length, n):
            curr_atr = (prev_atr * (length - 1) + tr[i]) / length
            atr[i] = curr_atr
            prev_atr = curr_atr

        return atr
