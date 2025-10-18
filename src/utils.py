import pandas as pd
from datetime import datetime

from pandas.core.interchange.dataframe_protocol import DataFrame

pd.set_option('display.max_columns', None)


def open_file_xlsx(path_file: str):
    """чтение файла xlsx"""
    if path_file:
        open_file = pd.read_excel(path_file)
        # print(open_file.head(3))
        # print(open_file.shape)
        return open_file
    else:
        raise FileNotFoundError


def data_analysis(current_time: str, df: DataFrame) -> DataFrame:
    """данные с начала месяца по входящую дату"""
    try:
        date_obj = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')

        end_date_str = datetime.strftime(date_obj, '%d.%m.%Y')
        start_date_str = end_date_str.split('.')
        start_date_str[0] = '01'
        start_date_str = '.'.join(start_date_str)

        df['Дата операции'] = pd.to_datetime(df['Дата операции'], format='%d.%m.%Y %H:%M:%S')
        start_date = pd.to_datetime(start_date_str, format='%d.%m.%Y')
        end_date = pd.to_datetime(end_date_str, format='%d.%m.%Y')
        filter_data = df[(df['Дата операции'] >= start_date) & (df['Дата операции'] <= end_date)]
        #print(filter_data)
        return filter_data

    except Exception as ex:
        print(f'Ошибка: {ex}')


def greetings(current_time: str) -> str:  # YYYY-MM-DD HH:MM:SS
    """Приветсвие"""
    try:
        date_obj = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')
        hour = date_obj.hour
        if 5 <= hour <= 12:
            return 'Доброе утро'
        elif 12 <= hour <= 18:
            return 'Добрый день'
        elif 18 <= hour <= 23:
            return 'Добрый вечер'
        else:
            return 'Доброй ночи'
    except Exception as ex:
        print(f'Ошибка: {ex}')


def cards(df: DataFrame) -> list[dict]:
    """последние 4 цифры карты, общая сумма расходов, кешбэк (1 рубль на каждые 100 рублей)"""
    group_df = df.groupby('Номер карты').agg({
            'Сумма операции': lambda x: x[x < 0].sum(),
         'Бонусы (включая кэшбэк)': 'sum'})
    list_card = []
    for card_namber, data in group_df.iterrows():
        card = {
            "last_digits": card_namber,
            "total_spent": data['Сумма операции'],
            "cashback": data['Бонусы (включая кэшбэк)']
        }
        list_card.append(card)
    #print(list_card)
    return list_card


def top_transactions(df: DataFrame) -> list[dict]:
    """Топ-5 транзакций по сумме платежа"""
    expenses = df[df['Сумма операции'] < 0].copy()
    top5_expenses = expenses.nlargest(5, 'Сумма операции', keep='all')
    top5_expenses['Дата операции'] = pd.to_datetime(df['Дата операции'], format='%d.%m.%Y %H:%M:%S')
    top5_expenses_sorted = top5_expenses.sort_values('Дата операции', ascending=False)
    list_top5 = []
    for i, data in top5_expenses_sorted.iterrows():
        transaction = {
            "date": data['Дата операции'].strftime('%d.%m.%Y'),
            "amount": data['Сумма операции'],
            "category": data['Категория'],
            "description": data['Описание']
        }
        list_top5.append(transaction)
    #print(list_top5)
    return list_top5


if __name__ == '__main__':
    df = open_file_xlsx('../data/operations.xlsx')
    df = data_analysis('2019-01-10 16:26:00', df)
    print(df)
    cards(df)
    top_transactions(df)
