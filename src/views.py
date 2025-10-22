import json
from dotenv import load_dotenv
import os
import requests
import logging
import logging.config
from utils_logs.logger_utils import get_logger, log_execution_time, log_function_call


load_dotenv()
logger = get_logger(__name__)


@log_function_call("INFO")
def get_user_setting() -> dict:
    """получение настроек пользователя из файла user_settings.json"""
    try:
        file_path = "../user_settings.json"
        logger.info("📁 ЗАГРУЗКА НАСТРОЕК ПОЛЬЗОВАТЕЛЯ | Файл: %s", file_path)

        with log_execution_time("Загрузка user_settings.json", __name__):
            with open(file_path, "r", encoding="utf-8") as f:
                settings = json.load(f)

        logger.info(
            "✅ НАСТРОЙКИ ЗАГРУЖЕНЫ | Валюты: %d | Акции: %d",
            len(settings.get("user_currencies", [])),
            len(settings.get("user_stocks", [])),
        )
        logger.debug("⚙️  ЗАГРУЖЕННЫЕ НАСТРОЙКИ: %s", settings)

        return settings

    except FileNotFoundError:
        logger.error("❌ ФАЙЛ НАСТРОЕК НЕ НАЙДЕН: %s", file_path)
        return {}

    except json.JSONDecodeError as e:
        logger.error("❌ ОШИБКА ЧТЕНИЯ JSON | Файл: %s | Ошибка: %s", file_path, str(e), exc_info=True)
        return {}

    except Exception as ex:
        logger.error("❌ ОШИБКА ЗАГРУЗКИ НАСТРОЕК | Тип: %s", type(ex).__name__, exc_info=True)
        return {}


@log_function_call("INFO")
def exchange_rate(setting: dict) -> list[dict]:
    """курс валют"""

    if not setting:
        logger.warning("⚠️  НЕТ НАСТРОЕК ДЛЯ ПОЛУЧЕНИЯ КУРСА ВАЛЮТ")
        return []

    user_currencies = setting.get("user_currencies", [])
    if not user_currencies:
        logger.warning("⚠️  НЕТ НАСТРОЕННЫХ ВАЛЮТ ДЛЯ ОТСЛЕЖИВАНИЯ")
        return []

    logger.info("💱 ЗАПРОС КУРСОВ ВАЛЮТ | Количество валют: %d | Валюты: %s", len(user_currencies), user_currencies)

    api_key = os.getenv("API_KEY_RATE")
    if not api_key:
        logger.error("❌ ОТСУТСТВУЕТ API_KEY_RATE В ПЕРЕМЕННЫХ ОКРУЖЕНИЯ")
        return []

    logger.debug("🔑 API КЛЮЧ НАЙДЕН | Длина: %d символов", len(api_key))

    list_currency_rates = []
    successful_requests = 0
    failed_requests = 0

    with log_execution_time("Получение курсов валют", __name__):
        for currency in user_currencies:
            try:
                logger.debug("🌐 ЗАПРОС КУРСА | Валюта: %s", currency)
                url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{currency}"

                with log_execution_time(f"API запрос для {currency}", __name__):
                    response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    data_rate = response.json()
                    if data_rate.get("result") == "success":
                        rate_rub = data_rate["conversion_rates"].get("RUB")
                        if rate_rub:
                            currency_rate = {"currency": currency, "rate": round(rate_rub, 2)}
                            list_currency_rates.append(currency_rate)
                            successful_requests += 1

                            logger.debug("✅ КУРС ПОЛУЧЕН | Валюта: %s → RUB: %.2f", currency, rate_rub)
                        else:
                            logger.warning("⚠️  КУРС RUB НЕ НАЙДЕН ДЛЯ ВАЛЮТЫ: %s", currency)
                            failed_requests += 1
                    else:
                        logger.warning(
                            "⚠️  API ОШИБКА | Валюта: %s | Причина: %s",
                            currency,
                            data_rate.get("error-type", "Unknown"),
                        )
                    failed_requests += 1

                else:
                    logger.warning("⚠️  HTTP ОШИБКА | Валюта: %s | Код: %d", currency, response.status_code)
                    failed_requests += 1

            except requests.exceptions.Timeout:
                logger.error("⏰ ТАЙМАУТ ЗАПРОСА | Валюта: %s", currency)
                failed_requests += 1
            except requests.exceptions.ConnectionError:
                logger.error("🌐 ОШИБКА ПОДКЛЮЧЕНИЯ | Валюта: %s", currency)
                failed_requests += 1
            except Exception as e:
                logger.error("❌ ОШИБКА ЗАПРОСА | Валюта: %s | Тип: %s", currency, type(e).__name__, exc_info=True)
                failed_requests += 1
        # Итоговое логирование
        total_requests = len(user_currencies)
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0

        logger.info(
            "📊 ИТОГИ ПОЛУЧЕНИЯ КУРСОВ | Успешно: %d/%d (%.1f%%) | Получено курсов: %d",
            successful_requests,
            total_requests,
            success_rate,
            len(list_currency_rates),
        )

        if list_currency_rates:
            logger.debug("💱 ПОЛУЧЕННЫЕ КУРСЫ: %s", list_currency_rates)
        else:
            logger.warning("💱 КУРСЫ ВАЛЮТ НЕ ПОЛУЧЕНЫ")

        return list_currency_rates


