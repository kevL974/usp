# -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 12:48:45 2021

@author: kevL974
"""

from abc import ABC, abstractmethod
from typing import List, Tuple
import requests


class Bank(ABC):
    NAME: str
    URL: str
    API: str
    TIME: str

    def _make_request(self, *args: Tuple[str]) -> str:
        query = self.__class__.API

        for arg in args:
            query += arg + '/'
        return query[:-1]

    @staticmethod
    def _request(query: str):
        data = requests.get(query)
        if data.status_code != 200:
            print(f'Error while executing request : {query}')
        return data.json()

    @abstractmethod
    def get_historical_data(self, currency: str, start: str, end: str,
                          granularity: int) -> List:
        ...

    @abstractmethod
    def get_currencies(self) -> List:
        ...