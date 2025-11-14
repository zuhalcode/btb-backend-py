# 🧩 API SPECIFICATION – Trading Bot Backend

**Framework:** FastAPI

**Base URL:** `http://localhost:8000/api`

## 📚 ARSITEKTUR BOT

```mermaid

    %% ======================================================
    %% LAYER 1 — MARKET DATA SOURCE
    %% ======================================================
    subgraph L1[Layer 1: Market Data Source]
    A[MarketService<br/>(Exchange WS / REST API)]
    end

    %% ======================================================
    %% LAYER 2 — BOT ENGINE
    %% ======================================================
    subgraph L2[Layer 2: Bot Engine]
        B[Bot Engine<br/>(Strategy Core)]
        B1[Risk & Position Manager]
        B2[Order Executor]

        B --> B1
        B --> B2
    end

    %% Flow from Market → Bot
    A --> |Live Price Feed| B

    %% ======================================================
    %% LAYER 3 — DATA STORAGE
    %% ======================================================
    subgraph L3[Layer 3: Data Storage]
        C[(bot_trades)]
        D[(bot_session_states)]
    end

    B2 --> |Record Trades| C
    B1 --> |Update Snapshot| D

    %% ======================================================
    %% LAYER 4 — SESSION & EVENT LAYER
    %% ======================================================
    subgraph L4[Layer 4: Bot Session Manager & Event Dispatcher]
        E[BotSession Manager<br/>(Runtime Monitor)]
    end

    B --> |Emit Status & Events| E

    %% ======================================================
    %% LAYER 5 — SOCKET LAYER
    %% ======================================================
    subgraph L5[Layer 5: Socket Layer]
        F[SocketService<br/>(WebSocket Hub)]
    end

    E --> |Push Updates| F

    %% ======================================================
    %% LAYER 6 — FRONTEND
    %% ======================================================
    subgraph L6[Layer 6: Frontend]
        G[Web Clients<br/>(Dashboards)]
    end

    F --> |Broadcast Messages| G

```

#### Controllers

- `bot_controller.py`
<!-- * `trade_controller.py`
- `market_controller.py`
- `strategy_controller.py`
- `bot_controller.py` -->

#### Services

- `market_service.py`
- `bot_service.py`
- `bot_session_service.py`
- `bot_event_service.py`

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
