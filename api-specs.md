# 🧩 API SPECIFICATION – Trading Bot Backend

**Framework:** FastAPI

**Base URL:** `http://localhost:8000/api`

## 📚 ARSITEKTUR FOLDER

#### Controllers

- `bot_controller.py`
<!-- * `trade_controller.py`
- `market_controller.py`
- `strategy_controller.py`
- `bot_controller.py` -->

#### Services

- `bot_service.py`
<!-- * `trade_service.py`
- `market_service.py`
- `strategy_service.py`
- `bot_service.py` -->

<!-- #### Models

* `account_model.py`
* `trade_model.py`
* `market_model.py`
* `strategy_model.py`
* `bot_model.py` -->

<!-- #### Schemas

* `account_schema.py`
* `trade_schema.py`
* `market_schema.py`
* `strategy_schema.py`
* `bot_schema.py` -->

<!-- ## 🔐 AUTHENTICATION (Soon)

JWT token header:

```
Authorization: Bearer <token>
``` -->

## 🧾 BOT CONTROLLER

#### BOT CRUD

#### `GET /bots`

<!-- **Model:** `account_model.py` -->

**Summary :** Get list of all bots

**Service Logic :** `BotService.find_all()`

<!-- **Model:**
```python
class AccountModel(BaseModel):
    account_id: str
    total_balance: float
    available_balance: float
    positions_value: float
    unrealized_pnl: float
    open_positions: int
``` -->

**Response:**

```json
{
  "meta": {
    "status": 200,
    "message": "Binance connection OK"
  },

  "data": [
    {
      "id": "uuid-bot-1",
      "user_id": "uuid-user-1",
      "name": "Bot Alpha",
      "symbol": "BTCUSDT",
      "timeframe": "1h",
      "config": {
        "strategy": "scalping",
        "max_trade": 5
      },
      "created_at": "2025-11-08T12:00:00Z",
      "updated_at": null
    },
    {
      "id": "uuid-bot-2",
      "user_id": "uuid-user-2",
      "name": "Bot Beta",
      "symbol": "ETHUSDT",
      "timeframe": "4h",
      "config": {},
      "created_at": "2025-11-08T12:05:00Z",
      "updated_at": null
    }
  ]
}
```

#### `POST /bots`

<!-- **Model:** `account_model.py` -->

**Summary :** Create new bot

**Service Logic :** `BotService.create()`

**Request:**

```json
{
  "name": "Bot_BTC_1m",
  "symbol": "SOLUSDT",
  "timeframe": "1m",
  "config": {
    "strategy": "scalping",
    "max_trade": 5
  }
}
```

**Response 200:**

```json
{
  "meta": {
    "status": 200,
    "message": "Bot_BTC_1m created successfully"
  },

  "data": {
    "bot_id": "bot_btc_1m"
  }
}
```

#### `PATCH /bot/:id`

<!-- **Model:** `account_model.py` -->

**Summary :** Edit part of bot config

**Service Logic :** `BotService.edit()`

<!-- **Model:**
```python
class AccountModel(BaseModel):
    account_id: str
    total_balance: float
    available_balance: float
    positions_value: float
    unrealized_pnl: float
    open_positions: int
``` -->

**Request:**

```json
{
  "name": "Bot_BTC_1m",
  "symbol": "SOLUSDT",
  "timeframe": "1m"
}
```

**Response:**

```json
{
  "meta": {
    "status": 200,
    "message": "Bot updated successfully"
  },

  "data": {
    "bot_id": "bot_btc_1m"
  }
}
```

### BOT CONTROL

#### `DELETE /bot/:id`

<!-- **Model:** `account_model.py` -->

**Summary :** Get list of all bots

**Service Logic :** `BotService.delete()`

<!-- **Model:**
```python
class AccountModel(BaseModel):
    account_id: str
    total_balance: float
    available_balance: float
    positions_value: float
    unrealized_pnl: float
    open_positions: int
``` -->

**Request:**

```json
{}
```

**Response:**

```json
{
  "meta": {
    "status": 200,
    "message": "Bot deleted successfully"
  },

  "data": { "id": "bot_1" }
}
```

#### `POST /bot/:id/start`

<!-- **Model:** `account_model.py` -->

**Summary :** Start spesific bot chosen

**Service Logic :** `BotService.start()`

<!-- **Model:**
```python
class AccountModel(BaseModel):
    account_id: str
    total_balance: float
    available_balance: float
    positions_value: float
    unrealized_pnl: float
    open_positions: int
``` -->

**Response:**

```json
{
  "meta": {
    "status": 200,
    "message": "Bot started successfully"
  },
  "data": {
    "status": "started",
    "symbol": "BTCUSDT"
  }
}
```

#### `POST /bot/:id/stop`

<!-- **Model:** `account_model.py` -->

**Summary :** Get list of all bots

**Service Logic :** `BotService.stop()`

<!-- **Model:**
```python
class AccountModel(BaseModel):
    account_id: str
    total_balance: float
    available_balance: float
    positions_value: float
    unrealized_pnl: float
    open_positions: int
``` -->

**Response:**

```json
{
  "meta": {
    "status": 200,
    "message": "Trading stopped successfully"
  },
  "data": {
    "status": "stopped",
    "running": false
  }
}
```

#### `GET /bot/check-connection`

<!-- **Model:** `account_model.py` -->

**Summary :** Check Connection Bot to Server

**Service Logic :** `BotService.check_connection()`

<!-- **Model:**
```python
class AccountModel(BaseModel):
    account_id: str
    total_balance: float
    available_balance: float
    positions_value: float
    unrealized_pnl: float
    open_positions: int
``` -->

**Request:**

```json
{}
```

**Response:**

```json
{
  "meta": {
    "status": 200,
    "message": "Binance connection OK"
  },
  "data": {
    "status": "connected",
    "testnet": true,
    "ping_status": 200,
    "serverTime": 1762404450075,
    "localTime": 1762404450333,
    "offset_ms": -258
  }
}
```

## 🧾 TRADE CONTROLLER

**File:** `controllers/trade_controller.py`
**Service:** `trade_service.py`
**Model:** `trade_model.py`

#### `POST /trade/entry`

**Deskripsi:** Buka posisi baru (buy/sell).
**Service Logic:**

- Validasi saldo dan posisi.
- Hit API exchange (mock / real).
- Simpan transaksi ke DB.
- Return hasil order.

**Request Schema:**

```python
class TradeEntryRequest(BaseModel):
    symbol: str
    side: str  # BUY or SELL
    size: float
    type: str  # MARKET or LIMIT
    leverage: int
    note: Optional[str]
```

**Response Schema:**

```python
class TradeResponse(BaseModel):
    status: str
    message: str
    order_id: str
    filled_price: float
    timestamp: datetime
```

---
