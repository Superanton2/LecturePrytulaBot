from aiogram import Router, types, F

from app.utils.keyboards import create_main_admin_keyboard
from app.db.db_requests import is_admin

router = Router()

@router.callback_query(F.data == "admin_hub")
async def admin_dashboard(callback: types.CallbackQuery):
    if not await (is_admin(callback.from_user.id)):
        await callback.answer("⛔ Доступ заборонено", show_alert=True)
        return

    text = "Це панель адміна. Ці функції закритів для простих користувачів\n"
    keyboard = create_main_admin_keyboard()

    await callback.message.edit_text(
            text=text,
            reply_markup=keyboard.as_markup(),
            parse_mode="HTML"
        )


@router.callback_query(F.data == "admin_stop_registration")
async def admin_archive(callback: types.CallbackQuery):
    text = (
        f"<b>admin_stop_registration</b>\n\n"
    )

    await callback.message.edit_text(
        text=text,
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admin_write_participants")
async def admin_archive(callback: types.CallbackQuery):
    text = (
        f"<b>admin_write_participants</b>\n\n"
    )

    await callback.message.edit_text(
        text=text,
        parse_mode="HTML"
    )