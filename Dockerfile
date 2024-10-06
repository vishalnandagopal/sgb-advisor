FROM python:3.12-slim AS requirements-build

RUN ["pip","install","uv"]

COPY uv.lock uv.lock

COPY pyproject.toml pyproject.toml

RUN ["uv","export","--format","requirements-txt","--no-emit-project","-o", "requirements.txt"]

FROM python:3.12-slim AS final

# # Create a custom user with UID 1234 and GID 1234
# RUN groupadd -g 1234 customgroup && \
#     useradd -m -u 1234 -g customgroup vishal

# USER vishal

WORKDIR /sgb-advisor

COPY --from=requirements-build /requirements.txt requirements.txt

RUN ["pip","install","-r","requirements.txt"]

RUN ["python","--version"]

RUN ["playwright","install","firefox"]

RUN ["playwright","install-deps"]

COPY . .

CMD ["python","app.py"]