@log_function_call("INFO")
def stock_prices(settings: dict) -> list[dict]:
    """цены на акции"""

    if not settings:
        logger.warning("⚠️  НЕТ НАСТРОЕК ДЛЯ ПОЛУЧЕНИЯ ЦЕН НА АКЦИИ")
        return []

    user_stocks = settings.get("user_stocks", [])
    if not user_stocks:
        logger.warning("⚠️  НЕТ НАСТРОЕННЫХ АКЦИЙ ДЛЯ ОТСЛЕЖИВАНИЯ")
        return []

    logger.info("📈 ЗАПРОС ЦЕН НА АКЦИИ | Количество акций: %d | Акции: %s", len(user_stocks), user_stocks)

    api_key = os.getenv("API_KEY_STOCK")
    if not api_key:
        logger.error("❌ ОТСУТСТВУЕТ API_KEY_STOCK В ПЕРЕМЕННЫХ ОКРУЖЕНИЯ")
        return []

    logger.debug("🔑 API КЛЮЧ ДЛЯ АКЦИЙ НАЙДЕН | Длина: %d символов", len(api_key))

    list_stock_prices = []
    successful_requests = 0
    failed_requests = 0

    with log_execution_time("Получение цен на акции", __name__):
        for symbol in user_stocks:
            try:
                logger.debug("🌐 ЗАПРОС ЦЕНЫ АКЦИИ | Символ: %s", symbol)
                url = f"https://financialmodelingprep.com/stable/quote?symbol={symbol}&apikey={api_key}"

                with log_execution_time(f"API запрос для {symbol}", __name__):
                    response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    data = response.json()

                    # Проверяем, что данные не пустые
                    if data and len(data) > 0:
                        stock_data = data[0]
                        price = stock_data.get("price")

                        if price is not None:
                            stock = {"stock": symbol, "price": round(float(price), 2)}
                            list_stock_prices.append(stock)
                            successful_requests += 1

                            logger.debug("✅ ЦЕНА ПОЛУЧЕНА | Акция: %s → Цена: %.2f", symbol, price)
                        else:
                            logger.warning("⚠️  ЦЕНА НЕ НАЙДЕНА В ОТВЕТЕ | Акция: %s | Данные: %s", symbol, stock_data)
                            failed_requests += 1
                    else:
                        logger.warning("⚠️  ПУСТОЙ ОТВЕТ API | Акция: %s | Ответ: %s", symbol, data)
                        failed_requests += 1
                else:
                    logger.warning("⚠️  HTTP ОШИБКА | Акция: %s | Код: %d", symbol, response.status_code)
                    failed_requests += 1

            except requests.exceptions.Timeout:
                logger.error("⏰ ТАЙМАУТ ЗАПРОСА | Акция: %s", symbol)
                failed_requests += 1

            except requests.exceptions.ConnectionError:
                logger.error("🌐 ОШИБКА ПОДКЛЮЧЕНИЯ | Акция: %s", symbol)
                failed_requests += 1

            except KeyError as e:
                logger.error(
                    "❌ ОШИБКА КЛЮЧА В ОТВЕТЕ | Акция: %s | Отсутствует ключ: %s", symbol, str(e), exc_info=True
                )
                failed_requests += 1

            except IndexError:
                logger.error("❌ ОШИБКА ИНДЕКСА | Акция: %s | Пустой массив в ответе", symbol, exc_info=True)
                failed_requests += 1

            except ValueError as e:
                logger.error("❌ ОШИБКА ПРЕОБРАЗОВАНИЯ ДАННЫХ | Акция: %s | Ошибка: %s", symbol, str(e), exc_info=True)
                failed_requests += 1

            except Exception as e:
                logger.error("❌ ОШИБКА ЗАПРОСА | Акция: %s | Тип: %s", symbol, type(e).__name__, exc_info=True)
                failed_requests += 1

    # Итоговое логирование
    total_requests = len(user_stocks)
    success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0

    logger.info(
        "📊 ИТОГИ ПОЛУЧЕНИЯ ЦЕН АКЦИЙ | Успешно: %d/%d (%.1f%%) | Получено цен: %d",
        successful_requests,
        total_requests,
        success_rate,
        len(list_stock_prices),
    )

    if list_stock_prices:
        # Логируем общую статистику по ценам
        prices = [stock["price"] for stock in list_stock_prices]
        avg_price = sum(prices) / len(prices) if prices else 0
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0

        logger.info("💹 СТАТИСТИКА ЦЕН | Мин: %.2f | Макс: %.2f | Средняя: %.2f", min_price, max_price, avg_price)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("📈 ПОЛУЧЕННЫЕ ЦЕНЫ АКЦИЙ: %s", list_stock_prices)
    else:
        logger.warning("📈 ЦЕНЫ АКЦИЙ НЕ ПОЛУЧЕНЫ")

    return list_stock_prices


if __name__ == "__main__":
    setting = get_user_setting()
    exchange_rate(setting)
    stock_prices(setting)
