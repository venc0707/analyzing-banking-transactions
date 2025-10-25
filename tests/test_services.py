import json
import logging

import pandas as pd
import pytest

from src.services import search_translations

# Настройка логирования для тестов
logging.basicConfig(level=logging.ERROR)  # Уменьшаем уровень логирования для тестов


# Тесты для search_translations
def test_search_translations_empty_dataframe():
    """Тест с пустым DataFrame"""
    empty_df = pd.DataFrame()
    result = search_translations(empty_df)

    # Должен вернуться JSON с пустым списком
    data = json.loads(result)
    assert data == []


def test_search_translations_missing_columns():
    """Тест когда отсутствуют необходимые колонки"""
    # DataFrame без нужных колонок
    df = pd.DataFrame({"Неправильная_колонка": [1, 2, 3], "Другая_колонка": ["a", "b", "c"]})

    result = search_translations(df)
    data = json.loads(result)
    assert data == []


def test_search_translations_no_translations():
    """Тест когда нет переводов"""
    df = pd.DataFrame(
        {
            "Категория": ["Еда", "Транспорт", "Развлечения"],
            "Описание": ["Магазин", "Такси", "Кино"],
            "Дата операции": ["01.01.2023 10:00:00", "02.01.2023 12:00:00", "03.01.2023 15:00:00"],
            "Сумма операции": [-1000, -500, -300],
        }
    )

    result = search_translations(df)
    data = json.loads(result)
    assert data == []


def test_search_translations_found_translations():
    """Тест когда найдены переводы"""
    df = pd.DataFrame(
        {
            "Категория": ["Переводы", "Еда", "Переводы"],
            "Описание": ["Иван П. перевод", "Магазин", "Петр С. платеж"],
            "Дата операции": ["01.01.2023 10:00:00", "02.01.2023 12:00:00", "03.01.2023 15:00:00"],
            "Сумма операции": [-1000, -500, -1500],
        }
    )

    result = search_translations(df)
    data = json.loads(result)

    # Должны найтись 2 перевода
    assert len(data) == 2
    assert data[0]["category"] == "Переводы"
    assert data[0]["amount"] == 1000.0
    assert "Иван" in data[0]["description"]


def test_search_translations_correct_structure():
    """Тест структуры возвращаемых данных"""
    df = pd.DataFrame(
        {
            "Категория": ["Переводы"],
            "Описание": ["Анна К. перевод денег"],
            "Дата операции": ["01.01.2023 10:00:00"],
            "Сумма операции": [-2500.50],
        }
    )

    result = search_translations(df)
    data = json.loads(result)

    # Проверяем структуру объекта
    translation = data[0]
    assert "date" in translation
    assert "amount" in translation
    assert "category" in translation
    assert "description" in translation

    # Проверяем значения
    assert translation["category"] == "Переводы"
    assert translation["amount"] == 2500.50
    assert translation["description"] == "Анна К. перевод денег"


def test_search_translations_multiple_translations():
    """Тест с несколькими переводами"""
    df = pd.DataFrame(
        {
            "Категория": ["Переводы", "Переводы", "Переводы"],
            "Описание": ["Иван И. перевод", "Мария М", "Сергей Сергеев С. отправка"],
            "Дата операции": ["01.01.2023 10:00:00", "02.01.2023 12:00:00", "03.01.2023 15:00:00"],
            "Сумма операции": [-1000, -2000, -3000],
        }
    )

    result = search_translations(df)
    data = json.loads(result)

    assert len(data) == 1
    # Проверяем что суммы положительные (берется модуль)
    for translation in data:
        assert translation["amount"] > 0


def test_search_translations_with_positive_amounts():
    """Тест с положительными суммами (должны браться по модулю)"""
    df = pd.DataFrame(
        {
            "Категория": ["Переводы"],
            "Описание": ["Алексей К. перевод"],
            "Дата операции": ["01.01.2023 10:00:00"],
            "Сумма операции": [1500],  # Положительная сумма
        }
    )

    result = search_translations(df)
    data = json.loads(result)

    # Сумма должна быть положительной (берется abs)
    assert data[0]["amount"] == 1500.0


def test_search_translations_mixed_categories():
    """Тест со смешанными категориями"""
    df = pd.DataFrame(
        {
            "Категория": ["Переводы", "Еда", "Переводы", "Транспорт"],
            "Описание": ["Ольга П. перевод", "Супермаркет", "Дмитрий С. платеж", "Заправка"],
            "Дата операции": [
                "01.01.2023 10:00:00",
                "02.01.2023 12:00:00",
                "03.01.2023 15:00:00",
                "04.01.2023 18:00:00",
            ],
            "Сумма операции": [-1000, -500, -1500, -300],
        }
    )

    result = search_translations(df)
    data = json.loads(result)

    # Должны найтись только 2 перевода
    assert len(data) == 2
    for translation in data:
        assert translation["category"] == "Переводы"


