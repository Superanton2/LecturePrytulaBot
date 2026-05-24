from dotenv import load_dotenv

from aiogram import F
from aiogram.filters import Command
from aiogram import Router, types
from aiogram.fsm.context import FSMContext

import app.utils.keyboards as kb
from app.utils.funcs import safe_reply
from app.db.db_requests import is_admin
from app.routers.registration_router import router as registration_router
# from app.routers.profile_router import router as profile_router
from app.routers.admin_router import router as admin_router

load_dotenv()
router = Router()
router.include_routers(
    registration_router,
    # profile_router,
    admin_router,
)

@router.message(Command("start"))
async def cmd_start(message: types.Message):

    is_user_admin = await is_admin(message.from_user.id)

    keyboard = kb.create_main_keyboard(is_user_admin)
    text = ("Вітаю! Я бот для реєстрації на лекцію про благодійність від Сергія Притули. "
            "Після реєстрації ти побачиш час та місце проведення заходу. \nОбери дію:\n")

    await message.reply(
        text= text,
        reply_markup= keyboard.as_markup()
    )

@router.callback_query(F.data.in_(["controller_hub", "controller_hub_new"]))
async def cmd_back_hub(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await state.clear()

    is_user_admin = await is_admin(callback.from_user.id)

    keyboard = kb.create_main_keyboard(is_user_admin)
    text = ("Вітаю! Я бот для реєстрації на лекцію про благодійність від Сергія Притули. "
            "Після реєстрації ти побачиш час та місце проведення заходу. \nОбери дію:\n")


    if callback.data == "controller_hub_new":
        await safe_reply(
            message=callback.message,
            text=text,
            reply_markup=keyboard.as_markup()
        )
    else:
        await callback.message.answer(
            text=text,
            reply_markup=keyboard.as_markup()
        )

    await callback.answer()