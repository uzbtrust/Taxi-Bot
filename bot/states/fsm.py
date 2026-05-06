from aiogram.fsm.state import State, StatesGroup


class AuthStates(StatesGroup):
    waiting_phone = State()
    waiting_code = State()
    waiting_2fa = State()


class GroupStates(StatesGroup):
    select_account = State()
    waiting_input = State()


class BroadcastStates(StatesGroup):
    waiting_message = State()
    confirming = State()
