from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder


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

def get_news_btn(news):
    btn = InlineKeyboardBuilder()
    for elem in news:
        btn.row(
            types.InlineKeyboardButton(
                text=str(elem.datetime_start.strftime("%d.%m.%y %H:%M")),
                callback_data=f"news_edit_{elem.id}")
        )
    btn.row(
        types.InlineKeyboardButton(
            text="Создать новую рассылку",
            callback_data=f"new_news")
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
            text="Изменить картинку рассылки",
            callback_data=f"editing_start_image_{anons_id}")
    )
    btn.row(
        types.InlineKeyboardButton(
            text="Изменить картинку подведения итогов",
            callback_data=f"editing_end_image_{anons_id}")
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


def get_edit_news_btn(news_id):
    btn = InlineKeyboardBuilder()
    btn.row(
        types.InlineKeyboardButton(
            text="Изменить дату начала рассылки",
            callback_data=f"update_datetime_{news_id}"))
    btn.row(
        types.InlineKeyboardButton(
            text="Изменить текст рассылки",
            callback_data=f"update_msg_{news_id}"))
    btn.row(
        types.InlineKeyboardButton(
            text="Изменить картинку рассылки",
            callback_data=f"update_image_{news_id}"))
    btn.row(
        types.InlineKeyboardButton(
            text="Удалить рассылку",
            callback_data=f"remove_{news_id}"))
    btn.row(
        types.InlineKeyboardButton(
            text="Назад",
            callback_data=f"news"))
    btn = btn.as_markup()
    return btn


def get_confirmation_btn(anons_id):
    btn = InlineKeyboardBuilder()
    btn.row(
        types.InlineKeyboardButton(
            text="Да, я хочу удалить розыгрыш",
            callback_data=f"confirmation_yes_{anons_id}")
    )
    btn.row(
        types.InlineKeyboardButton(
            text="Нет",
            callback_data=f"confirmation_no_{anons_id}")
    )
    btn = btn.as_markup()
    return btn

def get_accept_btn(news_id):
    btn = InlineKeyboardBuilder()
    btn.row(
        types.InlineKeyboardButton(
            text="Да, я хочу удалить рассылку",
            callback_data=f"accept_yes_{news_id}")
    )
    btn.row(
        types.InlineKeyboardButton(
            text="Нет",
            callback_data=f"accept_no_{news_id}")
    )
    btn = btn.as_markup()
    return btn


def get_check_sub_btn(anons_id):
    btn = InlineKeyboardBuilder()
    btn.row(
        types.InlineKeyboardButton(
            text="Участвовать",
            callback_data=f"check_sub_{anons_id}")
    )
    btn = btn.as_markup()
    return btn


def get_check_sub_btn_for_unsub(anons_id):
    btn = InlineKeyboardBuilder()
    btn.row(
        types.InlineKeyboardButton(
            text="Проверить подписку",
            callback_data=f"check_sub_{anons_id}")
    )
    btn = btn.as_markup()
    return btn