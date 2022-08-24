import unittest
import os
import pandas as pd

from unittest.mock import patch, MagicMock
from bot_binance.Bot import Bot


class TestBot(unittest.TestCase):

    def setUp(self) -> None:
        ...

    def tearDown(self) -> None:
        os.remove("positions.csv")

    def test_change_position_when_buy_action(self):
        positions = pd.DataFrame([['BTCUSDT', 1, 0.02, '9286018'], ['ETHUSDT', 0, 0.0, 'NA']],
                                          columns=['symbol', 'position', 'qty', 'orderId'])

        expected_positions = pd.DataFrame([['BTCUSDT', 1, 0.02, '9286018'], ['ETHUSDT', 1, 1.0, '9286020']],
                                          columns=['symbol', 'position', 'qty', 'orderId'])

        bot = Bot(api_key='toto', api_secret='titi', position_file='positions.csv', testnet=False)
        with patch.object(bot, 'positions', positions):
            bot.change_positions('ETHUSDT', True, 1.0, '9286020')
            self.assertTrue(bot.positions.equals(expected_positions))

    def test_change_position_when_sell_action(self):
        positions = pd.DataFrame([['BTCUSDT', 1, 0.02, '9286018'], ['ETHUSDT', 1, 0.5, '9286020']],
                                 columns=['symbol', 'position', 'qty', 'orderId'])

        expected_positions = pd.DataFrame([['BTCUSDT', 1, 0.02, '9286018'], ['ETHUSDT', 0, 0.0, 'NA']],
                                          columns=['symbol', 'position', 'qty', 'orderId'])
        bot = Bot(api_key='toto', api_secret='titi', position_file='positions.csv', testnet=False)
        with patch.object(bot, 'positions', positions):
            bot.change_positions('ETHUSDT', False, 0.0, '9286020')
            self.assertTrue(bot.positions.equals(expected_positions))

    @patch.object(Bot, 'is_open_position')
    def test_check_buy(self, mock_is_open_position):
        # case positions is not opened
        mock_is_open_position.return_value = False
        bot = Bot(api_key='toto', api_secret='titi', position_file='positions.csv', testnet=False)

        df = pd.DataFrame([['BTCUSDT', True]],
                          columns=['symbol', 'Buy'])
        self.assertTrue(bot.check_buy('BTCUSDT', df))

        df = pd.DataFrame([['BTCUSDT', False]],
                          columns=['symbol', 'Buy'])
        self.assertFalse(bot.check_buy('BTCUSDT', df))

        # case positions is opened
        mock_is_open_position.return_value = True
        df = pd.DataFrame([['BTCUSDT', True]],
                          columns=['symbol', 'Buy'])
        self.assertFalse(bot.check_buy('BTCUSDT', df))

        df = pd.DataFrame([['BTCUSDT', False]],
                          columns=['symbol', 'Buy'])
        self.assertFalse(bot.check_buy('BTCUSDT', df))

    def test_is_open_position(self):
        positions = pd.DataFrame([['BTCUSDT', 1, 0.02, '9286018'], ['ETHUSDT', 0, 0.0, 'NA']],
                                          columns=['symbol', 'position', 'qty', 'orderId'])

        bot = Bot(api_key='toto', api_secret='titi', position_file='positions.csv', testnet=False)
        with patch.object(bot, 'positions', positions):
            self.assertTrue(bot.is_open_position('BTCUSDT'))
            self.assertFalse(bot.is_open_position('ETHUSDT'))

    def test_get_order_id(self):
        positions = pd.DataFrame([['BTCUSDT', 1, 0.02, '9286018'], ['ETHUSDT', 0, 0.0, 'NA']],
                                columns=['symbol', 'position', 'qty', 'orderId'])

        bot = Bot(api_key='toto', api_secret='titi', position_file='positions.csv', testnet=False)
        with patch.object(bot, 'positions', positions):
            self.assertEqual(bot.get_order_id('BTCUSDT'), '9286018')
            self.assertEqual(bot.get_order_id('ETHUSDT'), 'NA')

    @patch.object(Bot, 'get_raw_price')
    def test_price_calc(self, mock):
        bot = Bot(api_key='toto', api_secret='titi', position_file='positions.csv', testnet=False)
        mock.return_value = 1000.0
        self.assertEqual(bot.price_calc('BTCUSDT', 0.90), 900.0)


if __name__ == '__main__':
    unittest.main()
