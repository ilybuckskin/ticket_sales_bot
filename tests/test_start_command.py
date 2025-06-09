import pytest
from aiogram.types import Message

from bot.main import cmd_start


@pytest.mark.asyncio
async def test_cmd_start_new_user(mocker):
    message = mocker.Mock(spec=Message)
    message.from_user = mocker.Mock()
    message.from_user.id = 1001
    message.from_user.username = "testuser"
    message.answer = mocker.AsyncMock()

    scalars_result = mocker.Mock()
    scalars_result.first.return_value = None

    execute_result = mocker.Mock()
    execute_result.scalars.return_value = scalars_result

    session_mock = mocker.AsyncMock()
    session_mock.execute.return_value = execute_result
    session_mock.add = mocker.Mock()
    session_mock.commit = mocker.AsyncMock()

    mocker.patch("bot.main.select")
    mocker.patch(
        "bot.main.AsyncSessionLocal",
        return_value=mocker.AsyncMock(
            __aenter__=mocker.AsyncMock(return_value=session_mock)
        ),
    )

    await cmd_start(message)

    message.answer.assert_awaited()
    session_mock.add.assert_called_once()
    session_mock.commit.assert_awaited_once()
