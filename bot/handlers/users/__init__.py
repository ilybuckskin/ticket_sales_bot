from aiogram import Router

from .block import router as block_router
from .list import router as list_router
from .menu import router as menu_router
from .role import router as role_router

router = Router()
router.include_router(menu_router)
router.include_router(list_router)
router.include_router(block_router)
router.include_router(role_router)
