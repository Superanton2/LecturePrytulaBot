from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import MetaData, Table, Column, Integer, BigInteger, String, Date, Time, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import select, insert

import os
from dotenv import load_dotenv

load_dotenv()
BD_ENGINE = os.getenv("BD_ENGINE")
SUPER_ADMINS = [int(x) for x in os.getenv("SUPER_ADMINS").split(",")]
engine = create_async_engine(BD_ENGINE, echo=False)
meta = MetaData()

admin_list = Table(
    "admin_list",
    meta,
    Column("telegram_id", BigInteger, primary_key=True),
    Column("name", String, nullable=False),
    Column("is_active", Boolean, default=True)
)

user_list = Table(
    "user_list",
    meta,
    Column("telegram_id", BigInteger, primary_key=True),
    Column("username", String, nullable=True),
    Column("name", String, nullable=False), # ПІБ
    Column("phone", String, nullable=False),
    Column("mail", String, nullable=False),
    Column("education", String, nullable=True),
    Column("faculty", String, nullable=True),
)


async def init_db():
    """
    database initialization. Start of all tables
    :return: None
    """
    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)

        # if no admins
        check_admins = await conn.execute(select(admin_list))
        if check_admins.fetchone() is None:

            insert_statement1 = insert(admin_list).values(telegram_id=SUPER_ADMINS[0], name="Anton")
            insert_statement2 = insert(admin_list).values(telegram_id=SUPER_ADMINS[1], name="Arina")
            await conn.execute(insert_statement1)
            await conn.execute(insert_statement2)
