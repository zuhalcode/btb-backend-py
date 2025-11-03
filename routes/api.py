from fastapi import APIRouter
from controllers.trading_controller import TradingController

router = APIRouter(prefix="/api/trading")

router.get("/check-connection")(TradingController.check_connection)
router.post("/start")(TradingController.start_grid_trading)
router.post("/stop")(TradingController.stop_grid_trading)
