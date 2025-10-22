import pandas as pd
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from src.utils import open_file_xlsx
from utils_logs.logger_utils import get_logger, log_function_call, log_execution_time, log_dataframe_info

logger = get_logger(__name__)


@log_function_call("INFO")
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Траты по категории за последние 90 дней"""

    logger.info(
        "💰 АНАЛИЗ РАСХОДОВ ПО КАТЕГОРИИ | Категория: '%s' | Дата: %s", category, date if date else "текущая дата"
    )

    try:
        # Логируем входные данные
        log_dataframe_info(transactions, "Входные данные транзакций", __name__)
        logger.debug(
            "📋 КАТЕГОРИИ В ДАННЫХ: %s",
            transactions["Категория"].unique() if "Категория" in transactions.columns else "Колонка не найдена",
        )
        # Проверяем наличие необходимых колонок
        required_columns = ["Категория", "Дата операции"]
        missing_columns = [col for col in required_columns if col not in transactions.columns]
        if missing_columns:
            logger.error(
                "❌ ОТСУТСТВУЮТ ОБЯЗАТЕЛЬНЫЕ КОЛОНКИ: %s | Доступные колонки: %s",
                missing_columns,
                list(transactions.columns),
            )
            return pd.DataFrame()

        # Определяем период анализа
        with log_execution_time("Определение периода анализа", __name__):
            if date:
                end_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                logger.debug("📅 ИСПОЛЬЗУЕТСЯ УКАЗАННАЯ ДАТА: %s", end_date)
            else:
                end_date = datetime.now()
                logger.debug("📅 ИСПОЛЬЗУЕТСЯ ТЕКУЩАЯ ДАТА: %s", end_date)

            start_date = end_date - timedelta(days=90)
            logger.info(
                "📅 ПЕРИОД АНАЛИЗА | Начало: %s | Конец: %s | Дней: 90",
                start_date.strftime("%d.%m.%Y"),
                end_date.strftime("%d.%m.%Y"),
            )

            # Преобразуем даты
            with log_execution_time("Преобразование дат", __name__):
                initial_count = len(transactions)
                transactions["Дата операции"] = pd.to_datetime(
                    transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce"
                )

                # Проверяем успешность преобразования дат
                failed_dates = transactions["Дата операции"].isna().sum()
                if failed_dates > 0:
                    logger.warning(
                        "⚠️  НЕ УДАЛОСЬ ПРЕОБРАЗОВАТЬ ДАТЫ | Невалидных дат: %d из %d", failed_dates, initial_count
                    )
                    # Фильтруем данные
            with log_execution_time("Фильтрация данных по категории и периоду", __name__):
                # Проверяем существование категории
                available_categories = transactions["Категория"].unique()
                if category not in available_categories:
                    logger.warning(
                        "⚠️  КАТЕГОРИЯ НЕ НАЙДЕНА | Запрошенная: '%s' | Доступные: %s",
                        category,
                        list(available_categories),
                    )
                    return pd.DataFrame()
                # Применяем фильтры
                filtered_df = transactions[
                    (transactions["Дата операции"] >= start_date)
                    & (transactions["Дата операции"] <= end_date)
                    & (transactions["Категория"] == category)
                ]
            # Логируем результаты фильтрации
            filtered_count = len(filtered_df)
            efficiency = (filtered_count / initial_count * 100) if initial_count > 0 else 0

            logger.info(
                "✅ ФИЛЬТРАЦИЯ ЗАВЕРШЕНА | Исходно: %,d | Отфильтровано: %,d | Эффективность: %.1f%%",
                initial_count,
                filtered_count,
                efficiency,
            )
            if filtered_df.empty:
                logger.warning(
                    "⚠️  НЕТ ДАННЫХ ПО КАТЕГОРИИ | Категория: '%s' | Период: %s - %s",
                    category,
                    start_date.strftime("%d.%m.%Y"),
                    end_date.strftime("%d.%m.%Y"),
                )
                return filtered_df

            # Логируем информацию об отфильтрованных данных
            log_dataframe_info(filtered_df, f"Данные по категории '{category}'", __name__)

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    "📝 ПЕРВЫЕ 5 ТРАНЗАКЦИЙ ПО КАТЕГОРИИ '%s':\n%s",
                    category,
                    filtered_df[["Дата операции", "Сумма операции", "Описание"]].head().to_string(),
                )
                return filtered_df

    except Exception as ex:
        logger.error(
            "❌ ОШИБКА В spending_by_category | Категория: '%s' | Тип: %s", category, type(ex).__name__, exc_info=True
        )
        return pd.DataFrame()


if __name__ == "__main__":
    df = open_file_xlsx("../data/operations.xlsx")
    # spending_by_category(df, "Переводы", "2019-01-10 16:26:00")

    if df is not None:
        # Анализ расходов по категории "Супермаркеты"
        result = spending_by_category(transactions=df, category="Супермаркеты", date="2024-01-15 10:00:00")

        if not result.empty:
            logger.info("✅ АНАЛИЗ ЗАВЕРШЕН УСПЕШНО")
        else:
            logger.info("ℹ️  ДАННЫЕ ПО КАТЕГОРИИ НЕ НАЙДЕНЫ")
