import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, PhotoSize

from bot.handlers.scan_ticket import process_ticket_scan


@pytest.mark.asyncio
async def test_process_ticket_scan_invalid_user(mocker):
    mock_message = mocker.Mock(spec=Message)
    mock_message.from_user = mocker.Mock()
    mock_message.from_user.id = 123
    mock_message.answer = mocker.AsyncMock()
    mock_message.photo = [mocker.Mock(spec=PhotoSize, file_id="fake_photo_id")]
    mock_message.bot = mocker.Mock()
    mock_message.bot.get_file = mocker.AsyncMock()
    mock_message.bot.download_file = mocker.AsyncMock(
        return_value=mocker.Mock(read=lambda: b"image")
    )

    mock_state = mocker.Mock(spec=FSMContext)
    mock_state.get_data = mocker.AsyncMock(return_value={"selected_event_id": 1})

    scalars_result = mocker.Mock()
    scalars_result.first.return_value = None

    execute_result = mocker.Mock()
    execute_result.scalars.return_value = scalars_result

    session_mock = mocker.AsyncMock()
    session_mock.execute.return_value = execute_result

    mocker.patch("bot.handlers.scan_ticket.select")
    mocker.patch(
        "bot.handlers.scan_ticket.AsyncSessionLocal",
        return_value=mocker.AsyncMock(
            __aenter__=mocker.AsyncMock(return_value=session_mock)
        ),
    )

    await process_ticket_scan(mock_message, mock_state)
    mock_message.answer.assert_called_with(
        "⛔ У вас нет прав для сканирования билетов."
    )
