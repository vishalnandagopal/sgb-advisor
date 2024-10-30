FROM python:3.12-slim AS requirements-build

RUN ["pip","install","uv"]

COPY pyproject.toml pyproject.toml

RUN ["uv","export","--no-dev","--format","requirements-txt","--no-emit-project","-o", "requirements.txt"]

FROM python:3.12-slim AS final

WORKDIR /sgb-advisor

COPY --from=requirements-build /requirements.txt requirements.txt

RUN ["pip","install","-r","requirements.txt"]

RUN ["python","--version"]

RUN ["playwright","install","firefox"]

RUN ["playwright","install-deps"]

COPY . .

CMD ["python","app.py"]
