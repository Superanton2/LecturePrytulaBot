from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardRemove

from app.utils.bot_state import global_state
from app.utils.google_sheets import add_user_to_sheet
from app.db.db_requests import add_user, get_user
import asyncio
import logging
import os
from dotenv import load_dotenv

load_dotenv()

router = Router()


class RegisterForm(StatesGroup):
    entering_name = State()
    entering_phone = State()
    entering_mail = State()
    choosing_education = State()
    entering_other_edu = State()
    entering_faculty = State()
    agreeing_to_rules = State()
    waiting_confirmation = State()


@router.callback_query(F.data == "registration")
async def start_registration(callback: types.CallbackQuery, state: FSMContext):
    # Перевіряємо, чи відкрита реєстрація
    if not global_state["registration_open"]:
        await callback.answer("На жаль, реєстрація вже закрита ❌", show_alert=True)
        return

    existing_user = await get_user(callback.from_user.id)

    if existing_user:
        builder = InlineKeyboardBuilder()
        builder.button(text="🪪 Перейти в профіль", callback_data="profile")
        builder.button(text="Головне меню", callback_data="controller_hub", style="primary")

        await callback.message.edit_text(
            "❌ <b>Ти вже зареєстрований на цей захід!</b>\n\n"
            "Якщо ти хочете змінити свої дані (наприклад, номер телефону чи факультет), "
            "перейди у свій Профіль.",
            reply_markup=builder.as_markup()
        )
        await callback.answer()
        return

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    new_msg = await callback.message.answer(
        "[1/5] 👤 Введи твоє ПІБ \nПриклад: Корнага Ярослав Ігорович"
    )

    await state.update_data(main_message_id=new_msg.message_id)
    await state.set_state(RegisterForm.entering_name)
    await callback.answer()


@router.message(RegisterForm.entering_name, F.text)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    main_msg_id = data.get("main_message_id")

    try:
        await message.delete()
    except Exception:
        pass
    if main_msg_id:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=main_msg_id)
        except Exception:
            pass

    builder = ReplyKeyboardBuilder()
    builder.button(text="Надіслати мій номер", request_contact=True)

    new_msg = await message.answer(
        "[2/5] 📱Введи твій номер телефону або натисни кнопку нижче\nПриклад: 095 027...",
        reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    )

    await state.update_data(main_message_id=new_msg.message_id)
    await state.set_state(RegisterForm.entering_phone)


@router.message(RegisterForm.entering_phone)
async def process_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    main_msg_id = data.get("main_message_id")

    try:
        await message.delete()
    except Exception:
        pass
    if main_msg_id:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=main_msg_id)
        except Exception:
            pass

    if message.contact:
        phone = message.contact.phone_number
    elif message.text:
        phone = message.text
    else:
        await message.answer("[2/5] 📱Введи твій номер телефону або натисни кнопку нижче\nПриклад: 095 027...")
        return

    await state.update_data(phone=phone)

    new_msg = await message.answer(
        "[3/5] ✉️ Введи твою електронну пошту\nПриклад: email@example.com",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.update_data(main_message_id=new_msg.message_id)
    await state.set_state(RegisterForm.entering_mail)


@router.message(RegisterForm.entering_mail, F.text)
async def process_mail(message: types.Message, state: FSMContext):
    await state.update_data(mail=message.text)
    data = await state.get_data()
    main_msg_id = data.get("main_message_id")

    try:
        await message.delete()
    except Exception:
        pass
    if main_msg_id:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=main_msg_id)
        except Exception:
            pass

    builder = InlineKeyboardBuilder()
    builder.button(text="🎓 КПІ ім. Ігоря Сікорського", callback_data="edu_kpi")
    builder.button(text="🏫 Інший університет", callback_data="edu_other")
    builder.button(text="❌ Не навчаюсь", callback_data="edu_none")
    builder.adjust(1)

    new_msg = await message.answer(
        "[4/5] Вкажи твій статус щодо навчання:",
        reply_markup=builder.as_markup()
    )

    await state.update_data(main_message_id=new_msg.message_id)
    await state.set_state(RegisterForm.choosing_education)


