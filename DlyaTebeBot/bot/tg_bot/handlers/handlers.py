from aiogram import Router

from . import inline, menu, user

router = Router()
router.include_routers(user.router, menu.router, inline.router)
