import os

from supabase import create_client, Client
from libs.env import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError(
        "Supabase URL or Service Role Key not found in environment variables."
    )

# Simpan instance global
_supabase: Client | None = None


def get_supabase() -> Client:
    global _supabase
    if _supabase is None:
        _supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    return _supabase


# Instance siap dipakai di mana pun
supabase = get_supabase()
