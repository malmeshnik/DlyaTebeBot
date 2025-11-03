from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from ..repo import MessageRepo, TgUserRepo
from ..keyboards.user import get_contact_keyboard
from ..states import UserStates

router = Router()
repo = MessageRepo()

@router.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    msg = await repo.get_message_by_name('start')
    await message.answer(
        text=msg.text,
        reply_markup=get_contact_keyboard(),
    )

    await state.set_state(UserStates.contact)

@router.message(UserStates.contact)
async def handle_contact(message: Message, state: FSMContext) -> None:
    msg = await repo.get_message_by_name('contact_received')
    phone_number = message.contact.phone_number

    #TODO додати логіку збереження номеру телефону користувача та перевірки чи існує в СРМ

    if phone_number:
        await message.answer(
            text=msg.text,
        )
    await state.clear()