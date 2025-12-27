import os
import pandas as pd


class DataLoaderService:
    _dir = "data"
    _filenames = {
        "1h": "BTCUSDT_1h.csv",
        "4h": "BTCUSDT_4h.csv",
        "1d": "BTCUSDT_1d.csv",
        "1w": "BTCUSDT_1w.csv",
    }

    @staticmethod
    def load_by_tf(tf: str):
        tf = tf.lower()

        if tf not in DataLoaderService._filenames:
            raise ValueError(f"Timeframe tidak dikenali: {tf}")

        path = os.path.join(DataLoaderService._dir, DataLoaderService._filenames[tf])

        if not os.path.exists(path):
            raise FileNotFoundError(f"File tidak ditemukan: {path}")

        df = pd.read_csv(path, parse_dates=["open_time"])

        # Pastikan tidak ada null mengganggu
        df = df.dropna(subset=["open_time"])

        # Convert open_time timezone safely
        if df["open_time"].dt.tz is None:
            # Naive → localize dulu
            df["open_time"] = (
                df["open_time"].dt.tz_localize("UTC").dt.tz_convert("Asia/Jakarta")
            )
        else:
            # Already tz-aware → cukup convert
            df["open_time"] = df["open_time"].dt.tz_convert("Asia/Jakarta")

        return df.sort_values("open_time").reset_index(drop=True)
