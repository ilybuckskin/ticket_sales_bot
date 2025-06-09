from aiogram import Router

from .contact_manager import router as contact_manager_router

router = Router()
router.include_router(contact_manager_router)
