import pandas as pd


from services.strategy_service import StrategyService


class BacktestService:

    @staticmethod
    def compute_pnl(df, capital: float = 1000, entry_alloc: float = 100):
        trades = []
        position = None
        entry_price = None
        entry_time = None

        for _, row in df.iterrows():

            # ENTRY
            if row["buy"] and position is None:
                position = "LONG"
                entry_price = row["close"]
                entry_time = row["open_time"]
                continue

            # EXIT
            if row["sell"] and position == "LONG":
                exit_price = row["close"]
                exit_time = row["open_time"]

                btc_qty = entry_alloc / entry_price
                pnl_nominal = btc_qty * (exit_price - entry_price)
                pnl_percent = pnl_nominal / entry_alloc * 100

                trades.append(
                    {
                        "entry_time": entry_time,
                        "entry_price": entry_price,
                        "exit_time": exit_time,
                        "exit_price": exit_price,
                        "pnl_percent": pnl_percent,
                        "pnl_nominal": pnl_nominal,
                    }
                )

                position = None
                entry_price = None
                entry_time = None

        trades_df = pd.DataFrame(trades)
        # ========================
        # Equity Curve (capital grow)
        # ========================
        equity = [capital]
        for t in trades_df.itertuples():
            equity.append(equity[-1] + t.pnl_nominal)
        equity_series = pd.Series(equity)

        # Max Drawdown
        max_drawdown = (
            (equity_series.cummax() - equity_series) / equity_series.cummax() * 100
        ).max()

        return trades_df, equity_series, max_drawdown

    @staticmethod
    def test():
        capital = 1000
        entry_alloc = capital * 0.1

        df = StrategyService.scalp_1h(use_ema200=False, conservative=False)

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
