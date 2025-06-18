import asyncio
from datetime import datetime

from aiogram.filters.command import Command
from aiogram import types, F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.utils.deep_linking import decode_payload, encode_payload
from decouple import config

import app.utils.copy as cp
import app.keyboards.keyboard as kb
from app.database.requests import get_user, add_user, get_actual_anons, get_anons, edit_anons, remove_anons, new_anons, \
    set_participant_user, update_active, get_stats, get_actual_news, new_news, get_news, remove_news, edit_news, \
    get_winners_anons
from app.states.state import Admin

router_main = Router()
CHANNEL_ID = int(config('CHANNEL_ID'))

ADMINS_ID = [654557598, 365276269, 1269975870, 7927932978]

@router_main.message(Command('test_winners'))
async def cmd_message(message: types.Message, state: FSMContext, bot: Bot, command: Command):
    if message.from_user.id in ADMINS_ID:
        winners = await get_winners_anons()
        await message.answer(f"{winners[0].username}\n{winners[1].username}\n{winners[2].username}")


@router_main.message(Command('start'))
async def cmd_message(message: types.Message, state: FSMContext, bot: Bot, command: Command):
    if message.from_user.id == message.chat.id:
        user = await get_user(message.from_user.id)
        await message.answer_photo(caption=cp.start_msg, photo=FSInputFile('imgs/start_img.png'), parse_mode='HTML')
        if not user:
            await add_user(message.from_user.id, message.from_user.first_name, message.from_user.username,
                           message.from_user.full_name)
            anons = await get_actual_anons(for_user=True)
            if anons:
                await message.answer(text=anons.start_msg, parse_mode="HTML", disable_web_page_preview=True,
                                     reply_markup=kb.get_check_sub_btn(anons.id))
        elif not user.is_active:
            await update_active(user.tg_id)


# ===========================================================================================================
@router_main.message(Command('get_id'))
async def cmd_message(message: types.Message, state: FSMContext, bot: Bot, command: Command):
    if message.from_user.id in ADMINS_ID:
        await state.clear()
        await message.answer("Загрузи гифку")
        await state.set_state(Admin.GET_ID)

@router_main.message(Admin.GET_ID)
async def message(message: types.Message, bot: Bot, state: FSMContext):
    await state.clear()
    if message.animation and message.animation.file_id:
        await message.answer(message.animation.file_id)
        await message.answer_animation(message.animation.file_id)
    elif message.document and message.document.file_id:
        await message.answer(message.document.file_id)
        await message.answer_animation(message.document.file_id)

@router_main.message(Command('anons'))
async def cmd_message(message: types.Message, state: FSMContext, bot: Bot, command: Command):
    if message.from_user.id in ADMINS_ID:
        anons = await get_actual_anons()
        await message.answer("Розыгрыши", reply_markup=kb.get_anons_btn(anons))
        await state.clear()


@router_main.message(Command('news'))
async def cmd_message(message: types.Message, state: FSMContext, bot: Bot, command: Command):
    if message.from_user.id in ADMINS_ID:
        news = await get_actual_news()
        await message.answer("Рассылки", reply_markup=kb.get_news_btn(news))
        await state.clear()


@router_main.message(Command('stats'))
async def cmd_message(message: types.Message, state: FSMContext, bot: Bot, command: Command):
    if message.from_user.id in ADMINS_ID:
        stats = await get_stats()
        await message.answer(f"Всего людей: {stats[0]}\nУчастников: {stats[1]}")


