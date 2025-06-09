help:
	@echo "Доступные команды:"
	@echo "  make install      Установить зависимости"
	@echo "  make lint         Запустить линтеры: black, flake8, isort"
	@echo "  make tests        Запустить тесты с pytest"
	@echo "  make run          Запустить приложение"


install:
	@echo "Установка зависимостей..."
	poetry install

lint:
	@echo "Запуск линтеров..."
	poetry run ruff check --select I --fix .
	poetry run ruff format .

test:
	@echo "Запуск тестов..."
	poetry run run pytest tests/

run:
	@echo "Запуск приложения..."
	poetry run python -m bot.main
