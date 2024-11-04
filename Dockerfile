FROM python:3.13-slim AS final

RUN --mount=type=cache,target=/root/.cache/pip ["pip", "install", "playwright"]

RUN ["playwright", "install", "--with-deps", "firefox"]

WORKDIR /sgb_advisor

COPY requirements.txt requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip ["pip", "install", "-r", "requirements.txt"]

COPY . .

CMD ["python", "app.py"]
