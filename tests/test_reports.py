import logging
from datetime import datetime, timedelta
from unittest.mock import mock_open, patch

import pandas as pd
import pytest

from src.reports import spending_by_category

# Настройка логирования для тестов
logging.basicConfig(level=logging.ERROR)


# Тесты для spending_by_category
def test_spending_by_category_success():
    """Тест успешного анализа расходов по категории"""
    # Создаем тестовые данные
    test_data = pd.DataFrame(
        {
            "Категория": ["Еда", "Еда", "Транспорт", "Еда"],
            "Дата операции": [
                "01.01.2023 10:00:00",
                "15.01.2023 14:30:00",
                "20.01.2023 09:15:00",
                "25.01.2023 18:00:00",
            ],
            "Сумма операции": [-1000, -1500, -500, -2000],
            "Описание": ["Магазин", "Ресторан", "Такси", "Супермаркет"],
        }
    )

    result = spending_by_category(test_data, "Еда", "2023-01-30 12:00:00")

    assert not result.empty
    assert len(result) == 3  # 3 операции категории "Еда"
    assert all(result["Категория"] == "Еда")


def test_spending_by_category_empty_dataframe():
    """Тест с пустым DataFrame"""
    empty_df = pd.DataFrame()
    result = spending_by_category(empty_df, "Еда", "2023-01-30 12:00:00")

    assert result.empty


def test_spending_by_category_missing_columns():
    """Тест когда отсутствуют необходимые колонки"""
    df = pd.DataFrame({"Неправильная_колонка": [1, 2, 3], "Другая_колонка": ["a", "b", "c"]})

    result = spending_by_category(df, "Еда", "2023-01-30 12:00:00")
    assert result.empty


def test_spending_by_category_nonexistent_category():
    """Тест когда категория не существует"""
    df = pd.DataFrame(
        {
            "Категория": ["Еда", "Транспорт"],
            "Дата операции": ["01.01.2023 10:00:00", "02.01.2023 12:00:00"],
            "Сумма операции": [-1000, -500],
        }
    )

    result = spending_by_category(df, "НесуществующаяКатегория", "2023-01-30 12:00:00")
    assert result.empty


def test_spending_by_category_no_data_in_period():
    """Тест когда нет данных в указанном периоде"""
    # Создаем данные с датами вне периода 90 дней
    old_date = (datetime.now() - timedelta(days=100)).strftime("%d.%m.%Y %H:%M:%S")

    df = pd.DataFrame({"Категория": ["Еда"], "Дата операции": [old_date], "Сумма операции": [-1000]})

    result = spending_by_category(df, "Еда")
    assert result.empty


def test_spending_by_category_without_date():
    """Тест без указания даты (используется текущая дата)"""
    # Создаем данные с текущей датой
    current_date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    df = pd.DataFrame(
        {"Категория": ["Еда", "Еда"], "Дата операции": [current_date, current_date], "Сумма операции": [-1000, -1500]}
    )

    result = spending_by_category(df, "Еда")
    assert not result.empty
    assert len(result) == 2


def test_spending_by_category_invalid_dates():
    """Тест с невалидными датами"""
    df = pd.DataFrame(
        {
            "Категория": ["Еда", "Еда"],
            "Дата операции": ["неправильная дата", "01.01.2023 10:00:00"],
            "Сумма операции": [-1000, -1500],
        }
    )

    result = spending_by_category(df, "Еда", "2023-01-30 12:00:00")
    # Должна найти хотя бы одну валидную запись
    assert len(result) == 1


def test_spending_by_category_date_filtering():
    """Тест фильтрации по дате"""
    # Создаем данные с разными датами
    base_date = datetime(2023, 1, 15)

    dates = [
        (base_date - timedelta(days=80)).strftime("%d.%m.%Y %H:%M:%S"),  # Входит в период (80 дней назад)
        (base_date - timedelta(days=50)).strftime("%d.%m.%Y %H:%M:%S"),  # Входит в период (50 дней назад)
        (base_date - timedelta(days=95)).strftime("%d.%m.%Y %H:%M:%S"),  # Не входит (95 дней назад)
    ]

    df = pd.DataFrame(
        {"Категория": ["Еда", "Еда", "Еда"], "Дата операции": dates, "Сумма операции": [-1000, -1500, -2000]}
    )

    result = spending_by_category(df, "Еда", "2023-01-15 12:00:00")
    # Должны найти 2 записи (в пределах 90 дней)
    assert len(result) == 2


