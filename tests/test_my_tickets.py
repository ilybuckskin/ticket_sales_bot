import pytest
from aiogram.filters.command import CommandObject
from aiogram.types import Message

from bot.handlers.my_tickets import my_tickets


@pytest.mark.asyncio
async def test_my_tickets_none(mocker):
    message = mocker.Mock(spec=Message)
    message.text = "Мои билеты"
    message.from_user = mocker.Mock()
    message.from_user.id = 42
    message.answer = mocker.AsyncMock()

    user_result = mocker.Mock()
    user_result.first.return_value = mocker.Mock(id=1)

    ticket_result = mocker.Mock()
    ticket_result.all.return_value = []

    session_mock = mocker.AsyncMock()
    session_mock.execute.side_effect = [
        mocker.Mock(scalars=mocker.Mock(return_value=user_result)),
        mocker.Mock(scalars=mocker.Mock(return_value=ticket_result)),
    ]

    mocker.patch("bot.handlers.my_tickets.select")
    mocker.patch(
        "bot.handlers.my_tickets.AsyncSessionLocal",
        return_value=mocker.AsyncMock(
            __aenter__=mocker.AsyncMock(return_value=session_mock)
        ),
    )

    await my_tickets(message, CommandObject(command="test"))
    message.answer.assert_called_with("📭 У вас пока нет купленных билетов.")
