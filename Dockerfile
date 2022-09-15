FROM 2000cubits/raspbian:bullseye.latest

# Install dependencies
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    python3 \
    python3-dev \
    python3-pip \
    python3-venv \
    libatlas-base-dev && \
    rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN ["/bin/bash", "-c", "python3 -m venv $VIRTUAL_ENV"]

WORKDIR /usr/src/app
COPY requirements.txt ./
COPY ./bot_binance/ ./bot_binance
COPY ./strategies/ ./strategies
COPY main.py ./
RUN pip install --upgrade pip && \
    pip install opencv-python && \
    pip install -r requirements.txt

CMD ["python3", "main.py", "-c", "app_conf/bot.ini", "--testnet" ]