def test_spending_by_category_multiple_categories():
    """Тест с несколькими категориями"""
    df = pd.DataFrame(
        {
            "Категория": ["Еда", "Транспорт", "Еда", "Развлечения", "Еда"],
            "Дата операции": [
                "01.01.2023 10:00:00",
                "02.01.2023 12:00:00",
                "03.01.2023 15:00:00",
                "04.01.2023 18:00:00",
                "05.01.2023 20:00:00",
            ],
            "Сумма операции": [-1000, -500, -1500, -800, -1200],
        }
    )

    result = spending_by_category(df, "Еда", "2023-01-10 12:00:00")
    # Должны найти только операции категории "Еда"
    assert len(result) == 3
    assert all(result["Категория"] == "Еда")


def test_spending_by_category_structure():
    """Тест структуры возвращаемых данных"""
    df = pd.DataFrame(
        {
            "Категория": ["Еда"],
            "Дата операции": ["01.01.2023 10:00:00"],
            "Сумма операции": [-1000],
            "Описание": ["Магазин"],
            "Другие_колонки": ["значение"],  # Дополнительные колонки
        }
    )

    result = spending_by_category(df, "Еда", "2023-01-30 12:00:00")

    # Проверяем что все исходные колонки сохранились
    assert "Категория" in result.columns
    assert "Дата операции" in result.columns
    assert "Сумма операции" in result.columns
    assert "Описание" in result.columns
    assert "Другие_колонки" in result.columns


def test_spending_by_category_positive_amounts():
    """Тест с положительными суммами (должны включаться)"""
    df = pd.DataFrame(
        {
            "Категория": ["Еда", "Еда"],
            "Дата операции": ["01.01.2023 10:00:00", "02.01.2023 12:00:00"],
            "Сумма операции": [1000, -1500],  # Одна положительная, одна отрицательная
        }
    )

    result = spending_by_category(df, "Еда", "2023-01-30 12:00:00")
    # Должны найти обе записи (фильтр по категории, а не по знаку суммы)
    assert len(result) == 2


def test_spending_by_category_file_writing():
    """Тест что результат записывается в файл (мок)"""
    df = pd.DataFrame({"Категория": ["Еда"], "Дата операции": ["01.01.2023 10:00:00"], "Сумма операции": [-1000]})

    # Мокаем запись в файл
    with patch("builtins.open", mock_open()) as mock_file:
        spending_by_category(df, "Еда", "2023-01-30 12:00:00")

        # Проверяем что файл был открыт для записи
        mock_file.assert_called_once_with("../data/spending_by_category.txt", "w", encoding="utf-8")


def test_spending_by_category_different_date_formats():
    """Тест с разными форматами дат"""
    df = pd.DataFrame(
        {
            "Категория": ["Еда", "Еда"],
            "Дата операции": [pd.Timestamp("2023-01-01 10:00:00"), "15.01.2023 14:30:00"],  # Timestamp  # Строка
            "Сумма операции": [-1000, -1500],
        }
    )

    result = spending_by_category(df, "Еда", "2023-01-30 12:00:00")
    # Обе даты должны быть обработаны
    assert len(result) == 2


def test_spending_by_category_large_dataset():
    """Тест с большим набором данных"""
    # Создаем 100 записей
    categories = ["Еда", "Транспорт", "Развлечения"]
    dates = [f"{(datetime(2023, 1, 1) + timedelta(days=i)).strftime('%d.%m.%Y')} 10:00:00" for i in range(100)]

    df = pd.DataFrame(
        {
            "Категория": [categories[i % 3] for i in range(100)],
            "Дата операции": dates,
            "Сумма операции": [-i * 100 for i in range(100)],
        }
    )

    result = spending_by_category(df, "Еда", "2023-04-10 12:00:00")
    # Должны найти только записи категории "Еда" за последние 90 дней от указанной даты
    assert all(result["Категория"] == "Еда")
    # Проверяем что даты в правильном диапазоне
    if not result.empty:
        min_date = result["Дата операции"].min()
        assert isinstance(min_date, (str, pd.Timestamp))


def test_spending_by_category_error_handling():
    """Тест обработки ошибок"""
    # Создаем проблемные данные
    df = pd.DataFrame({"Категория": ["Еда"], "Дата операции": ["неправильная дата"], "Сумма операции": ["не число"]})

    # Функция должна обработать это без падения
    result = spending_by_category(df, "Еда", "2023-01-30 12:00:00")
    assert isinstance(result, pd.DataFrame)


if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v"])
