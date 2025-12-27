class CandlestickIndicator:

    @staticmethod
    def bullish_marubozu(df, shadow_ratio=0.05, epsilon=1e-8):
        """
        Menandai Bullish Marubozu pada seluruh DataFrame
        dan menambahkan kolom: candlestick
        """

        def _detect(row):
            open_ = row["open"]
            high = row["high"]
            low = row["low"]
            close = row["close"]

            # Harus bullish
            if close <= open_:
                return None

            candle_range = high - low
            if candle_range <= epsilon:
                return None

            upper_shadow = high - close
            lower_shadow = open_ - low

            if (upper_shadow / candle_range) > shadow_ratio:
                return None

            if (lower_shadow / candle_range) > shadow_ratio:
                return None

            return "marubozu"

        df["candle"] = df.apply(_detect, axis=1)
        return df

    @staticmethod
    def bullish_long_white(df, shadow_ratio=0.2, epsilon=1e-8):
        """
        Menandai Bullish Marubozu pada seluruh DataFrame
        dan menambahkan kolom: candlestick
        """

        MIN_SHADOW_RATIO = 0.05  # > marubozu
        MAX_SHADOW_RATIO = 0.20  # toleransi long white
        MIN_BODY_RATIO = 0.60  # body harus dominan

        def _detect(row):
            if row["candle"] is not None:
                return row["candle"]

            open_ = row["open"]
            high = row["high"]
            low = row["low"]
            close = row["close"]

            # Harus bullish
            if close <= open_:
                return None

            candle_range = high - low
            if candle_range <= epsilon:
                return None

            body = abs(close - open_)
            body_ratio = body / candle_range

            upper_shadow = high - close
            lower_shadow = open_ - low

            upper_ratio = upper_shadow / candle_range
            lower_ratio = lower_shadow / candle_range

            # body harus dominan
            if body_ratio < MIN_BODY_RATIO:
                return None

            # wick tidak boleh sekecil marubozu
            if upper_ratio <= MIN_SHADOW_RATIO:
                return None

            if lower_ratio <= MIN_SHADOW_RATIO:
                return None

            # wick tidak boleh terlalu besar
            if upper_ratio > MAX_SHADOW_RATIO:
                return None

            if lower_ratio > MAX_SHADOW_RATIO:
                return None

            return "long_white"

        df["candle"] = df.apply(_detect, axis=1)
        return df

    @staticmethod
    def bullish_hammer(df, epsilon=1e-8):
        """
        Menandai Bullish Hammer pada seluruh DataFrame
        dan menambahkan kolom: candle
        """

        BODY_MIN_RATIO = 0.10  # body minimal 10% dari range
        BODY_MAX_RATIO = 0.35  # body maksimal 35% dari range
        LOWER_WICK_BODY_RATIO = 2.0  # lower wick ≥ 2x body
        UPPER_WICK_BODY_MAX = 0.30  # upper wick ≤ 30% body

        def _detect(row):
            if row["candle"] is not None:
                return row["candle"]

            open_ = row["open"]
            high = row["high"]
            low = row["low"]
            close = row["close"]

            # Bias bullish
            if close < open_:
                return None

            candle_range = high - low
            if candle_range <= epsilon:
                return None

            body = abs(close - open_)

            # body harus proporsional (tidak doji, tidak full body)
            if body < candle_range * BODY_MIN_RATIO:
                return None

            if body > candle_range * BODY_MAX_RATIO:
                return None

            lower_wick = min(open_, close) - low
            upper_wick = high - max(open_, close)

            # karakteristik hammer
            if lower_wick < body * LOWER_WICK_BODY_RATIO:
                return None

            if upper_wick > body * UPPER_WICK_BODY_MAX:
                return None

            return "hammer"

        df["candle"] = df.apply(_detect, axis=1)
        return df

    @staticmethod
    def bullish_inverted_hammer(df, epsilon=1e-8):
        """
        Menandai Bullish Hammer pada seluruh DataFrame
        dan menambahkan kolom: candle
        """

        BODY_MIN_RATIO = 0.10  # body minimal 10% dari range
        BODY_MAX_RATIO = 0.35  # body maksimal 35% dari range
        UPPER_WICK_BODY_RATIO = 2.0  # upper wick ≥ 2x body
        LOWER_WICK_BODY_MAX = 0.30  # lower wick ≤ 30% body

        def _detect(row):
            if row["candle"] is not None:
                return row["candle"]

            open_ = row["open"]
            high = row["high"]
            low = row["low"]
            close = row["close"]

            # Bias bullish
            if close < open_:
                return None

            candle_range = high - low
            if candle_range <= epsilon:
                return None

            body = abs(close - open_)

            # body harus proporsional (tidak doji, tidak full body)
            if body < candle_range * BODY_MIN_RATIO:
                return None

            if body > candle_range * BODY_MAX_RATIO:
                return None

            lower_wick = min(open_, close) - low
            upper_wick = high - max(open_, close)

            # karakteristik inverted hammer
            if upper_wick < body * UPPER_WICK_BODY_RATIO:
                return None

            if lower_wick > body * LOWER_WICK_BODY_MAX:
                return None

            return "inverted_hammer"

        df["candle"] = df.apply(_detect, axis=1)
        return df
