ARG BASEIMAGE=python:3.13-slim-bullseye

FROM $BASEIMAGE AS final

WORKDIR /sgb_advisor

COPY requirements.txt requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip ["pip", "install", "-r", "requirements.txt"]

RUN ["playwright", "install", "--with-deps", "firefox"]

COPY . .

LABEL \
    org.opencontainers.image.title="SGB Advisor" \
    org.opencontainers.image.authors="Vishal Nandagopal (dev@vishalnandagopal.com)" \
    org.opencontainers.image.description="A tool to analyse Sovereign Gold Bonds and compare their yields" \
    org.opencontainers.image.source="https://github.com/vishalnandagopal/sgb-advisor" \
    org.opencontainers.image.url="https://github.com/vishalnandagopal/sgb-advisor"

CMD ["python", "app.py"]
