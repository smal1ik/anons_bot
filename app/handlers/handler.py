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
    set_participant_user, update_active
from app.states.state import Admin

router_main = Router()
CHANNEL_ID = int(config('CHANNEL_ID'))

ADMINS_ID = [654557598, 365276269]

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
                await message.answer(text=anons.start_msg, parse_mode="HTML", disable_web_page_preview=True, reply_markup=kb. get_check_sub_btn(anons.id))
        elif not user.is_active:
            await update_active(user.tg_id)

# ===========================================================================================================
@router_main.message(Command('anons'))
async def cmd_message(message: types.Message, state: FSMContext, bot: Bot, command: Command):
    if message.from_user.id in ADMINS_ID:
        anons = await get_actual_anons()
        await message.answer("Розыгрыши", reply_markup=kb.get_anons_btn(anons))
        await state.clear()


@router_main.callback_query(F.data == 'anons')
async def answer_message(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    if callback.from_user.id in ADMINS_ID:
        anons = await get_actual_anons()
        await callback.message.answer("Розыгрыши", reply_markup=kb.get_anons_btn(anons))
        await state.clear()
# ===========================================================================================================


# ===========================================================================================================
@router_main.callback_query(F.data.contains('anons_edit'))
async def answer_message(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    _, _, anons_id = callback.data.split('_')
    anons = await get_anons(anons_id)
    await callback.message.answer(cp.get_edit_anons_msg(anons), reply_markup=kb.get_edit_anons_btn(anons_id), parse_mode="HTML")
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
    else:
        if time_edit == 'start':
            await callback.message.answer("Отправь новую дату начала (дд.мм.гг чч:мм)")
        else:
            await callback.message.answer("Отправь новую дату окончания (дд.мм.гг чч:мм)")
    # помещаем всю инфу в редис и новое состояние
    await state.set_state(Admin.EDIT)
    await state.set_data({"time_edit": time_edit, "type_edit": type_edit, "anons_id": anons_id})

@router_main.message(Admin.EDIT)
async def message(message: types.Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    time_edit = data.get("time_edit")
    type_edit = data.get("type_edit")
    anons_id = data.get("anons_id")
    await edit_anons(anons_id=anons_id, type_edit=type_edit, time_edit=time_edit, new_data=message.text)

    anons = await get_anons(anons_id)
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
    await message.answer("Введите текст для подведения итогов")
    await state.set_state(Admin.ADD_END_MSG)

@router_main.message(Admin.ADD_END_MSG)
async def message(message: types.Message, bot: Bot, state: FSMContext):
    end_msg = message.text
    data = await state.get_data()
    await state.set_state(Admin.ADD_END_MSG)
    await new_anons(datetime_start=datetime.strptime(data.get('datetime_start'), "%d.%m.%y %H:%M"),
                    datetime_end=datetime.strptime(data.get('datetime_end'), "%d.%m.%y %H:%M"),
                    start_msg=data.get('start_msg'),
                    end_msg=end_msg)

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
        await callback.message.answer(cp.unsub_msg, parse_mode="HTML", reply_markup=kb.get_check_sub_btn_for_unsub(anons_id))
