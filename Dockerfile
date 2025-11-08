ARG IMAGE_PLATFORM=linux/amd64
ARG BASEIMAGE=docker.io/library/python:3.14-slim-bookworm

FROM --platform=${IMAGE_PLATFORM} $BASEIMAGE AS final

RUN apt-get clean && \
    apt-get update && \
    apt-get upgrade --yes && \
    apt-get autoremove --yes

WORKDIR /sgb_advisor_runtime

COPY requirements.txt requirements.txt

RUN ["pip", "install", "-r", "requirements.txt"]

RUN ["playwright", "install", "--with-deps", "firefox"]

COPY . .

LABEL \
    org.opencontainers.image.title="SGB Advisor" \
    org.opencontainers.image.authors="Vishal Nandagopal (dev@vishalnandagopal.com)" \
    org.opencontainers.image.description="A tool to analyse Sovereign Gold Bonds and compare their yields" \
    org.opencontainers.image.url="https://github.com/vishalnandagopal/sgb-advisor" \
    org.opencontainers.image.source="https://github.com/vishalnandagopal/sgb-advisor.git" \
    org.opencontainers.image.documentation="https://github.com/vishalnandagopal/sgb-advisor/blob/master/README.md#running-the-app" \
    org.opencontainers.image.licenses="GPL-3.0-only"

ENTRYPOINT ["python3", "app.py"]
