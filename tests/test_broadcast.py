import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.handlers.broadcast import start_broadcast


@pytest.mark.asyncio
async def test_start_broadcast(mocker):
    message = mocker.Mock(spec=Message)
    message.answer = mocker.AsyncMock()
    state = mocker.Mock(spec=FSMContext)
    state.set_state = mocker.AsyncMock()

    await start_broadcast(message, state)
    state.set_state.assert_called()
    message.answer.assert_called_with("✉️ Введите текст для рассылки:")
