import json
import os
import sys
from unittest.mock import MagicMock, mock_open, patch

import pytest

from src.utils import exchange_rate, get_user_setting, stock_prices

sys.path.append("..")  # Добавляем путь к исходным файлам


# Тесты для get_user_setting
def test_get_user_setting_success():
    """Тест успешной загрузки настроек"""
    mock_data = {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "GOOGL"]}

    with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
        result = get_user_setting()

    assert result == mock_data
    assert "user_currencies" in result
    assert "user_stocks" in result


def test_get_user_setting_file_not_found():
    """Тест случая когда файл не найден"""
    with patch("builtins.open", side_effect=FileNotFoundError()):
        result = get_user_setting()

    assert result == {}


def test_get_user_setting_json_error():
    """Тест случая с ошибкой JSON"""
    with patch("builtins.open", mock_open(read_data="invalid json")):
        result = get_user_setting()

    assert result == {}


# Тесты для exchange_rate
def test_exchange_rate_no_settings():
    """Тест когда нет настроек"""
    result = exchange_rate({})
    assert result == []


def test_exchange_rate_no_currencies():
    """Тест когда нет валют в настройках"""
    result = exchange_rate({"user_currencies": []})
    assert result == []


def test_exchange_rate_missing_api_key():
    """Тест когда отсутствует API ключ"""
    with patch.dict(os.environ, {}, clear=True):
        result = exchange_rate({"user_currencies": ["USD"]})
    assert result == []


def test_exchange_rate_success():
    """Тест успешного получения курсов валют"""
    mock_settings = {"user_currencies": ["USD"]}
    mock_response = {"result": "success", "conversion_rates": {"RUB": 75.5}}

    with patch.dict(os.environ, {"API_KEY_RATE": "test_key"}):
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_response

            result = exchange_rate(mock_settings)

    assert len(result) == 1
    assert result[0]["currency"] == "USD"
    assert result[0]["rate"] == 75.5


def test_exchange_rate_api_error():
    """Тест ошибки API"""
    mock_settings = {"user_currencies": ["USD"]}
    mock_response = {"result": "error", "error-type": "invalid_key"}

    with patch.dict(os.environ, {"API_KEY_RATE": "test_key"}):
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_response

            result = exchange_rate(mock_settings)

    assert result == []


def test_exchange_rate_http_error():
    """Тест HTTP ошибки"""
    mock_settings = {"user_currencies": ["USD"]}

    with patch.dict(os.environ, {"API_KEY_RATE": "test_key"}):
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 404

            result = exchange_rate(mock_settings)

    assert result == []


# Тесты для stock_prices
def test_stock_prices_no_settings():
    """Тест когда нет настроек"""
    result = stock_prices({})
    assert result == []


def test_stock_prices_no_stocks():
    """Тест когда нет акций в настройках"""
    result = stock_prices({"user_stocks": []})
    assert result == []


def test_stock_prices_missing_api_key():
    """Тест когда отсутствует API ключ для акций"""
    with patch.dict(os.environ, {}, clear=True):
        result = stock_prices({"user_stocks": ["AAPL"]})
    assert result == []


def test_stock_prices_success():
    """Тест успешного получения цен акций"""
    mock_settings = {"user_stocks": ["AAPL"]}
    mock_response = [{"price": 150.25}]

    with patch.dict(os.environ, {"API_KEY_STOCK": "test_key"}):
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_response

            result = stock_prices(mock_settings)

    assert len(result) == 1
    assert result[0]["stock"] == "AAPL"
    assert result[0]["price"] == 150.25


def test_stock_prices_empty_response():
    """Тест пустого ответа от API"""
    mock_settings = {"user_stocks": ["AAPL"]}

    with patch.dict(os.environ, {"API_KEY_STOCK": "test_key"}):
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = []

            result = stock_prices(mock_settings)

    assert result == []


def test_stock_prices_missing_price():
    """Тест когда цена отсутствует в ответе"""
    mock_settings = {"user_stocks": ["AAPL"]}
    mock_response = [{"name": "Apple Inc."}]  # Нет поля price

    with patch.dict(os.environ, {"API_KEY_STOCK": "test_key"}):
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_response

            result = stock_prices(mock_settings)

    assert result == []


def test_stock_prices_http_error():
    """Тест HTTP ошибки для акций"""
    mock_settings = {"user_stocks": ["AAPL"]}

    with patch.dict(os.environ, {"API_KEY_STOCK": "test_key"}):
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 500

            result = stock_prices(mock_settings)

    assert result == []


# Интеграционные тесты (просто проверяем что функции работают вместе)
def test_integration_flow():
    """Простой интеграционный тест потока данных"""
    mock_settings = {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}

    # Тестируем что настройки загружаются
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_settings))):
        settings = get_user_setting()

    assert settings == mock_settings

    # Мокаем API вызовы для остальных функций
    with patch.dict(os.environ, {"API_KEY_RATE": "test_key", "API_KEY_STOCK": "test_key"}):
        with patch("requests.get") as mock_get:
            # Настраиваем мок для возврата разных ответов в зависимости от URL
            def side_effect_func():
                call_count = 0

                def inner(*args, **kwargs):
                    nonlocal call_count
                    call_count += 1
                    if call_count == 1:  # Первый вызов - курс валют
                        return MagicMock(
                            status_code=200, json=lambda: {"result": "success", "conversion_rates": {"RUB": 75.5}}
                        )
                    else:  # Второй вызов - цена акций
                        return MagicMock(status_code=200, json=lambda: [{"price": 150.25}])

                return inner

            mock_get.side_effect = side_effect_func()

            rates = exchange_rate(settings)
            stocks = stock_prices(settings)

    assert len(rates) == 1
    assert len(stocks) == 1


if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v"])
