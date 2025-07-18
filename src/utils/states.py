from aiogram.fsm.state import State, StatesGroup

class AnalysisStates(StatesGroup):
    waiting_for_profile = State()
    waiting_for_chat = State()
    waiting_for_target_profile = State()
    waiting_for_sos_context = State()  # Новое состояние для SOS-кнопки
    waiting_for_user_info = State()  # Для генерации анкеты
    waiting_for_other_profile = State()  # Для анализа чужой анкеты