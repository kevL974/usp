# -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 16:57:45 2021

@author: kevla
"""
import sqlite3
import matplotlib.pyplot as plt

from backtesting.Bank import Bank
from typing import Callable, List
from datetime import datetime, date, timedelta
from backtesting.VirtualWallet import VirtualWallet
from backtesting.Strategy import Strategy
from sys import exit


class TimeMachine:

    def __init__(self, start: str, end: str, devise: str = 'EUR'):
        self._start = date.fromisoformat(start)
        self._end = date.fromisoformat(end)
        self._devise = devise
        self._db = None
        self._bank = None
        self._wallet = None

    def __del__(self):
        if self.is_db_defined():
            r = self._db.execute('drop table if exists TMP_HISTORIC')
            self._db.close()

    def is_db_defined(self) -> bool:
        return self._db is not None

    def is_bank_defined(self) -> bool:
        return self._bank is not None

    def is_wallet_defined(self) -> bool:
        return self._wallet is not None

    def init_db(self):
        if not self.is_bank_defined():
            print('You must define a bank before initializing Database !')
            exit(1)
        self._db = sqlite3.connect('timeMachine.db')
        self._db.execute('create table if not exists CURRENCIES (name text, id text)')

        if self._db.execute('select count(*) from CURRENCIES').fetchone()[0] == 0:
            data = self._bank.get_currencies()
            print(data)
            for currency in data:
                self._db.execute('insert into CURRENCIES values (:name, :id)',
                                 {
                                     'name': currency['base_currency'],
                                     'id': currency['id']
                                 }
                                 )

        self._db.commit()

    def attach_wallet(self, wallet: VirtualWallet) -> None:
        self._wallet = wallet

    def choose_bank(self, bank: Callable[[], Bank]) -> None:
        self._bank = bank()

    def exists_currency(self, currency: str) -> bool:
        if not self.is_db_defined():
            print('You must define a bank before initializing Database !')
            exit(1)

        result = self._db.execute('select * from CURRENCIES where name = :currency', {'currency': currency})

        data = result.fetchone()
        if data is None:
            return False
        else:
            return True

    def get_data(self, currency: str):
        if self._bank is None:
            print('You must specify a bank before !')
        else:
            if not self.exists_currency(currency):
                print(f'The currency {currency} is not available  in your bank {self._bank.NAME}')
                exit(2)

        d = self._end - self._start
        h_total = d.days * 24
        if h_total <= 300:
            self._historical_data_to_db(
                self._bank.get_historical_data(currency + '-' + self._devise, self._start, self._end, 3600))
        else:
            steps = 300
            start = self._start
            end = self._start + timedelta(hours=steps)
            while h_total > 0:
                if h_total >= steps:
                    h_total -= steps
                    end = start + timedelta(hours=steps)
                else:
                    end = self._end
                    h_total = 0
                self._historical_data_to_db(
                    self._bank.get_historical_data(currency + '-' + self._devise, self._start, self._end, 3600))
                start = end

    def _historical_data_to_db(self, data: List[List]) -> None:
        self._db.execute(
            'create table if not exists TMP_HISTORIC (date text, time text, cost real)')
        print(data)
        for row in data:
            print(row)
            date_cur = datetime.fromtimestamp(row[0]).strftime('%Y-%m-%d')
            time = datetime.fromtimestamp(row[0]).strftime('%H:%M:%S')
            self._db.execute(
                'insert into TMP_HISTORIC values (:date, :time, :cost)',
                {
                    'date': date_cur,
                    'time': time,
                    'cost': row[1],
                }
                )
        self._db.commit()

    def show_data(self, type: str = 'csv', extra: List = None):
        result = self._db.execute('select * from TMP_HISTORIC order by date, time')

        if type == 'graph':
            data = []
            x_axis_values = []
            x_axis_step = 0

        for row in result.fetchall():
            if type == 'csv':
                print(f'{row[0]};{row[1]};{row[2]}')
            elif type == 'graph':
                data.append(row[2])
                if x_axis_step % 100 == 0:
                    x_axis_values.append(row[0])
                else:
                    x_axis_values.append('')
                x_axis_step += 1
            else:
                print('_show_data : Unsupported type')
                exit(3)

        if type == 'graph':
            plt.figure(figsize=(18, 12))
            plt.plot(data)
            plt.xlabel('Time')
            plt.ylabel(f'Value ({self._devise})')
            plt.tick_params(axis='x', length=0)
            plt.ylim(bottom=0)
            for i in range(len(x_axis_values)):
                if x_axis_values[i] != '':
                    plt.plot([i, i], [0, data[i]], linestyle='dashed', color='#cfd7e6')
            plt.xticks(list(range(len(x_axis_values))), x_axis_values, rotation=45)

            if extra is not None:
                for transaction in extra:
                    if transaction[0] == 'buy':
                        plt.plot(transaction[6], transaction[5], color='#f00', marker='v')
                    else:
                        plt.plot(transaction[6], transaction[5], color='#0f0', marker='^')

            plt.show()

    def test_strategy(self, strategy: Strategy) -> List:
        if not self.is_wallet_defined():
            print('you must attach a Wallet first ! ')
            exit(1)

        # ...

        result = self._db.execute('select * from TMP_HISTORIC order by date, time')
        last_op = None
        n = 0
        for row in result.fetchall():
            if last_op is None:
                self._wallet.buy(self._wallet.get_total_funds()*0.2, row[2], row[0], row[1], n)
                buy_rate = row[2]
                last_op = 'buy'
            else:
                if last_op == 'buy':
                    if strategy.get_action('sell') == 'up':
                        if row[2] >= buy_rate + buy_rate * strategy.get_rate('sell') / 100:
                            self._wallet.sell(self._wallet.get_total_coins(), row[2], row[0], row[1], n)
                            last_op = 'sell'
                            buy_rate = row[2]
                    if strategy.get_action('sell') == 'down':
                        if row[2] >= buy_rate - buy_rate * strategy.get_rate('sell') / 100:
                            self._wallet.sell(self.wallet.get_total_coins(), row[2], row[0], row[1], n)
                            last_op = 'sell'
                            buy_rate = row[2]
                elif last_op == 'sell':
                    if strategy.get_action('buy') == 'up':
                        if row[2] >= buy_rate + buy_rate * strategy.get_rate('buy') / 100:
                            self._wallet.buy(self._wallet.get_total_funds()*0.2, row[2], row[0], row[1], n)
                            last_op = 'buy'
                            buy_rate = row[2]
                    if strategy.get_action('buy') == 'down':
                        if row[2] >= buy_rate - buy_rate * strategy.get_rate('buy') / 100:
                            self._wallet.buy(self._wallet.get_total_funds()*0.2, row[2], row[0], row[1], n)
                            last_op = 'buy'
                            buy_rate = row[2]

            n += 1
        self._wallet.show_transactions()

        return self._wallet.get_transactions()
    