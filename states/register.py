from aiogram.dispatcher.filters.state import State, StatesGroup


class RegisterState(StatesGroup):
    name = State()
    phone = State()
    ask = State()


class AdminAnswerState(StatesGroup):
    user_id = State()


__all__ = [RegisterState, AdminAnswerState]
