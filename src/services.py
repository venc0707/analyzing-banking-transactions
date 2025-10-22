import json
import pandas as pd
from pandas import DataFrame
from typing import Dict, List, Any
from utils_logs.logger_utils import get_logger, log_function_call, log_execution_time, log_dataframe_info


pd.set_option("display.max_columns", None)
# Получаем логгер используя нашу утилиту
logger = get_logger(__name__)


@log_function_call("INFO")
def search_translations(df: DataFrame) -> List[Dict]:
    """Поиск переводов физическим лицам"""

    try:
        # Логируем входные данные используя нашу утилиту
        log_dataframe_info(df, "Входные данные для поиска переводов", __name__)

        if df.empty:
            logger.warning("⚠️  ПУСТОЙ DATAFRAME ДЛЯ ПОИСКА ПЕРЕВОДОВ")
            return json.dumps([], ensure_ascii=False)

        # Проверяем наличие необходимых колонок
        required_columns = ["Категория", "Описание", "Дата операции", "Сумма операции"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            logger.error(
                "❌ ОТСУТСТВУЮТ ОБЯЗАТЕЛЬНЫЕ КОЛОНКИ: %s | Доступные колонки: %s", missing_columns, list(df.columns)
            )
            return json.dumps([], ensure_ascii=False)

        # Поиск переводов физическим лицам
        logger.info("🎯 ФИЛЬТРАЦИЯ ПЕРЕВОДОВ ФИЗЛИЦАМ")
        logger.debug("🔍 РЕГУЛЯРНОЕ ВЫРАЖЕНИЕ: ^[А-Я]\\w+\\s[А-Я][.] - Имя с инициалом")

        initial_count = len(df)

        with log_execution_time("Фильтрация переводов", __name__):
            df_group = df[
                (df["Категория"] == "Переводы")
                & df["Описание"].str.contains(r"^[А-Я]\w+\s[А-Я][.]", case=False, na=False)
            ]

        filtered_count = len(df_group)
        efficiency = (filtered_count / initial_count * 100) if initial_count > 0 else 0

        logger.info(
            "✅ ФИЛЬТРАЦИЯ ЗАВЕРШЕНА | Исходно: %,d | Найдено переводов: %,d | Эффективность: %.1f%%",
            initial_count,
            filtered_count,
            efficiency,
        )

        if df_group.empty:
            logger.warning("⚠️  ПЕРЕВОДЫ ФИЗИЧЕСКИМ ЛИЦАМ НЕ НАЙДЕНЫ")
            return json.dumps([], ensure_ascii=False)

        # Формируем список переводов
        logger.info("📝 ФОРМИРОВАНИЕ СПИСКА ПЕРЕВОДОВ")
        list_translations = []
        total_amount = 0

        with log_execution_time("Обработка найденных переводов", __name__):
            for i, data in df_group.iterrows():
                try:
                    # Безопасное извлечение данных
                    date_value = data["Дата операции"]
                    if hasattr(date_value, "strftime"):
                        date_str = date_value.strftime("%d.%m.%Y %H:%M:%S")
                    elif isinstance(date_value, str):
                        date_str = date_value
                    else:
                        date_str = str(date_value)

                    amount = float(data["Сумма операции"]) if pd.notna(data["Сумма операции"]) else 0.0
                    category = str(data["Категория"]) if pd.notna(data["Категория"]) else "Неизвестно"
                    description = str(data["Описание"]) if pd.notna(data["Описание"]) else "Без описания"

                    translation = {
                        "date": date_str,
                        "amount": round(abs(amount), 2),
                        "category": category,
                        "description": description,
                    }
                    list_translations.append(translation)
                    total_amount += abs(amount)

                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(
                            "💸 НАЙДЕН ПЕРЕВОД | Дата: %s | Сумма: %,.2f | Описание: %.50s",
                            date_str,
                            amount,
                            description,
                        )

                except Exception as row_error:
                    logger.warning("⚠️  ОШИБКА ОБРАБОТКИ СТРОКИ %d | Тип: %s", i, type(row_error).__name__)
                    continue

            # Логируем итоговую статистику
            if list_translations:
                avg_translation = total_amount / len(list_translations) if list_translations else 0
                logger.info(
                    "📊 ИТОГИ ПОИСКА ПЕРЕВОДОВ | Переводов: %d | Общая сумма: %,.2f | Средний перевод: %,.2f",
                    len(list_translations),
                    total_amount,
                    avg_translation,
                )
            else:
                logger.warning("📊 ПЕРЕВОДЫ НЕ НАЙДЕНЫ ПОСЛЕ ОБРАБОТКИ")
                return json.dumps([], ensure_ascii=False)

            # Конвертируем в JSON
            logger.debug("🔄 КОНВЕРТАЦИЯ В JSON ФОРМАТ")
            try:
                json_list_translations = json.dumps(list_translations, indent=2, ensure_ascii=False, default=str)
                logger.info(
                    "✅ JSON СФОРМИРОВАН | Размер: %,d символов | Переводов: %d",
                    len(json_list_translations),
                    len(list_translations),
                )
                return json_list_translations

            except Exception as json_error:
                logger.error("❌ ОШИБКА КОНВЕРТАЦИИ В JSON | Тип: %s", type(json_error).__name__, exc_info=True)
                return json.dumps([], ensure_ascii=False)

    except Exception as ex:
        logger.error("❌ КРИТИЧЕСКАЯ ОШИБКА В search_translations | Тип: %s", type(ex).__name__, exc_info=True)
        return json.dumps([], ensure_ascii=False)


# if __name__ == "__main__":
#     df = open_file_xlsx("../data/operations.xlsx")
#     search_translations(df)
