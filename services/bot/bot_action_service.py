class BotActionService:

    def __init__(self, client, symbol):
        self.client = client
        self.symbol = symbol

    async def get_current_price(self):
        try:
            ticker = self.client.get_symbol_ticker(symbol=self.symbol)
            price = float(ticker["price"])
            return price

        except Exception as e:
            print(f"❌ Failed to get current price: {e}")
            return 0.0

    async def get_balance(self, asset="USDT"):
        try:
            account_info = self.client.get_account()
            balance = next(
                (b for b in account_info["balances"] if b["asset"] == asset), None
            )

            return {
                "account": account_info,
                "balance": balance,
            }
        except Exception as e:
            print(f"❌ Failed to get balance: {e}")
