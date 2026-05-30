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


async def add_user_to_sheet(tg_id: int, username: str, name: str, phone: str,
                            mail: str, education: str, faculty: str):
    """Додає нового зареєстрованого користувача в таблицю"""
    try:
        row = [str(tg_id), username, name, phone, mail, education, faculty]
        await asyncio.to_thread(_append_row_sync, "Users", row)
        print(f"✅ Користувача {name} успішно додано в Sheets!")
    except Exception as e:
        print(f"❌ ПОМИЛКА додавання користувача в Sheets: {e}")


def _update_user_sync(tg_id: str, field: str, new_value: str):
    """Синхронно шукає юзера за ID і оновлює вказане поле"""
    sh = get_sheet()
    ws = sh.worksheet("Users")
    try:
        cell = ws.find(str(tg_id), in_column=1)
        if cell:
            col_map = {
                "username": "B",
                "name": "C",
                "phone": "D",
                "mail": "E",
                "education": "F",
                "faculty": "G"
            }
            if field in col_map:
                cell_label = f"{col_map[field]}{cell.row}"
                ws.update_acell(cell_label, new_value)
                print(f"✅ Sheets: Оновлено ID {tg_id}, поле {field} -> {new_value}")
        else:
            print(f"⚠️ Sheets: Користувача {tg_id} не знайдено для оновлення.")
    except Exception as e:
        print(f"❌ Sheets: Помилка оновлення користувача: {e}")


async def update_user_in_sheet(tg_id: int, field: str, new_value: str):
    """
    Оновлює дані користувача.
    Доступні поля (field): 'name', 'username', 'phone', 'mail', 'education', 'faculty'
    """
    await asyncio.to_thread(_update_user_sync, str(tg_id), field, new_value)
