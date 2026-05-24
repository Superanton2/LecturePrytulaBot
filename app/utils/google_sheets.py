import gspread
import asyncio
import os
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
