import json
from datetime import datetime

import pandas as pd
from pandas import DataFrame
from typing import Dict, List, Any


from src.views import exchange_rate, stock_prices, get_user_setting
from utils_logs.logger_utils import (
    get_logger,
    log_function_call,
    log_execution_time,
    log_dataframe_info,
    log_data_quality,
    log_dict_structure,
)


pd.set_option("display.max_columns", None)


@log_function_call("INFO")
def open_file_xlsx(path_file: str):
    """чтение файла xlsx"""
    logger = get_logger(__name__)
    logger.info("📁 ЗАГРУЗКА ФАЙЛА: %s", path_file)
    try:
        if path_file:
            with log_execution_time(f"Загрузка Excel файла {path_file}"):
                open_file = pd.read_excel(path_file)

            logger.debug("📄 Формат: Excel")
            log_dataframe_info(open_file, "Загруженный файл")
            logger.info("✅ ДАННЫЕ УСПЕШНО ЗАГРУЖЕНЫ")
            return open_file
        else:
            logger.error("❌ ПУТЬ К ФАЙЛУ НЕ УКАЗАН")
            raise ValueError("Путь к файлу не может быть пустым")

    except FileNotFoundError:
        logger.error("❌ ФАЙЛ НЕ НАЙДЕН: %s", path_file)
        return None
    except Exception as e:
        logger.error("❌ ОШИБКА ЗАГРУЗКИ %s | Тип: %s", path_file, type(e).__name__, exc_info=True)
        return None


@log_function_call("INFO")
def data_analysis(current_time: str, df: pd.DataFrame) -> pd.DataFrame:
    """данные с начала месяца по входящую дату"""
    logger = get_logger(__name__)

    logger.info("🔍 ЗАПУСК АНАЛИЗА ДАННЫХ | Дата: %s", current_time)

    try:
        # Логируем исходные параметры
        initial_count = len(df)
        logger.debug("📊 ВХОДНЫЕ ДАННЫЕ | Строк: %d | Колонок: %d", initial_count, len(df.columns))

        with log_execution_time("Парсинг дат"):
            date_obj = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
            logger.debug("📅 ПАРСИНГ ДАТЫ | Объект datetime: %s", date_obj)

            end_date_str = datetime.strftime(date_obj, "%d.%m.%Y")
            start_date_str = end_date_str.split(".")
            start_date_str[0] = "01"
            start_date_str = ".".join(start_date_str)

        logger.info("📅 РАСЧЕТ ПЕРИОДА | Начало: %s | Конец: %s", start_date_str, end_date_str)

        # Преобразование дат
        with log_execution_time("Преобразование дат"):
            df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
            start_date = pd.to_datetime(start_date_str, format="%d.%m.%Y")
            end_date = pd.to_datetime(end_date_str, format="%d.%m.%Y")

        logger.debug("📅 ПРЕОБРАЗОВАНИЕ ДАТ | Start: %s | End: %s", start_date, end_date)

        # Фильтрация данных
        with log_execution_time("Фильтрация данных"):
            filter_data = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)]
            filtered_count = len(filter_data)

        efficiency = (filtered_count / initial_count * 100) if initial_count > 0 else 0
        logger.info(
            "✅ ФИЛЬТРАЦИЯ ЗАВЕРШЕНА | Исходно: %d | Отфильтровано: %d | Эффективность: %.1f%%",
            initial_count,
            filtered_count,
            efficiency,
        )

        if filtered_count == 0:
            logger.warning("⚠️  НЕТ ДАННЫХ В УКАЗАННОМ ПЕРИОДЕ")
        else:
            log_dataframe_info(filter_data, "Отфильтрованные данные")

        return filter_data

    except Exception as ex:
        logger.error("❌ ОШИБКА В data_analysis | Дата: %s | Тип: %s", current_time, type(ex).__name__, exc_info=True)
        return pd.DataFrame()


@log_function_call("DEBUG")
def greetings(current_time: str) -> str:  # YYYY-MM-DD HH:MM:SS
    """Приветсвие"""
    logger = get_logger(__name__)

    logger.info(f"👋 ЗАПУСК ФОРМИРОВАНИЯ ПРИВЕТСТВИЯ | Время: {current_time}")

    try:
        date_obj = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
        hour = date_obj.hour

        logger.debug("⏰ АНАЛИЗ ВРЕМЕНИ | Час: %d", hour)

        if 5 <= hour <= 12:
            greeting = "Доброе утро"
        elif 12 <= hour <= 18:
            greeting = "Добрый день"
        elif 18 <= hour <= 23:
            greeting = "Добрый вечер"
        else:
            greeting = "Доброй ночи"

        logger.info("👋 ПРИВЕТСТВИЕ СФОРМИРОВАНО: '%s'", greeting)
        return greeting

    except Exception as ex:
        logger.error("❌ ОШИБКА В greetings | Время: %s | Тип: %s", current_time, type(ex).__name__, exc_info=True)
        return "Здравствуйте"


