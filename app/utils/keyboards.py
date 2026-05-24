import os
from dotenv import load_dotenv
load_dotenv()
SHEET_URL = os.getenv("SHEET_URL")

from aiogram.utils.keyboard import InlineKeyboardBuilder

def create_main_keyboard(is_admin: bool= False) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button( text="🎟️ Зареєструватись", callback_data="registration")
    builder.button( text="🪪 Профіль", callback_data="profile")
    builder.adjust(1)

    if is_admin:
        builder.button( text="🔐 Панель Адміна", callback_data="admin_hub")
        builder.adjust(1)
    return builder


def create_main_admin_keyboard() -> InlineKeyboardBuilder:
        builder = InlineKeyboardBuilder()
        builder.button(text="📊 Google табличка", url=SHEET_URL)
        builder.button(text="Зупинити реєстрацію", callback_data="admin_stop_registration")
        builder.button(text="Написати учасникам", callback_data="admin_write_participants") # зареєустровані / всі учасники

        builder.adjust(1)
        return builder