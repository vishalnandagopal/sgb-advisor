FROM python:3.13-slim AS final

WORKDIR /sgb-advisor

COPY requirements.txt requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip ["pip", "install", "-r", "requirements.txt"]

RUN ["playwright", "install", "--with-deps", "firefox"]

COPY . .

CMD ["python", "app.py"]
