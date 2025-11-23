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

        return DataLoaderService._load_csv(path)

    @staticmethod
    def _load_csv(path: str):
        df = pd.read_csv(path, parse_dates=["open_time"])

        # Pastikan tidak ada null mengganggu
        df = df.dropna(subset=["open_time"]).reset_index(drop=True)

        # Sort berdasarkan timestamp
        df = df.sort_values("open_time").reset_index(drop=True)

        return df