@router.callback_query(RegisterForm.choosing_education, F.data.startswith("edu_"))
async def process_education_choice(callback: types.CallbackQuery, state: FSMContext):
    choice = callback.data

    if choice == "edu_none":
        await state.update_data(education="не навчаюсь", faculty="не навчаюсь")
        await callback.answer()
        await ask_for_rules(callback, state)

    elif choice == "edu_kpi":
        await state.update_data(education="КПІ")
        await callback.message.edit_text("[5/5] Введи назву твого факультету\nПриклад: ФІОТ")
        await state.set_state(RegisterForm.entering_faculty)
        await callback.answer()

    elif choice == "edu_other":
        await callback.message.edit_text("[4/5] Введи назву твого навчального закладу:")
        await state.set_state(RegisterForm.entering_other_edu)
        await callback.answer()


@router.message(RegisterForm.entering_other_edu, F.text)
async def process_other_edu(message: types.Message, state: FSMContext):
    await state.update_data(education=message.text)
    data = await state.get_data()
    main_msg_id = data.get("main_message_id")

    try:
        await message.delete()
    except Exception:
        pass

    try:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=main_msg_id,
            text="[5/5] 🏫 Введи назву твого факультету\nПриклад: ФІОТ"
        )
    except Exception:
        pass

    await state.set_state(RegisterForm.entering_faculty)


@router.message(RegisterForm.entering_faculty, F.text)
async def process_faculty(message: types.Message, state: FSMContext):
    await state.update_data(faculty=message.text)
    try:
        await message.delete()
    except Exception:
        pass

    await ask_for_rules(message, state)


async def ask_for_rules(event: types.Message | types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    main_msg_id = data.get("main_message_id")

    bot = event.bot
    chat_id = event.message.chat.id if isinstance(event, types.CallbackQuery) else event.chat.id


    rules_url = os.getenv("RULES_URL")

    text = (
        f"📜 <b>Правила заходу</b>\n\n"
        f"Будь ласка, ознайомся із правилами нашого заходу за посиланням нижче:\n"
        f"<a href='{rules_url}'>Читати правила</a>\n\n"
        f"Чи згоден/а ти їх дотримуватися?"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="Погоджуюсь", callback_data="agree_rules", style="success")
    # builder.button(text="❌ Відмовляюсь", callback_data="cancel_registration")
    builder.adjust(1)

    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(text=text, reply_markup=builder.as_markup(), disable_web_page_preview=False)
    else:
        if main_msg_id:
            try:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=main_msg_id,
                    text=text,
                    reply_markup=builder.as_markup(),
                    disable_web_page_preview=False
                )
            except Exception:
                new_msg = await event.answer(text=text, reply_markup=builder.as_markup(), disable_web_page_preview=False)
                await state.update_data(main_message_id=new_msg.message_id)
        else:
            new_msg = await event.answer(text=text, reply_markup=builder.as_markup(), disable_web_page_preview=False)
            await state.update_data(main_message_id=new_msg.message_id)

    await state.set_state(RegisterForm.agreeing_to_rules)


@router.callback_query(RegisterForm.agreeing_to_rules, F.data == "agree_rules")
async def process_agree_rules(callback: types.CallbackQuery, state: FSMContext):
    await show_confirmation_screen(callback, state)
    await callback.answer()


