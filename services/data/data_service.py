import time
import numpy as np
from services.data import DataLoaderService
from utils.logger import time_logger


class DataService:
    df_1h = None

    _data_training = None
    _data_validation = None
    _data_out_of_sample = None

    @classmethod
    def init(cls):
        print("Data Service Init ...")
        cls.df_1h = DataLoaderService.load_by_tf("1h")
        cls.df_1h = cls.df_1h.sort_values("open_time").reset_index(drop=True)

        cls._split_data()
        print("Data Service Ready to Use")

    # ============================================================
    # 1. DATA SPLIT 60/20/20
    # ============================================================
    @classmethod
    def _split_data(cls):
        n = len(cls.df_1h)

        train_end = int(n * 0.60)
        valid_end = int(n * 0.80)

        cls._data_training = cls.df_1h.iloc[:train_end].reset_index(drop=True)
        cls._data_validation = cls.df_1h.iloc[train_end:valid_end].reset_index(
            drop=True
        )
        cls._data_out_of_sample = cls.df_1h.iloc[valid_end:].reset_index(drop=True)

    # ============================================================
    # 2. ACCESSORS
    # ============================================================
    @classmethod
    def get_df_1h(cls):
        return cls.df_1h.copy()

    @classmethod
    def get_train(cls):
        return cls._data_training.copy()

    @classmethod
    def get_valid(cls):
        return cls._data_validation.copy()

    @classmethod
    def get_oos(cls):
        return cls._data_out_of_sample.copy()
