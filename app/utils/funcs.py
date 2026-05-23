from aiogram import types
from aiogram.exceptions import TelegramBadRequest

import app.db.db_requests as db

# "───────────────\n"

async def safe_reply(message: types.Message, text: str, reply_markup=None):
    try:
        return await message.edit_text(text=text, reply_markup=reply_markup,
                                        parse_mode="HTML", disable_web_page_preview=True)
    except TelegramBadRequest:
        return await message.answer(text=text, reply_markup=reply_markup, parse_mode="HTML",
                                    disable_web_page_preview=True)