def test_search_translations_date_format():
    """Тест формата даты"""
    df = pd.DataFrame(
        {
            "Категория": ["Переводы"],
            "Описание": ["Елена В. перевод"],
            "Дата операции": [pd.Timestamp("2023-01-01 10:00:00")],  # Timestamp объект
            "Сумма операции": [-1000],
        }
    )

    result = search_translations(df)
    data = json.loads(result)

    # Дата должна быть в строковом формате
    assert isinstance(data[0]["date"], str)
    assert "2023" in data[0]["date"]


def test_search_translations_with_nan_values():
    """Тест с NaN значениями"""
    df = pd.DataFrame(
        {
            "Категория": ["Переводы", "Переводы"],
            "Описание": ["Иван П. перевод", None],  # Одно описание NaN
            "Дата операции": ["01.01.2023 10:00:00", "02.01.2023 12:00:00"],
            "Сумма операции": [-1000, None],  # Одна сумма NaN
        }
    )

    result = search_translations(df)
    data = json.loads(result)

    # Только одна строка должна пройти фильтрацию (с валидным описанием)
    assert len(data) == 1
    assert data[0]["amount"] == 1000.0
    assert data[0]["description"] == "Иван П. перевод"


def test_search_translations_regex_pattern():
    """Тест регулярного выражения для имен - ИСПРАВЛЕННЫЙ С УЧЕТОМ case=False"""
    test_cases = [
        ("Иван П.", True),  # Стандартный формат с точкой
        ("Мария С.", True),  # Стандартный формат с точкой
        ("Петр в.", True),  # Маленькая буква в инициале - ДОЛЖНО ПРОЙТИ из-за case=False
        ("Анна", False),  # Только имя, без инициала
        ("Н. Петр", False),  # Инициал перед именем
        ("Иван Петрович", False),  # Полное имя
        ("иван п.", True),  # Маленькие буквы - ДОЛЖНО ПРОЙТИ из-за case=False
        ("ИВАН П.", True),  # Заглавные буквы с точкой
        ("Иван Иванов И.", False),  # Два слова + инициал
    ]

    for description, should_match in test_cases:
        df = pd.DataFrame(
            {
                "Категория": ["Переводы"],
                "Описание": [f"{description} перевод"],
                "Дата операции": ["01.01.2023 10:00:00"],
                "Сумма операции": [-1000],
            }
        )

        result = search_translations(df)
        data = json.loads(result)

        if should_match:
            assert len(data) == 1, f"Должен найти перевод для '{description}'"
        else:
            assert len(data) == 0, f"Не должен находить перевод для '{description}'"


def test_search_translations_integration():
    """Интеграционный тест с реальными данными"""
    # Более реалистичные данные
    df = pd.DataFrame(
        {
            "Категория": ["Переводы", "Еда", "Переводы", "Транспорт", "Переводы", "Развлечения", "Переводы", "Прочее"],
            "Описание": [
                "Иван Петров И. перевод между счетами",
                "Покупка в супермаркете",
                "Мария Сидорова М. возврат долга",
                "Оплата такси",
                "Петр Васильев П. денежный перевод",
                "Билеты в кино",
                "Анна К. подарок",  # True (Имя с инициалом.)
                "Прочие расходы",
            ],
            "Дата операции": [
                "15.01.2023 14:30:00",
                "16.01.2023 09:15:00",
                "17.01.2023 16:45:00",
                "18.01.2023 11:20:00",
                "19.01.2023 13:10:00",
                "20.01.2023 20:00:00",
                "21.01.2023 10:05:00",
                "22.01.2023 12:30:00",
            ],
            "Сумма операции": [-5000, -1500, -3000, -400, -2000, -800, -1000, -200],
        }
    )

    result = search_translations(df)
    data = json.loads(result)

    # Должны найти 1 перевода
    assert len(data) == 1

    # Проверяем общую сумму
    total_amount = sum(item["amount"] for item in data)
    expected_total = 1000  # Суммы по модулю
    assert total_amount == expected_total

    # Проверяем что все найденные - переводы
    for item in data:
        assert item["category"] == "Переводы"


def test_search_translations_error_handling():
    """Тест обработки ошибок"""
    # Создаем проблемные данные
    df = pd.DataFrame(
        {
            "Категория": ["Переводы"],
            "Описание": ["Тест П. перевод"],
            "Дата операции": ["неправильная дата"],  # Проблемная дата
            "Сумма операции": ["не число"],  # Проблемная сумма
        }
    )

    # Функция должна обработать это без падения
    result = search_translations(df)
    data = json.loads(result)

    # Может вернуть пустой список или обработать как-то иначе
    assert isinstance(data, list)


if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v"])
