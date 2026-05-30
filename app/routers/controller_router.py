from dotenv import load_dotenv

from aiogram import F
from aiogram.filters import Command
from aiogram import Router, types
from aiogram.fsm.context import FSMContext

import app.utils.keyboards as kb
from app.utils.funcs import safe_reply
from app.db.db_requests import is_admin, get_user
from app.routers.admin_router import router as admin_router
from app.routers.registration_router import router as registration_router
from app.routers.profile_router import router as profile_router

load_dotenv()
router = Router()
router.include_routers(
    admin_router,
    registration_router,
    profile_router,
)

@router.message(Command("start"))
async def cmd_start(message: types.Message):

    is_user_admin = await is_admin(message.from_user.id)
    existing_user = await get_user(message.from_user.id)

    text = ("Вітаю! Я бот для реєстрації на лекцію про благодійність від Сергія Притули. "
                "Ви не зареєстровані, після реєстрації ви побачите час та місце проведення заходу.")
    # if is_user_admin:
    #     keyboard = kb.create_main_admin_keyboard()
    #     text += ("\n\n───────────────\n"
    #             "Ви маєте права Адміна\nОбери дію:\n")
    if existing_user:
        keyboard = kb.create_main_keyboard(is_existing_user=existing_user)
        text = ("Ви вже зареєстровані. Дата 24 травня. Вітаю Макса Коваля з днюхою!\n"
                "Можете переглянути свої дані в профілі.")
    else:
        keyboard = kb.create_main_keyboard(is_existing_user=existing_user)

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
    existing_user = await get_user(callback.from_user.id)

    text = ("Вітаю! Я бот для реєстрації на лекцію про благодійність від Сергія Притули. "
                "Ви не зареєстровані, після реєстрації ви побачите час та місце проведення заходу.")
    # if is_user_admin:
    #     keyboard = kb.create_main_admin_keyboard()
    #     text += ("\n\n───────────────\n"
    #             "Ви маєте права Адміна\nОбери дію:\n")
    if existing_user:
        keyboard = kb.create_main_keyboard(is_existing_user=existing_user)
        text = ("Ви вже зареєстровані. Дата 24 травня. Вітаю Макса Коваля з днюхою!\n"
                "Можете переглянути свої дані в профілі.")
    else:
        keyboard = kb.create_main_keyboard(is_existing_user=existing_user)


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