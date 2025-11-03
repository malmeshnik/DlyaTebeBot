from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import CommandStart
from aiogram.enums import ParseMode

from ..repo import MessageRepo
from ..keyboards.user import get_contact_keyboard

router = Router()
repo = MessageRepo()

@router.message(CommandStart())
async def start(message: Message) -> None:
    msg = await repo.get_message_by_name('start')
    await message.answer(
        text=msg.text,
        reply_markup=get_contact_keyboard(),
    )