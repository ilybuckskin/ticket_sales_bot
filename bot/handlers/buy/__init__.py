from aiogram import Router

from .menu import router as menu_router
from .process import router as process_router

router = Router()
router.include_router(menu_router)
router.include_router(process_router)
