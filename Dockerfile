FROM python:3.12-slim AS final

WORKDIR /sgb-advisor

COPY requirements.txt requirements.txt

RUN ["pip","install","-r","requirements.txt"]

RUN ["playwright","install","firefox"]

RUN ["playwright","install-deps"]

COPY . .

CMD ["python","app.py"]
