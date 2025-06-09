import pytest
from aiogram.filters.command import CommandObject
from aiogram.types import Message

from bot.handlers.buy_ticket import buy_ticket


@pytest.mark.asyncio
async def test_buy_ticket_no_events(mocker):
    message = mocker.Mock(spec=Message)
    message.text = "Купить билет"
    message.answer = mocker.AsyncMock()

    scalars_result = mocker.Mock()
    scalars_result.all.return_value = []

    execute_result = mocker.Mock()
    execute_result.scalars.return_value = scalars_result

    session_mock = mocker.AsyncMock()
    session_mock.execute.return_value = execute_result

    mocker.patch("bot.handlers.buy_ticket.select")
    mocker.patch(
        "bot.handlers.buy_ticket.AsyncSessionLocal",
        return_value=mocker.AsyncMock(
            __aenter__=mocker.AsyncMock(return_value=session_mock)
        ),
    )

    await buy_ticket(message, CommandObject(command="test"))
    message.answer.assert_called_with("Сейчас нет доступных мероприятий.")
