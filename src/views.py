import json
from dotenv import load_dotenv
import os
import requests

load_dotenv()


def get_user_setting() -> dict:
    """получение настроек пользователя из файла user_settings.json"""
    try:
        data = '../user_settings.json'
        with open(data, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as ex:
        print(f'Ошибка: {ex}')


def exchange_rate(setting: dict) -> list[dict]:
    """курс валют"""
    try:
        list_currency_rates = []
        api_key = os.getenv('API_KEY_RATE')
        for currency_rate in setting['user_currencies']:
            url = f'https://v6.exchangerate-api.com/v6/{api_key}/latest/{currency_rate}'
            response = requests.get(url)
            if response.status_code == 200:
                data_rate = response.json()
                currency_rate = {
                    "currency": currency_rate,
                    "rate": round(data_rate['conversion_rates']['RUB'], 2)
                }
                list_currency_rates.append(currency_rate)
        print(list_currency_rates)
        return list_currency_rates
    except Exception as ex:
        print(f'Ошибка: {ex}')


def stock_prices(settings: dict) -> list[dict]:
    """цены на акции"""
    try:
        list_stock_prices = []
        for symbol in settings['user_stocks']:
            api_key = os.getenv('API_KEY_STOCK')
            url = f'https://financialmodelingprep.com/stable/quote?symbol={symbol}&apikey={api_key}'
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                stock = {
                    "stock": symbol,
                    "price": data[0]['price']
                }
                list_stock_prices.append(stock)
        print(list_stock_prices)
        return list_stock_prices

    except Exception as ex:
        print(f'Ошибка: {ex}')


if __name__ == '__main__':
    setting = get_user_setting()
    exchange_rate(setting)
    stock_prices(setting)
