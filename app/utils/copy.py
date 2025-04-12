from datetime import datetime

from app.utils.utils import get_month_name_ru

start_msg = """<b>Привет 👋</b>

Меня зовут Синни, я друг СИН. Хотя мы с тобой уже знакомы — ведь в руках ты держишь пакет с моей фотографией 🛍

<b>В этом чат-боте буду рассказывать про новые розыгрыши. Включай уведомления, чтобы ничего не пропустить!</b>"""


def get_edit_anons_msg(anons):
    msg = f"""Дата начала: {anons.datetime_start.strftime("%d.%m.%y %H:%M")}
Дата окончания: {anons.datetime_end.strftime("%d.%m.%y %H:%M")}

Текст рассылки:
{anons.start_msg}

Текст подведения итогов:
{anons.end_msg}"""
    return msg

def get_sub_msg(date: datetime):
    day = date.day
    month = get_month_name_ru(date.month)
    msg = f"""Вижу твою подписку 📲
Теперь <b>ты участвуешь в розыгрыше</b> — жди результаты уже {day} {month} :)"""
    return msg

unsub_msg = """Не вижу подписки на канал СИН 💔
Это обязательное условие — пожалуйста, выполни его, чтобы участвовать в розыгрыше!"""

def get_end_anons_msg(winners, msg):
    winners_check = []
    for winner in winners:
        if winner.username:
            winners_check.append("@" + winner.username)
        else:
            winners_check.append(winner.full_name)
    winners_text = f"1. {winners_check[0]}\n2. {winners_check[1]}\n3. {winners_check[2]}"
    msg = msg.replace('!WINNERS', winners_text)
    return msg


