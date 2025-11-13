from aiogram.fsm.state import StatesGroup, State

class UserStates(StatesGroup):
    """Represents the states that a user can be in."""
    contact = State()