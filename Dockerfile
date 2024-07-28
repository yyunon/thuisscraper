FROM python:3.10
WORKDIR /code
COPY ./pyproject.toml /code/pyproject.toml

RUN pip install poetry

COPY ./app /code/app

ENV postgres_conn=${postgres_conn}
ENV proxy_user=${proxy_user}
ENV proxy_password=${proxy_password}
ENV proxy_host=${proxy_host}
ENV proxy_port=${proxy_port}

RUN pip install fastapi
RUN poetry install 

CMD ["poetry", "run", "fastapi", "run", "./app/main.py", "--host", "0.0.0.0", "--port", "8000"]