async def show_confirmation_screen(event: types.Message | types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    name = data.get('name')
    phone = data.get('phone')
    mail = data.get('mail')
    education = data.get('education', 'не навчаюсь')
    faculty = data.get('faculty', 'не навчаюсь')
    main_msg_id = data.get("main_message_id")

    bot = event.bot
    chat_id = event.message.chat.id if isinstance(event, types.CallbackQuery) else event.chat.id

    confirmation_text = (
        f"📋 <b>Перевірте ваші дані перед підтвердженням:</b>\n\n"
        f"👤 <b>Ім'я:</b> {name}\n"
        f"📱 <b>Телефон:</b> {phone}\n"
        f"✉️ <b>Пошта:</b> {mail}\n"
        f"🎓 <b>Навчання:</b> {education}\n"
        if faculty != "не навчаюсь"
            f"🏛 <b>Факультет:</b> {faculty}\n\n"
        else
            f"\n"
        f"Все правильно? Натисни підтвердити для завершення або скасуй реєстрацію."
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="Підтвердити реєстрацію", callback_data="confirm_registration", style="success")
    builder.button(text="Скасувати", callback_data="cancel_registration", style="danger")
    builder.adjust(1)

    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(text=confirmation_text, reply_markup=builder.as_markup())
    else:
        if main_msg_id:
            try:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=main_msg_id,
                    text=confirmation_text,
                    reply_markup=builder.as_markup()
                )
            except Exception:
                new_msg = await event.answer(text=confirmation_text, reply_markup=builder.as_markup())
                await state.update_data(main_message_id=new_msg.message_id)
        else:
            new_msg = await event.answer(text=confirmation_text, reply_markup=builder.as_markup())
            await state.update_data(main_message_id=new_msg.message_id)

    await state.set_state(RegisterForm.waiting_confirmation)


@router.callback_query(RegisterForm.waiting_confirmation, F.data == "confirm_registration")
async def confirm_registration(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    name = data.get('name')
    phone = data.get('phone')
    mail = data.get('mail')
    education = data.get('education', 'не навчаюсь')
    faculty = data.get('faculty', 'не навчаюсь')

    tg_username = callback.from_user.username
    username_field = f"@{tg_username}" if tg_username else "немає"

    try:
        await add_user(
            tg_id=callback.from_user.id,
            username=username_field,
            name=name,
            phone=phone,
            mail=mail,
            education=education,
            faculty=faculty
        )

        asyncio.create_task(add_user_to_sheet(
            tg_id=callback.from_user.id,
            username=username_field,
            name=name,
            phone=phone,
            mail=mail,
            education=education,
            faculty=faculty
        ))

        builder = InlineKeyboardBuilder()
        builder.button(text="Головне меню", callback_data="controller_hub")

        success_text = (
            f"🎉 <b>Реєстрація успішна!</b>\n\n"
            f"👤 <b>Ім'я:</b> {name}\n"
            f"📱 <b>Телефон:</b> {phone}\n"
            f"✉️ <b>Пошта:</b> {mail}\n"
            f"🎓 <b>Навчання:</b> {education}\n"
            if faculty != "не навчаюсь"
                f"🏛 <b>Факультет:</b> {faculty}\n\n"
            else
                f"\n"
            f"Ти успішно зареєструвалися на захід. Змінити дані можна у вкладці 'Профіль'.\n"
            f"Очікуй на інформацію про час та місце проведення заходу."
        )

        await callback.message.edit_text(text=success_text, reply_markup=builder.as_markup())
        await state.clear()

    except Exception as e:
        logging.error(f"\033[31mПомилка БД під час реєстрації: {e}\033[0m")
        builder = InlineKeyboardBuilder()
        builder.button(text="Спробувати ще раз", callback_data="registration")

        await callback.message.edit_text(
            text="Виникла помилка під час збереження даних. Спробуйте ще раз.",
            reply_markup=builder.as_markup()
        )
        await state.clear()

    await callback.answer()


@router.callback_query(RegisterForm.waiting_confirmation, F.data == "cancel_registration")
async def cancel_registration(callback: types.CallbackQuery, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.button(text="Повернутись в меню", callback_data="controller_hub", style="primary")

    await callback.message.edit_text(
        text="❌ <b>Реєстрацію скасовано.</b> Твої дані не було збережено в системі.",
        reply_markup=builder.as_markup()
    )
    await state.clear()
    await callback.answer()