@router_main.callback_query(F.data == 'anons')
async def answer_message(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    if callback.from_user.id in ADMINS_ID:
        anons = await get_actual_anons()
        await callback.message.answer("Розыгрыши", reply_markup=kb.get_anons_btn(anons))
        await state.clear()


@router_main.callback_query(F.data == 'news')
async def answer_message(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    if callback.from_user.id in ADMINS_ID:
        news = await get_actual_news()
        await message.answer("Рассылки", reply_markup=kb.get_news_btn(news))
        await state.clear()


# ===========================================================================================================


# ===========================================================================================================
@router_main.callback_query(F.data.contains('anons_edit'))
async def answer_message(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    _, _, anons_id = callback.data.split('_')
    anons = await get_anons(anons_id)
    if anons.start_image:
        await callback.message.answer_photo(photo=anons.start_image, caption='Картинка для рассылки')
    if anons.end_image:
        await callback.message.answer_photo(photo=anons.end_image, caption='Картинка для подведения итогов')
    await callback.message.answer(cp.get_edit_anons_msg(anons), reply_markup=kb.get_edit_anons_btn(anons_id),
                                  parse_mode="HTML")
    await state.clear()


@router_main.callback_query(F.data.contains('delete'))
async def answer_message(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    _, anons_id = callback.data.split('_')
    await callback.message.answer("Ты уверен?", reply_markup=kb.get_confirmation_btn(anons_id))


@router_main.callback_query(F.data.contains('confirmation'))
async def answer_message(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    _, accept, anons_id = callback.data.split('_')
    if accept == 'yes':
        await remove_anons(anons_id)
        await state.clear()
    anons = await get_actual_anons()
    await callback.message.answer("Розыгрыши", reply_markup=kb.get_anons_btn(anons))


@router_main.callback_query(F.data.contains('editing'))
async def answer_message(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    _, time_edit, type_edit, anons_id = callback.data.split('_')
    if type_edit == 'msg':
        if time_edit == 'start':
            await callback.message.answer("Отправь новый текст для анонса")
        else:
            await callback.message.answer("Отправь новый текст для подведения итогов")
    elif type_edit == 'datetime':
        if time_edit == 'start':
            await callback.message.answer("Отправь новую дату начала (дд.мм.гг чч:мм)")
        else:
            await callback.message.answer("Отправь новую дату окончания (дд.мм.гг чч:мм)")
    elif type_edit == 'image':
        if time_edit == 'start':
            await callback.message.answer("Отправь новую картинку для рассылки")
        else:
            await callback.message.answer("Отправь новую картинку для подведения итогов")
    # помещаем всю инфу в редис и новое состояние
    await state.set_state(Admin.EDIT)
    await state.set_data({"time_edit": time_edit, "type_edit": type_edit, "anons_id": anons_id})


@router_main.message(Admin.EDIT)
async def message(message: types.Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    time_edit = data.get("time_edit")
    type_edit = data.get("type_edit")
    anons_id = data.get("anons_id")
    if type_edit == 'image' and message.photo:
        new_data = message.photo[-1].file_id
    else:
        new_data = message.text
    await edit_anons(anons_id=anons_id, type_edit=type_edit, time_edit=time_edit, new_data=new_data)
    anons = await get_anons(anons_id)
    if anons.start_image:
        await message.answer_photo(photo=anons.start_image, caption='Картинка для рассылки')
    if anons.end_image:
        await message.answer_photo(photo=anons.end_image, caption='Картинка для подведения итогов')
    await message.answer(cp.get_edit_anons_msg(anons), reply_markup=kb.get_edit_anons_btn(anons_id), parse_mode="HTML")
    await state.clear()
# ===========================================================================================================
@router_main.callback_query(F.data == 'new_anons')
async def answer_message(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback.message.answer("Введите дату начала запуска рассылки (дд.мм.гг чч:мм)")
    await state.set_state(Admin.ADD_START_DATETIME)


@router_main.message(Admin.ADD_START_DATETIME)
async def message(message: types.Message, bot: Bot, state: FSMContext):
    await state.update_data({"datetime_start": message.text})
    await message.answer("Введите дату подведения итогов (дд.мм.гг чч:мм)")
    await state.set_state(Admin.ADD_END_DATETIME)


@router_main.message(Admin.ADD_END_DATETIME)
async def message(message: types.Message, bot: Bot, state: FSMContext):
    await state.update_data({"datetime_end": message.text})
    await message.answer("Введите текст для рассылки")
    await state.set_state(Admin.ADD_START_MSG)


@router_main.message(Admin.ADD_START_MSG)
async def message(message: types.Message, bot: Bot, state: FSMContext):
    await state.update_data({"start_msg": message.text})
    await message.answer("Отправьте изображение для рассылки, если его нет, введите (нет)")
    await state.set_state(Admin.ADD_START_IMAGE)


@router_main.message(Admin.ADD_START_IMAGE)
async def message(message: types.Message, bot: Bot, state: FSMContext):
    if message.text and 'нет' in message.text.lower():
        await message.answer("Отправьте изображение для подведения итогов, если его нет, введите (нет)")
        await state.update_data({"start_image": ""})
        await state.set_state(Admin.ADD_END_IMAGE)
    elif message.photo:
        image_id = message.photo[-1].file_id
        await state.update_data({"start_image": image_id})
        await message.answer("Отправьте изображение для подведения итогов, если его нет, введите (нет)")
        await state.set_state(Admin.ADD_END_IMAGE)
    else:
        await message.answer("Ой, ой, что то не так")


@router_main.message(Admin.ADD_END_IMAGE)
async def message(message: types.Message, bot: Bot, state: FSMContext):
    if message.text and 'нет' in message.text.lower():
        await message.answer("Введите текст для подведения итогов")
        await state.update_data({"end_image": ""})
        await state.set_state(Admin.ADD_END_MSG)
    elif message.photo:
        image_id = message.photo[-1].file_id
        await state.update_data({"end_image": image_id})
        await message.answer("Введите текст для подведения итогов")
        await state.set_state(Admin.ADD_END_MSG)
    else:
        await message.answer("Ой, ой, что то не так")


@router_main.message(Admin.ADD_END_MSG)
async def message(message: types.Message, bot: Bot, state: FSMContext):
    end_msg = message.text
    data = await state.get_data()
    await state.set_state(Admin.ADD_END_MSG)
    await new_anons(datetime_start=datetime.strptime(data.get('datetime_start'), "%d.%m.%y %H:%M"),
                    datetime_end=datetime.strptime(data.get('datetime_end'), "%d.%m.%y %H:%M"),
                    start_msg=data.get('start_msg'),
                    end_msg=end_msg,
                    start_image=data.get('start_image'),
                    end_image=data.get('end_image'))

    anons = await get_actual_anons()
    await message.answer("Розыгрыши", reply_markup=kb.get_anons_btn(anons))
    await state.clear()


@router_main.callback_query(F.data.contains('check_sub'))
async def answer_message(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    _, _, anons_id = callback.data.split('_')
    user_channel_status = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=callback.from_user.id)
    if user_channel_status.status != 'left':
        anons = await get_anons(anons_id)
        await set_participant_user(callback.from_user.id)
        await callback.message.answer(cp.get_sub_msg(anons.datetime_end), parse_mode="HTML")
    else:
        await callback.message.answer(cp.unsub_msg, parse_mode="HTML",
                                      reply_markup=kb.get_check_sub_btn_for_unsub(anons_id))


# ============================================================================================================================

@router_main.callback_query(F.data == 'new_news')
async def answer_message(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    await callback.message.answer("Введите дату начала запуска рассылки (дд.мм.гг чч:мм)")
    await state.set_state(Admin.ADD_NEWS_START_DATETIME)


@router_main.message(Admin.ADD_NEWS_START_DATETIME)
async def message(message: types.Message, bot: Bot, state: FSMContext):
    await state.update_data({"datetime_start": message.text})
    await message.answer("Введите текст для рассылки")
    await state.set_state(Admin.ADD_NEWS_START_MSG)


@router_main.message(Admin.ADD_NEWS_START_MSG)
async def message(message: types.Message, bot: Bot, state: FSMContext):
    await state.update_data({"msg": message.text})
    await message.answer("Отправьте картинку для рассылки, если не нужно, напишите (нет)")
    await state.set_state(Admin.ADD_NEWS_START_IMAGE)


@router_main.message(Admin.ADD_NEWS_START_IMAGE)
async def message(message: types.Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    if message.text and 'нет' in message.text.lower():
        image_id = ""
    elif message.photo:
        image_id = message.photo[-1].file_id
    else:
        await message.answer("Ой, ой, что то не так")
        return
    await new_news(datetime_start=datetime.strptime(data.get('datetime_start'), "%d.%m.%y %H:%M"),
                   msg=data.get('msg'),
                   image=image_id)
    news = await get_actual_news()
    await message.answer("Рассылки", reply_markup=kb.get_news_btn(news))
    await state.clear()

# ======================================================================================================================

@router_main.callback_query(F.data.contains('news_edit'))
async def answer_message(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    _, _, news_id = callback.data.split('_')
    news = await get_news(news_id)
    if news.image:
        await callback.message.answer_photo(photo=news.image, caption='Картинка для рассылки')
    await callback.message.answer(cp.get_edit_news_msg(news), reply_markup=kb.get_edit_news_btn(news_id),
                                  parse_mode="HTML")
    await state.clear()


@router_main.callback_query(F.data.contains('remove'))
async def answer_message(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    _, news_id = callback.data.split('_')
    await callback.message.answer("Ты уверен?", reply_markup=kb.get_accept_btn(news_id))


@router_main.callback_query(F.data.contains('accept'))
async def answer_message(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    _, accept, news_id = callback.data.split('_')
    if accept == 'yes':
        await remove_news(news_id)
        await state.clear()
    news = await get_actual_news()
    await callback.message.answer("Рассылки", reply_markup=kb.get_news_btn(news))


@router_main.callback_query(F.data.contains('update'))
async def answer_message(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    _, type_edit, news_id = callback.data.split('_')
    if type_edit == 'msg':
        await callback.message.answer("Отправь новый текст для рассылки")
    elif type_edit == 'datetime':
        await callback.message.answer("Отправь новую дату рассылки (дд.мм.гг чч:мм)")
    elif type_edit == 'image':
        await callback.message.answer("Отправь новую картинку для рассылки")
    await state.set_state(Admin.NEWS_EDIT)
    await state.set_data({"type_edit": type_edit, "news_id": news_id})


@router_main.message(Admin.NEWS_EDIT)
async def message(message: types.Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    type_edit = data.get("type_edit")
    news_id = data.get("news_id")
    if type_edit == 'image' and message.photo:
        new_data = message.photo[-1].file_id
    else:
        new_data = message.text
    await edit_news(news_id=news_id, type_edit=type_edit, new_data=new_data)
    news = await get_news(news_id)
    if news.image:
        await message.answer_photo(photo=news.image, caption='Картинка для рассылки')
    await message.answer(cp.get_edit_news_msg(news), reply_markup=kb.get_edit_news_btn(news_id), parse_mode="HTML")
    await state.clear()
