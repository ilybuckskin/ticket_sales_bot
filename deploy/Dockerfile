FROM python:3.12

# Poetry
ENV POETRY_VERSION=1.8.2
RUN pip install "poetry==$POETRY_VERSION"
RUN apt update && apt-get install libzbar0 -y

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction

COPY . .

CMD ["poetry", "run", "python", "-m", "bot.main"]