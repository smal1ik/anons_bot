from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


channel_btn = InlineKeyboardBuilder()
channel_btn.row(
    types.InlineKeyboardButton(
        text="Подписаться на канал",
        url="https://t.me/sin_russia"
    )
)

def get_anons_btn(anons):
    btn = InlineKeyboardBuilder()
    for elem in anons:
        btn.row(
            types.InlineKeyboardButton(
                text=str(elem.datetime_start.strftime("%d.%m.%y %H:%M")),
                callback_data=f"anons_edit_{elem.id}")
        )
    btn.row(
        types.InlineKeyboardButton(
            text="Создать новый розыгрыш",
            callback_data=f"new_anons")
    )
    btn = btn.as_markup()
    return btn

def get_edit_anons_btn(anons_id):
    btn = InlineKeyboardBuilder()
    btn.row(
        types.InlineKeyboardButton(
            text="Изменить дату начала",
            callback_data=f"editing_start_datetime_{anons_id}")
    )
    btn.row(
        types.InlineKeyboardButton(
            text="Изменить дату окончания",
            callback_data=f"editing_end_datetime_{anons_id}")
    )
    btn.row(
        types.InlineKeyboardButton(
            text="Изменить текст анонса",
            callback_data=f"editing_start_msg_{anons_id}")
    )
    btn.row(
        types.InlineKeyboardButton(
            text="Изменить текст подведения итогов",
            callback_data=f"editing_end_msg_{anons_id}")
    )
    btn.row(
        types.InlineKeyboardButton(
            text="Удалить розыгрыш",
            callback_data=f"delete_{anons_id}")
    )
    btn.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=f"anons")
    )
    btn = btn.as_markup()
    return btn


def get_check_sub_btn(anons_id):
    btn = InlineKeyboardBuilder()
    btn.row(
        types.InlineKeyboardButton(
            text="Учавствовать",
            callback_data=f"check_sub_{anons_id}")
    )
    btn = btn.as_markup()
    return btn