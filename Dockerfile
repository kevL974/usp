FROM python:latest

WORKDIR /usr/src/app

COPY ./bot_binance/ ./bot_binance
COPY ./strategies/ ./strategies
COPY main.py requirements.txt ./
COPY ./entrypoint.sh ./

#RUN pip install --upgrade pip && pip install -r requirements.txt && chmod +x entrypoint.sh
CMD ['/bin/bash', '-c','python3 -m pip install -r requirements.txt']
CMD ['/bin/bash', '-c', 'chmod +x entrypoint.sh']

ENTRYPOINT [ "/usr/src/app/entrypoint.sh" ]
