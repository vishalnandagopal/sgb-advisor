ARG BASEIMAGE=python:3.13-slim-bullseye

FROM $BASEIMAGE AS final

WORKDIR /sgb_advisor

COPY requirements.txt requirements.txt

RUN --mount=type=cache,id=pip-cache-$BASEIMAGE,target=/root/.cache/pip ["pip", "install", "-r", "requirements.txt"]

RUN ["playwright", "install", "--with-deps", "firefox"]

COPY . .

CMD ["python", "app.py"]
