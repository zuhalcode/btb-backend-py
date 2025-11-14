from libs.supabase import supabase


from dtos.bot_session_dto import (
    BotSessionResponseDTO,
    BotSessionDTO,
    BotSessionUpdateDTO,
    BotSessionCreateDTO,
    BotSessionStatus as Status,
)

import requests
import time
import asyncio


class BotSessionService:
    _table = "bot_sessions"

    # CRUD
    @staticmethod
    def find_all() -> list[BotSessionResponseDTO]:
        try:
            result = (
                supabase.table(BotSessionService._table)
                .select("id, name, symbol, timeframe, config, created_at, updated_at")
                .order("created_at", desc=True)
                .execute()
            )

            return result.data

        except Exception as e:
            print("Error in retrieve data:", str(e))
            raise e

    @staticmethod
    def find_one(id: str) -> BotSessionResponseDTO:
        try:
            result = (
                supabase.table(BotSessionService._table)
                .select("*")
                .eq("id", id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )

            return result.data[0]

        except Exception as e:
            print("Error in retrieve Bot session:", str(e))
            raise e

    @staticmethod
    def find_one_by_bot_id(bot_id: str) -> BotSessionResponseDTO:
        try:
            result = (
                supabase.table(BotSessionService._table)
                .select("*")
                .eq("bot_id", bot_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )

            data = result.data[0]

            return data if data else None

        except Exception as e:
            print("Error in retrieve Bot session:", str(e))
            raise e

    @staticmethod
    def find_one_by_bot_id_and_status(
        bot_id: str, status: str
    ) -> BotSessionResponseDTO:
        try:
            result = (
                supabase.table(BotSessionService._table)
                .select("*")
                .eq("bot_id", bot_id)
                .eq("status", status)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )

            if not result.data:
                return None

            return result.data[0]

        except Exception as e:
            print("Error in retrieve Bot session by status and bot_id:", str(e))
            raise e

    @staticmethod
    def find_one_by_status(id: str, status: str) -> BotSessionResponseDTO:
        try:
            result = (
                supabase.table(BotSessionService._table)
                .select("*")
                .eq("bot_id", id)
                .eq("status", status)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )

            return result.data[0]

        except Exception as e:
            print("Error in retrieve Bot session:", str(e))
            raise e

    @staticmethod
    def create(id: str) -> BotSessionResponseDTO:
        try:
            result = (
                supabase.table(BotSessionService._table)
                .insert({"bot_id": id, "status": "IDLE"})
                .execute()
            )

            data = result.data[0]

            return data

        except Exception as e:
            print("Error creating Bot Session:", e)
            raise e

    @staticmethod
    def update(id: str, payload: BotSessionUpdateDTO) -> BotSessionResponseDTO:
        try:

            # ✅ Pastikan bot dengan ID tersebut ada
            existing = (
                supabase.table(BotSessionService._table)
                .select("id")
                .eq("id", id)
                .limit(1)
                .execute()
            )

            if not existing.data:
                raise ValueError(f"Bot with id '{id}' not found")

            result = (
                supabase.table(BotSessionService._table)
                .update(payload)
                .eq("id", id)
                .execute()
            )

            data = result.data[0]

            return data

        except Exception as e:
            print("Error updating Bot:", e)
            raise e

    def update_by_bot_id(
        bot_id: str, payload: BotSessionUpdateDTO
    ) -> list[BotSessionResponseDTO]:
        try:

            # ✅ Pastikan bot dengan ID tersebut ada
            existing = (
                supabase.table(BotSessionService._table)
                .select("id")
                .eq("bot_id", bot_id)
                .limit(1)
                .execute()
            )

            if not existing.data:
                raise ValueError(f"Bot with id '{bot_id}' not found")

            result = (
                supabase.table(BotSessionService._table)
                .update(payload)
                .eq("bot_id", bot_id)
                .execute()
            )

            return result.data

        except Exception as e:
            print(f"Error updating Bot by id {bot_id} : ", e)
            raise e

    @staticmethod
    def delete(id: str) -> list[BotSessionResponseDTO]:
        try:
            # ✅ Pastikan ID dikirim
            if not id:
                raise ValueError("Bot ID is required for deletion")

            # ✅ Cek apakah bot dengan ID tersebut ada
            existing = (
                supabase.table(BotSessionService._table)
                .select("id")
                .eq("id", id)
                .limit(1)
                .execute()
            )

            if not existing.data:
                raise ValueError(f"Bot with id '{id}' not found")

            result = (
                supabase.table(BotSessionService._table).delete().eq("id", id).execute()
            )
            return result.data

        except Exception as e:
            print("Error deleting Bot:", e)
            raise e

    # Force stop
    @staticmethod
    def force_stop():
        try:
            current_status = Status.RUNNING.value  # Ambil nilai string dari Enum

            payload = {"status": Status.FORCE_STOP.value}

            result = (
                supabase.table(BotSessionService._table)
                .update(payload)
                .eq("status", current_status)
                .execute()
            )

            return result.data

        except Exception as e:
            print(
                f"Error updating all running sessions to {Status.FORCE_STOP.value}:", e
            )
            raise e
