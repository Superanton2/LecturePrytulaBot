from aiogram.utils.keyboard import InlineKeyboardBuilder

def create_main_keyboard(is_admin: bool= False) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button( text="🎟️ Зареєструватись", callback_data="registration")
    builder.button( text="🪪 Профіль", callback_data="profile")
    builder.adjust(1)

    if is_admin:
        builder.button( text="🔐 Панель Адміна", callback_data="admin_hub")
        builder.adjust(1)
    return builder


def create_main_admin_keyboard() -> InlineKeyboardBuilder:
        builder = InlineKeyboardBuilder()
        builder.button(text="👥 Менеджмент персоналу", callback_data="admin_staff_manage_new")
        builder.button(text="📊 Google табличка", url="SHEET_URL")
        builder.button(text="зупинити реєстрацію", callback_data="admin_stop_registration")
        builder.button(text="написати учасникам", callback_data="admin_write_participants") # зареєустровані / всі учасники

        builder.adjust(1)
        return builder


def create_admin_staff_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔑 Додати адміна", callback_data="add_admin")
    builder.button(text="🛡️Керування доступом", callback_data="permission_control")

    builder.button(text="Назад", callback_data="controller_hub", style="primary")
    builder.adjust(1)

    return builder