@log_function_call("INFO")
def cards(df: DataFrame) -> list[dict]:
    """последние 4 цифры карты, общая сумма расходов, кешбэк (1 рубль на каждые 100 рублей)"""
    logger = get_logger(__name__)

    logger.info("💳 ЗАПУСК АНАЛИЗА КАРТ")

    try:
        # Логируем входные данные
        logger.debug("📊 ВХОДНЫЕ ДАННЫЕ ДЛЯ КАРТ | Строк: %d", len(df))

        if df.empty:
            logger.warning("⚠️  ПУСТОЙ DATAFRAME ДЛЯ АНАЛИЗА КАРТ")
            return []

        with log_execution_time("Группировка данных по картам"):
            # Группировка по картам
            group_df = df.groupby("Номер карты").agg(
                {"Сумма операции": lambda x: x[x < 0].sum(), "Бонусы (включая кэшбэк)": "sum"}
            )

        logger.info("💳 ГРУППИРОВКА КАРТ | Найдено карт: %d", len(group_df))

        list_card = []
        total_spent_all = 0
        total_cashback_all = 0

        for card_number, data in group_df.iterrows():
            spent = abs(data["Сумма операции"]) if pd.notna(data["Сумма операции"]) else 0
            cashback = data["Бонусы (включая кэшбэк)"] if pd.notna(data["Бонусы (включая кэшбэк)"]) else 0

            card = {
                "last_digits": card_number[1:],
                "total_spent": spent,
                "cashback": cashback,
            }
            list_card.append(card)

            total_spent_all += spent
            total_cashback_all += cashback

            logger.debug("💳 КАРТА %s | Расходы: %.2f | Кэшбэк: %.2f", card["last_digits"], spent, cashback)

        logger.info(
            "💳 АНАЛИЗ КАРТ ЗАВЕРШЕН | Карт: %d | Общие расходы: %.2f | Общий кэшбэк: %.2f",
            len(list_card),
            total_spent_all,
            total_cashback_all,
        )

        return list_card

    except Exception as ex:
        logger.error("❌ ОШИБКА В cards | Тип: %s", type(ex).__name__, exc_info=True)
        return []


