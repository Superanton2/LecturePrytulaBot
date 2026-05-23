import datetime

from sqlalchemy import select, insert, update, func, delete
from app.db.db_setup import engine, bookings, admin_list, worker_list, user_list, cars

import os
from dotenv import load_dotenv

load_dotenv()

async def is_admin(user_id: int):
    return True