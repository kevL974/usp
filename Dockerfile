FROM python:latest

ENV VIRTUAL_ENV=/opt/venv

WORKDIR /usr/src/app

COPY ./bot_binance/ ./bot_binance
COPY ./strategies/ ./strategies
COPY main.py requirements.txt ./

RUN ["/bin/bash", "-c", "python -m venv $VIRTUAL_ENV"]

ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python3", "/usr/src/app/main.py" ]
