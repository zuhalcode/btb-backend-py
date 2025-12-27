import pandas as pd
import numpy as np

import time
import os

from utils.logger import time_logger
from services.ema_service import EMAService

from services.strategy_service import StrategyService
from services.indicator_cache_service import IndicatorCacheService


class BacktestService:

    @staticmethod
    def compute_pnl(
        arrays,
        capital: float = 1000,
        entry_alloc: float = 100,
    ):
        # arrays: dict from ema_tuning_arrays
        close = arrays["close"]
        buy = arrays["buy"]
        sell = arrays["sell"]
        open_time = arrays["open_time"]

        n = close.shape[0]

        # pre-allocate lists (faster than append of tuple)
        entries = []
        entry_prices = []
        exits = []
        exit_prices = []
        pnl_pct = []
        pnl_nom = []

        position = False
        entry_price = 0.0
        entry_time = None

        # local binding for speed
        ea = entry_alloc
        c_arr = close
        b_arr = buy
        s_arr = sell
        t_arr = open_time

        for i in range(n):
            b = b_arr[i]
            if b and (not position):
                position = True
                entry_price = float(c_arr[i])
                entry_time = t_arr[i]
                continue

            s = s_arr[i]
            if s and position:
                exit_price = float(c_arr[i])
                exit_time = t_arr[i]

                qty = ea / entry_price
                pnl_n = qty * (exit_price - entry_price)  # nominal
                pnl_p = (pnl_n / ea) * 100  # percent

                entries.append(entry_time)
                entry_prices.append(entry_price)
                exits.append(exit_time)
                exit_prices.append(exit_price)
                pnl_pct.append(pnl_p)
                pnl_nom.append(pnl_n)

                position = False

        # build dataframe once (fast)
        if len(entries) == 0:
            trades_df = pd.DataFrame(
                columns=[
                    "entry_time",
                    "entry_price",
                    "exit_time",
                    "exit_price",
                    "pnl_percent",
                    "pnl_nominal",
                ]
            )
            equity_series = pd.Series([capital])
            max_drawdown = 0.0
            return trades_df, equity_series, max_drawdown

        trades_df = pd.DataFrame(
            {
                "entry_time": entries,
                "entry_price": entry_prices,
                "exit_time": exits,
                "exit_price": exit_prices,
                "pnl_percent": pnl_pct,
                "pnl_nominal": pnl_nom,
            }
        )

        # equity array (numpy) and drawdown (numpy)
        pnl_nom_array = np.array(pnl_nom, dtype=float)
        equity = np.concatenate(([capital], capital + np.cumsum(pnl_nom_array)))
        equity_series = pd.Series(equity)

        cummax = np.maximum.accumulate(equity)
        # avoid divide by zero
        dd = (cummax - equity) / np.where(cummax == 0, 1, cummax) * 100
        max_drawdown = float(np.max(dd)) if dd.size > 0 else 0.0

        return trades_df, equity_series, max_drawdown

    @staticmethod
    def test_strategy():
        capital = 1000
        entry_alloc = capital * 0.1

        df = StrategyService.ema_baseline_subset()

        results, equity_series, max_drawdown = BacktestService.compute_pnl(
            df, capital, entry_alloc
        )

        # Statistik dasar
        total_trades = len(results)

        # Hitung jumlah sinyal buy dan sell
        total_buy = df["buy"].sum()
        total_sell = df["sell"].sum()

        win_rate = (results["pnl_percent"] > 0).mean() * 100
        avg_win = results[results["pnl_percent"] > 0]["pnl_percent"].mean()
        avg_loss = results[results["pnl_percent"] < 0]["pnl_percent"].mean()

        # Profit Factor
        gross_profit = results[results["pnl_percent"] > 0]["pnl_nominal"].sum()
        gross_loss = abs(results[results["pnl_percent"] < 0]["pnl_nominal"].sum())
        profit_factor = gross_profit / gross_loss if gross_loss != 0 else float("inf")

        final_equity = equity_series.iloc[-1]
        pnl = (final_equity - capital) / capital * 100

        print("\n=== SIGNAL SUMMARY ===")
        print(f"Total Buy Signals  : {total_buy}")
        print(f"Total Sell Signals : {total_sell}")

        # Print summary
        print("\n=== BACKTEST SUMMARY ===")
        print(f"Total Capital      : {capital} USDT")
        print(f"Entry Allocation   : {entry_alloc} USDT per trade")
        print(f"Total Trades       : {total_trades}")
        print(f"Win Rate           : {win_rate:.2f}%")
        print(f"Avg Win (%)        : {avg_win:.2f}%")
        print(f"Avg Loss (%)       : {avg_loss:.2f}%")
        print(f"Profit Factor      : {profit_factor:.2f}")
        print(f"Max Drawdown       : {max_drawdown:.2f}%")
        print(f"Final Equity       : {final_equity:.2f} USDT")
        print(f"Total PnL (%)      : {pnl:.2f}%")

    @staticmethod
    def test_tuning():
        csv_file = "ema_tuning_results_1h_60.csv"
        # header create if not exists
        columns = [
            "ema_fast",
            "ema_slow",
            "total_trades",
            "win_rate",
            "avg_win",
            "avg_loss",
            "profit_factor",
            "max_drawdown",
            "final_equity",
            "pnl_percent",
        ]
        if not os.path.exists(csv_file):
            pd.DataFrame(columns=columns).to_csv(csv_file, index=False)

        capital = 1000.0
        entry_alloc = capital * 0.1

        rows_buffer = []
        flush_every = 200  # tulis ke CSV tiap 200 kombinasi (tune sesuai)
        comb_count = 0
        total_start = time.perf_counter()

        for ema_fast in range(1, 100):
            for ema_slow in range(ema_fast + 1, 101):
                comb_count += 1

                arrays = EMAService.ema_tuning(ema_fast=ema_fast, ema_slow=ema_slow)

                results, equity_series, max_drawdown = BacktestService.compute_pnl(
                    arrays, capital=capital, entry_alloc=entry_alloc
                )

                total_trades = len(results)

                if total_trades == 0:
                    win_rate = 0.0
                    avg_win = 0.0
                    avg_loss = 0.0
                    profit_factor = 0.0
                else:
                    pnl_pct_series = results["pnl_percent"]
                    win_rate = float((pnl_pct_series > 0).mean() * 100)
                    avg_win = float(pnl_pct_series[pnl_pct_series > 0].mean() or 0.0)
                    avg_loss = float(pnl_pct_series[pnl_pct_series < 0].mean() or 0.0)
                    gross_profit = float(
                        results.loc[results["pnl_percent"] > 0, "pnl_nominal"].sum()
                    )
                    gross_loss = abs(
                        float(
                            results.loc[results["pnl_percent"] < 0, "pnl_nominal"].sum()
                        )
                    )
                    profit_factor = (
                        float(gross_profit / gross_loss)
                        if gross_loss != 0
                        else float("inf")
                    )

                final_equity = float(equity_series.iloc[-1])
                pnl_percent = (final_equity - capital) / capital * 100.0

                row = {
                    "ema_fast": ema_fast,
                    "ema_slow": ema_slow,
                    "total_trades": total_trades,
                    "win_rate": round(win_rate, 2),
                    "avg_win": round(avg_win, 6),
                    "avg_loss": round(avg_loss, 6),
                    "profit_factor": (
                        round(profit_factor, 4)
                        if profit_factor != float("inf")
                        else float("inf")
                    ),
                    "max_drawdown": round(max_drawdown, 4),
                    "final_equity": round(final_equity, 4),
                    "pnl_percent": round(pnl_percent, 4),
                }

                rows_buffer.append(row)

                # flush buffer periodically to CSV (faster than per-iteration write)
                if len(rows_buffer) >= flush_every:
                    pd.DataFrame(rows_buffer).to_csv(
                        csv_file, mode="a", index=False, header=False
                    )
                    rows_buffer = []

                # optional light progress print every N combos
                if comb_count % 500 == 0:
                    elapsed_total = time.perf_counter() - total_start
                    print(f" [{comb_count}] combos done — elapsed {elapsed_total:.1f}s")

        # final flush
        if rows_buffer:
            pd.DataFrame(rows_buffer).to_csv(
                csv_file, mode="a", index=False, header=False
            )

        total_elapsed = time.perf_counter() - total_start
        print(f"\nFINISHED {comb_count} combos in {total_elapsed:.2f} sec")

    @staticmethod
    def test_tuning_subset():
        print("\nUSE EMA TUNING SUBSET")
        csv_file = "ema_tuning_subset_results_60.csv"

        top_ema_combos = [
            {"ema_fast": 60, "ema_slow": 63},
            {"ema_fast": 61, "ema_slow": 62},
            {"ema_fast": 59, "ema_slow": 64},
            {"ema_fast": 58, "ema_slow": 65},
            {"ema_fast": 70, "ema_slow": 94},
        ]

        regime_df = pd.read_csv("regime_subset.csv")

        data_subsets = [
            {
                "regime": row["regime"],
                "start_date": pd.to_datetime(row["start"]),
                "end_date": pd.to_datetime(row["end"]),
                "note": f'{row["regime"]}',
            }
            for _, row in regime_df.iterrows()
        ]

        # header create if not exists
        columns = [
            "note",
            "start_date",
            "end_date",
            "ema_fast",
            "ema_slow",
            "total_trades",
            "win_rate",
            "avg_win",
            "avg_loss",
            "profit_factor",
            "max_drawdown",
            "final_equity",
            "pnl_percent",
        ]

        if not os.path.exists(csv_file):
            pd.DataFrame(columns=columns).to_csv(csv_file, index=False)

        capital = 1000.0
        entry_alloc = capital * 0.1

        rows_buffer = []
        flush_every = 1

        for subset in data_subsets:
            start_date = subset["start_date"]
            end_date = subset["end_date"]
            note = subset["note"]

            for combo in top_ema_combos:
                ema_fast = combo["ema_fast"]
                ema_slow = combo["ema_slow"]

                arrays = EMAService.ema_tuning_subset(
                    ema_fast=ema_fast,
                    ema_slow=ema_slow,
                    start_date=start_date,
                    end_date=end_date,
                )

                # ✅ HARD GUARD
                if arrays is None:
                    print("SKIPPED: arrays None (block too small)")
                    continue

                results, equity_series, max_drawdown = BacktestService.compute_pnl(
                    arrays,
                    capital=capital,
                    entry_alloc=entry_alloc,
                )

                total_trades = len(results)

                if total_trades == 0:
                    win_rate = np.nan
                    avg_win = np.nan
                    avg_loss = np.nan
                    profit_factor = np.nan
                else:
                    pnl_pct_series = results["pnl_percent"]
                    win_rate = float((pnl_pct_series > 0).mean() * 100)
                    avg_win = float(pnl_pct_series[pnl_pct_series > 0].mean() or 0.0)
                    avg_loss = float(pnl_pct_series[pnl_pct_series < 0].mean() or 0.0)
                    gross_profit = float(
                        results.loc[results["pnl_percent"] > 0, "pnl_nominal"].sum()
                    )
                    gross_loss = abs(
                        float(
                            results.loc[results["pnl_percent"] < 0, "pnl_nominal"].sum()
                        )
                    )
                    profit_factor = (
                        float(gross_profit / gross_loss)
                        if gross_loss != 0
                        else float("inf")
                    )

                final_equity = float(equity_series.iloc[-1])
                pnl_percent = (final_equity - capital) / capital * 100.0

                row = {
                    "note": note,
                    "start_date": start_date,
                    "end_date": end_date,
                    "ema_fast": ema_fast,
                    "ema_slow": ema_slow,
                    "total_trades": total_trades,
                    "win_rate": round(win_rate, 2),
                    "avg_win": round(avg_win, 6),
                    "avg_loss": round(avg_loss, 6),
                    "profit_factor": (
                        round(profit_factor, 4)
                        if profit_factor != float("inf")
                        else float("inf")
                    ),
                    "max_drawdown": round(max_drawdown, 4),
                    "final_equity": round(final_equity, 4),
                    "pnl_percent": round(pnl_percent, 4),
                }

                rows_buffer.append(row)

                # flush buffer periodically to CSV (faster than per-iteration write)
                if len(rows_buffer) >= flush_every:
                    pd.DataFrame(rows_buffer).to_csv(
                        csv_file, mode="a", index=False, header=False
                    )
                    rows_buffer = []

        # final flush
        if rows_buffer:
            pd.DataFrame(rows_buffer).to_csv(
                csv_file, mode="a", index=False, header=False
            )

    @staticmethod
    def test_candlestick():
        print("\nUSE CANDLESTICK TESTING")
        csv_file = "candlestick_testing.csv"

        # header create if not exists
        columns = [
            "total_trades",
            "win_rate",
            "avg_win",
            "avg_loss",
            "profit_factor",
            "max_drawdown",
            "final_equity",
            "pnl_percent",
        ]

        if not os.path.exists(csv_file):
            pd.DataFrame(columns=columns).to_csv(csv_file, index=False)

        capital = 1000.0
        entry_alloc = capital * 0.1

        arrays = StrategyService.candlestick_entry()
        signal_df = arrays[(arrays["buy"]) | (arrays["sell"])].copy()

        # ==========================
        # TRACK POSITION STATE
        # ==========================
        signal_df["in_position"] = False
        in_pos = False

        for i in signal_df.index:
            if signal_df.at[i, "buy"]:
                in_pos = True

            signal_df.at[i, "in_position"] = in_pos

            if signal_df.at[i, "sell"] and in_pos:
                in_pos = False

        # ==========================
        # FILTER VALID EVENTS ONLY
        # ==========================
        filtered_df = signal_df[
            (signal_df["buy"]) | ((signal_df["sell"]) & (signal_df["in_position"]))
        ]

        print()
        print(
            filtered_df[
                [
                    "open_time",
                    "buy_price",
                    "rsi_before",
                    "buy",
                    "sell",
                    "candle_before",
                ]
            ].tail(50)
        )

        results, equity_series, max_drawdown = BacktestService.compute_pnl(
            arrays,
            capital=capital,
            entry_alloc=entry_alloc,
        )

        total_trades = len(results)

        if total_trades == 0:
            win_rate = np.nan
            avg_win = np.nan
            avg_loss = np.nan
            profit_factor = np.nan
        else:
            pnl_pct_series = results["pnl_percent"]
            win_rate = float((pnl_pct_series > 0).mean() * 100)
            avg_win = float(pnl_pct_series[pnl_pct_series > 0].mean() or 0.0)
            avg_loss = float(pnl_pct_series[pnl_pct_series < 0].mean() or 0.0)
            gross_profit = float(
                results.loc[results["pnl_percent"] > 0, "pnl_nominal"].sum()
            )
            gross_loss = abs(
                float(results.loc[results["pnl_percent"] < 0, "pnl_nominal"].sum())
            )
            profit_factor = (
                float(gross_profit / gross_loss) if gross_loss != 0 else float("inf")
            )

        final_equity = float(equity_series.iloc[-1])
        pnl_percent = (final_equity - capital) / capital * 100.0

        row = {
            "total_trades": total_trades,
            "win_rate": round(win_rate, 2),
            "avg_win": round(avg_win, 6),
            "avg_loss": round(avg_loss, 6),
            "profit_factor": (
                round(profit_factor, 4)
                if profit_factor != float("inf")
                else float("inf")
            ),
            "max_drawdown": round(max_drawdown, 4),
            "final_equity": f"{round(final_equity, 4)} USDT",
            "pnl_percent": round(pnl_percent, 4),
        }

        print(row)
