import gspread
import asyncio
import os
from sqlalchemy import select
from app.db.db_setup import engine, admin_list, user_list
from dotenv import load_dotenv

load_dotenv()


def get_sheet():
    gc = gspread.service_account(filename='credentials.json')
    return gc.open(os.getenv("LOG_SHEET_NAME"))


def _append_row_sync(sheet_name: str, row_data: list):
    sh = get_sheet()
    ws = sh.worksheet(sheet_name)
    ws.append_row(row_data)


async def add_user_to_sheet(tg_id: int, name: str, phone: str,
                            mail: str, education: str, faculty: str):
    """Додає нового зареєстрованого користувача в таблицю"""
    try:
        row = [str(tg_id), name, phone, mail, education, faculty]
        await asyncio.to_thread(_append_row_sync, "Users", row)
        print(f"✅ Користувача {name} успішно додано в Sheets!")
    except Exception as e:
        print(f"❌ ПОМИЛКА додавання користувача в Sheets: {e}")


def _update_user_sync(tg_id: str, field: str, new_value: str):
    """Синхронно шукає юзера за ID і оновлює вказане поле"""
    sh = get_sheet()
    ws = sh.worksheet("Users")
    try:
        # Шукаємо ID у першій колонці (Колонка A)
        cell = ws.find(str(tg_id), in_column=1)
        if cell:
            # Мапа колонок відповідно до структури:
            # A: tg_id, B: name, C: phone, D: mail, E: education, F: faculty
            col_map = {
                "name": "B",
                "phone": "C",
                "mail": "D",
                "education": "E",
                "faculty": "F"
            }
            if field in col_map:
                ws.update(range_name=f"{col_map[field]}{cell.row}", values=[[new_value]])
    except Exception as e:
        print(f"❌ Помилка оновлення користувача в Sheets: {e}")


async def update_user_in_sheet(tg_id: int, field: str, new_value: str):
    """
    Оновлює дані користувача.
    Доступні поля (field): 'name', 'phone', 'mail', 'education', 'faculty'
    """
    await asyncio.to_thread(_update_user_sync, str(tg_id), field, new_value)


def _sync_admins_sync(admin_data: list):
    """Синхронна функція для повного перезапису списку адмінів"""
    sh = get_sheet()
    ws_admins = sh.worksheet("Admins")

    # Очищаємо старі дані (залишаємо перший рядок під заголовки)
    ws_admins.batch_clear(["A2:C1000"])

    if admin_data:
        ws_admins.update(range_name="A2", values=admin_data)


async def sync_admins_to_sheet():
    """Асинхронно дістає всіх адмінів з БД і синхронізує їх з таблицею"""
    admin_rows = []

    async with engine.begin() as conn:
        admins_result = await conn.execute(select(admin_list))
        admins = list(admins_result.fetchall())

    # Сортуємо: спочатку активні
    admins.sort(key=lambda x: x.is_active, reverse=True)

    for a in admins:
        status = "Активний" if a.is_active else "Деактивований"
        admin_rows.append([str(a.telegram_id), a.name, status])

    await asyncio.to_thread(_sync_admins_sync, admin_rows)