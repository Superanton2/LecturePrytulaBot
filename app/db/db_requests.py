from sqlalchemy import select, insert, update
from app.db.db_setup import engine, admin_list, user_list

async def add_user(tg_id: int, name: str, phone: str, mail: str,
                   education: str = "не навчаюсь", faculty: str = "не навчаюсь") -> None:
    """
    add user to db
    :param tg_id: telegram id of user
    :param name: Ures name
    :param phone: +380 ...
    :param mail: example@google.com
    :param education: type of education
    :param faculty: name of faculty

    :return: None
    """
    async with engine.begin() as conn:
        insert_statement = insert(user_list).values(
            telegram_id=tg_id,
            name=name,
            phone=phone,
            mail=mail,
            education=education,
            faculty=faculty
        )
        await conn.execute(insert_statement)

async def get_user(tg_id: int):
    """
    Fing user data in db
    :param tg_id:
    :return: User data or None is there are no user in db
    """
    async with engine.begin() as conn:
        select_statement = select(user_list).where(user_list.c.telegram_id == tg_id)
        result = await conn.execute(select_statement)
        return result.fetchone()

async def get_all_users():
    async with engine.begin() as conn:
        select_statement = select(user_list)
        result = await conn.execute(select_statement)
        return result.fetchall()

async def update_user_field(tg_id: int, field_name: str, new_value: str) -> None:
    """
    update particular field in user db
    :param tg_id: id of user
    :param field_name: field to change. Have to be 'name', 'phone', 'mail', 'education' or 'faculty'
    :param new_value: value to write
    :return: None
    """
    async with engine.begin() as conn:
        update_data = {field_name: new_value}

        update_statement = (
            update(user_list)
            .where(user_list.c.telegram_id == tg_id)
            .values(**update_data)
        )
        await conn.execute(update_statement)

async def is_admin(user_id: int) -> bool:
    """
    Checks whether a person has an ACTIVE status in his role
    """

    async with engine.begin() as conn:
        select_statement = select(admin_list).where(
            (admin_list.c.telegram_id == user_id) & (admin_list.c.is_active == True)
        )

        result = await conn.execute(select_statement)
        return result.fetchone() is not None