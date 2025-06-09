from aiogram import Router

from .add import router as add_router
from .delete import router as delete_router
from .menu import router as menu_router

router = Router()
router.include_router(menu_router)
router.include_router(add_router)
router.include_router(delete_router)
