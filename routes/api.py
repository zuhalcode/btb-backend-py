from fastapi import APIRouter
from controllers.bot_controller import BotController

router = APIRouter(prefix="/api/bots")

# Bot Control
router.get("/check-connection")(BotController.check_connection)
router.post("/{id}/activate")(BotController.activate)
router.post("/{id}/deactivate")(BotController.deactivate)
router.post("/{id}/start")(BotController.start)
router.post("/{id}/stop")(BotController.stop)

# CRUD
router.get("")(BotController.find_all)
router.get("/{id}")(BotController.find_one)
router.post("")(BotController.create)
router.put("/{id}")(BotController.update)
router.delete("/{id}")(BotController.delete)
