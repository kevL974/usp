#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bot_binance.Bot import Bot
from bot_binance.utils import read_api_keys, OHLC_COLUMNS
from strategies.Strategy import Sma200Rsi10Strategy
from logging.handlers import TimedRotatingFileHandler

import logging
import logging.config
import logging.handlers
import argparse
import configparser
import time


def init_logger_conf(path: str) -> None:
    logging.config.fileConfig(path)
    # formatter_debug = logging.Formatter('%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
    # formatter_info = logging.Formatter('%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
    #
    # logger_debug = logging.getLogger('debug_log')
    # handler_debug = logging.handlers.TimedRotatingFileHandler('/var/log/debug.log', when='s', interval=5, encoding='utf-8')
    # handler_debug.setFormatter(formatter_debug)
    # logger_debug.setLevel(logging.DEBUG)
    # logger_debug.addHandler(handler_debug)
    #
    # logger_info = logging.getLogger('info_log')
    # handler_info = logging.handlers.TimedRotatingFileHandler('/var/log/info.log', when='d', interval=7, encoding='utf-8')
    # handler_info.setFormatter(formatter_info)
    # logger_info.setLevel(logging.INFO)
    # logger_info.addHandler(handler_info)
    #
    # logger_order = logging.getLogger('order_log')
    # handler_info_order = logging.handlers.TimedRotatingFileHandler('/var/log/order.log', when='d', interval=7, encoding='utf-8')
    # handler_info_order.setFormatter(formatter_info)
    # logger_order.setLevel(logging.INFO)
    # logger_order.addHandler(handler_info_order)


def load_config(path: str) -> configparser.ConfigParser:
    config_bot = configparser.ConfigParser()
    config_bot.read(path)
    return config_bot


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Make some trades with Binance')
    parser.add_argument('-c', '--config', help='path to bot configuration file.', type=str, required=True)
    parser.add_argument('--testnet', help='use binance testnet platform', action='store_true')
    parser.add_argument('--debug', help='activate debug mode', action='store_true')
    args = parser.parse_args()

    path_config = args.config
    testnet_mode = args.testnet
    debug_mode = args.debug

    config = load_config(path_config)
    logger_conf_path = config['logger']['path_conf_logger']

    bot = None
    if testnet_mode:
        api_key = config['api_binance_demo']['api_key']
        api_secret = config['api_binance_demo']['api_secret']
        positions_path = config['api_binance_demo']['path']
        bot = Bot(api_key, api_secret, positions_path, testnet=True)
    else:
        api_key = config['api_binance']['api_key']
        api_secret = config['api_binance']['api_secret']
        positions_path = config['api_binance']['path']
        bot = Bot(api_key, api_secret, positions_path, testnet=False)

    init_logger_conf(logger_conf_path)
    bot.choose_strategy(Sma200Rsi10Strategy)
    bot.run()