@log_function_call("INFO")
def top_transactions(df: DataFrame) -> list[dict]:
    """Топ-5 транзакций по сумме платежа"""
    logger = get_logger(__name__)

    logger.info("🏆 ЗАПУСК ПОИСКА ТОП-5 ТРАНЗАКЦИЙ")

    try:
        logger.debug("📊 ВХОДНЫЕ ДАННЫЕ | Строк: %d", len(df))

        if df.empty:
            logger.warning("⚠️  ПУСТОЙ DATAFRAME ДЛЯ ПОИСКА ТОП ТРАНЗАКЦИЙ")
            return []

        with log_execution_time("Фильтрация и сортировка транзакций"):
            # Фильтруем только расходы
            expenses = df[df["Сумма операции"] < 0].copy()
            logger.debug("💰 РАСХОДЫ | Найдено: %d транзакций", len(expenses))

            if expenses.empty:
                logger.warning("⚠️  НЕТ ТРАНЗАКЦИЙ РАСХОДОВ")
                return []

            # Получаем топ-5
            top5_expenses = expenses.nlargest(5, "Сумма операции", keep="all")

            # Преобразуем даты
            top5_expenses["Дата операции"] = pd.to_datetime(
                df["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce"
            )

            # Сортируем по дате
            top5_expenses_sorted = top5_expenses.sort_values("Дата операции", ascending=False)

        logger.info("🏆 НАЙДЕНО ТОП-ТРАНЗАКЦИЙ: %d", len(top5_expenses_sorted))

        list_top5 = []
        total_amount = 0

        for i, data in top5_expenses_sorted.iterrows():
            amount = abs(data["Сумма операции"]) if pd.notna(data["Сумма операции"]) else 0
            date_str = data["Дата операции"].strftime("%d.%m.%Y") if pd.notna(data["Дата операции"]) else "Неизвестно"
            category = data["Категория"] if pd.notna(data["Категория"]) else "Неизвестно"
            description = data["Описание"] if pd.notna(data["Описание"]) else "Без описания"

            transaction = {
                "date": date_str,
                "amount": amount,
                "category": category,
                "description": description,
            }
            list_top5.append(transaction)
            total_amount += amount

            logger.debug("🏆 ТОП-ТРАНЗАКЦИЯ | Дата: %s | Сумма: %.2f | Категория: %s", date_str, amount, category)

        logger.info(
            "🏆 ТОП-5 ТРАНЗАКЦИЙ СФОРМИРОВАНЫ | Транзакций: %d | Общая сумма: %.2f", len(list_top5), total_amount
        )
        return list_top5

    except Exception as ex:
        logger.error("❌ ОШИБКА В top_transactions | Тип: %s", type(ex).__name__, exc_info=True)
        return []


@log_function_call("INFO")
def main_utils(current_time: str) -> dict:
    """главную функцию модуля utils"""
    logger = get_logger(__name__)

    logger.info("🚀 ЗАПУСК ГЛАВНОЙ ФУНКЦИИ UTILS")
    logger.info("⏰ ТЕКУЩЕЕ ВРЕМЯ: %s", current_time)

    try:
        with log_execution_time("Полный цикл обработки данных"):
            # Загрузка данных
            logger.info("📁 ЗАГРУЗКА ДАННЫХ ИЗ ФАЙЛА")
            df = open_file_xlsx("../data/operations.xlsx")

            if df is None or df.empty:
                logger.error("❌ НЕ УДАЛОСЬ ЗАГРУЗИТЬ ДАННЫЕ ИЗ ФАЙЛА")
                return {}

            logger.info("📊 ДАННЫЕ ЗАГРУЖЕНЫ | Строк: %d | Колонок: %d", len(df), len(df.columns))

            # Анализ качества данных
            log_data_quality(df, "Исходные данные")

            # Анализ данных
            logger.info("🔍 ФИЛЬТРАЦИЯ ДАННЫХ ПО ПЕРИОДУ")
            df_filtered = data_analysis(current_time, df)

            if df_filtered.empty:
                logger.warning("⚠️  НЕТ ДАННЫХ ПОСЛЕ ФИЛЬТРАЦИИ")
            else:
                log_data_quality(df_filtered, "Отфильтрованные данные")

            # Получение настроек
            logger.info("⚙️  ПОЛУЧЕНИЕ НАСТРОЕК ПОЛЬЗОВАТЕЛЯ")
            setting = get_user_setting()
            logger.debug("⚙️  НАСТРОЙКИ: %s", setting)

            # Формирование данных
            logger.info("📊 ФОРМИРОВАНИЕ ОТВЕТА")
            data = {
                "greeting": greetings(current_time),
                "cards": cards(df_filtered if not df_filtered.empty else df),
                "top_transactions": top_transactions(df_filtered if not df_filtered.empty else df),
                "currency_rates": exchange_rate(setting),
                "stock_prices": stock_prices(setting),
            }

            # Логируем структуру результата
            log_dict_structure(data, "Финальные данные")

            # Логируем статистику результата
            cards_count = len(data["cards"])
            transactions_count = len(data["top_transactions"])
            greeting_text = data["greeting"]

            logger.info(
                "✅ ДАННЫЕ СФОРМИРОВАНЫ | Приветствие: '%s' | Карт: %d | Топ-транзакций: %d",
                greeting_text,
                cards_count,
                transactions_count,
            )

            # Конвертация в JSON
            logger.debug("🔄 КОНВЕРТАЦИЯ В JSON")
            json_data = json.dumps(data, indent=2, ensure_ascii=False)

        logger.info("🎯 ГЛАВНАЯ ФУНКЦИЯ UTILS УСПЕШНО ЗАВЕРШЕНА")
        return json_data

    except Exception as ex:
        logger.error(
            "❌ КРИТИЧЕСКАЯ ОШИБКА В main_utils | Время: %s | Тип: %s", current_time, type(ex).__name__, exc_info=True
        )
        return json.dumps({"error": "Произошла ошибка при обработке данных"}, ensure_ascii=False)


if __name__ == "__main__":
    print(main_utils("2019-01-10 16:26:00"))
    # df = open_file_xlsx('../data/operations.xlsx')
    # df = data_analysis('2019-01-10 16:26:00', df)
    # cards(df)
