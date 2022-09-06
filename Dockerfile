FROM python:latest

WORKDIR /usr/src/app

COPY ./bot_binance/ ./bot_binance
COPY ./strategies/ ./strategies
COPY main.py requirements.txt ./
COPY ./entrypoint.sh ./

RUN pip install --upgrade pip && pip install -r requirements.txt && chmod +x entrypoint.sh

CMD [ "/usr/src/app/entrypoint.sh" ]
