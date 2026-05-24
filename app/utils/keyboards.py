import os
from dotenv import load_dotenv
load_dotenv()
SHEET_URL = os.getenv("SHEET_URL")

from app.utils.bot_state import global_state
from aiogram.utils.keyboard import InlineKeyboardBuilder

def create_main_keyboard(is_existing_user: bool= False) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    if is_existing_user:
        builder.button( text="🪪 Профіль", callback_data="profile")
    else:
        builder.button( text="🎟️ Зареєструватись", callback_data="registration")

    return builder

def create_main_admin_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text="🎟️ Зареєструватись", callback_data="registration")
    builder.button(text="🪪 Профіль", callback_data="profile")
    builder.button(text="📊 Google табличка", url=SHEET_URL)

    status = "✅ ВІДКРИТА" if global_state["registration_open"] else "❌ ЗАКРИТА"
    if status == "✅ ВІДКРИТА":
        text = "🔐Закрити реєстрацію"
    else:
        text ="🔓Вікрити реєстрацію"
    builder.button(text=text, callback_data="admin_stop_registration")
    builder.button(text="📨Написати учасникам", callback_data="admin_write_participants")  # зареєустровані / всі учасники
    builder.adjust(1)
    return builder