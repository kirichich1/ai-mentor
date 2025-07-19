from aiogram.fsm.state import State, StatesGroup

class AnalysisStates(StatesGroup):
    waiting_for_profile = State()
    waiting_for_chat = State()
    waiting_for_target_profile = State()
    waiting_for_sos_context = State()
    waiting_for_user_info = State()
    waiting_for_other_profile = State()
    waiting_for_rescue_chat = State()
    waiting_for_message_interpretation = State()