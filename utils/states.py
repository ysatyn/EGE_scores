from telebot import custom_filters
from telebot.states import State, StatesGroup

class SpecialStates(StatesGroup):
    AWAITING_USER_DESIRED_SCORE = State()
    WAITING_FOR_SCORE_INPUT = State()