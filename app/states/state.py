from aiogram.fsm.state import StatesGroup, State

class Admin(StatesGroup):
    START = State()
    EDIT = State()
    NEWS_EDIT = State()
    ADD_START_DATETIME = State()
    ADD_NEWS_START_DATETIME = State()
    ADD_END_DATETIME = State()
    ADD_START_MSG = State()
    ADD_NEWS_START_MSG = State()
    ADD_START_IMAGE = State()
    ADD_NEWS_START_IMAGE = State()
    ADD_END_IMAGE = State()
    ADD_END_MSG = State()
    GET_ID = State()