import logging
import time
import functools
from contextlib import contextmanager
from typing import Optional
from pandas import DataFrame


def get_logger(name: str) -> logging.Logger:
    """Получить логгер для указанного имени с учетом конфигурации"""
    return logging.getLogger(name)


def log_function_call(level: str = "INFO"):
    """Декоратор для логирования вызовов функций с улучшенным форматированием"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            log_level = getattr(logging, level.upper())

            # Форматируем аргументы для логирования
            args_repr = [repr(a) for a in args[1:]] if args else []
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)

            if len(signature) > 200:  # Ограничиваем длину для читаемости
                signature = signature[:200] + "..."

            logger.log(log_level, "🚀 ВЫЗОВ: %s | Аргументы: %s", func.__name__, signature or "None")

            try:
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time

                # Логируем успешное завершение
                result_info = f"Тип: {type(result).__name__}"
                if hasattr(result, "shape"):
                    result_info += f", Размер: {result.shape}"
                elif hasattr(result, "__len__"):
                    result_info += f", Длина: {len(result)}"

                logger.log(
                    log_level, "✅ УСПЕХ: %s | Время: %.3f сек | %s", func.__name__, execution_time, result_info
                )

                return result

            except Exception as e:
                logger.error(
                    "❌ ОШИБКА: %s | Тип: %s | Сообщение: %s", func.__name__, type(e).__name__, str(e), exc_info=True
                )
                raise

        return wrapper

    return decorator


@contextmanager
def log_execution_time(operation_name: str, logger_name: Optional[str] = None):
    """
    Контекстный менеджер для логирования времени выполнения

    Args:
        operation_name: название операции
        logger_name: имя логгера (если None, используется корневой)
    """
    logger = get_logger(logger_name) if logger_name else get_logger(__name__)

    start_time = time.time()
    logger.info("⏰ НАЧАЛО: %s", operation_name)

    try:
        yield
    except Exception as e:
        logger.error(
            "💥 ОШИБКА В: %s | Тип: %s | Сообщение: %s", operation_name, type(e).__name__, str(e), exc_info=True
        )
        raise
    finally:
        end_time = time.time()
        duration = end_time - start_time
        logger.info("⏰ ЗАВЕРШЕНИЕ: %s | Затрачено: %.3f сек", operation_name, duration)


def log_dataframe_info(df: DataFrame, df_name: str = "DataFrame", logger_name: Optional[str] = None):
    """Логирует информацию о DataFrame с улучшенным форматированием"""
    logger = get_logger(logger_name) if logger_name else get_logger(__name__)

    if df is not None and not df.empty:
        memory_usage = df.memory_usage(deep=True).sum() / 1024**2

        logger.info(
            "📊 ДАННЫЕ: %s | Строк: %,d | Столбцов: %d | Память: %.2f MB",
            df_name,
            len(df),
            len(df.columns),
            memory_usage,
        )

        # Детальная информация только в debug режиме
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("📋 СТОЛБЦЫ %s: %s", df_name, list(df.columns))
            logger.debug("📝 ТИПЫ ДАННЫХ %s:\n%s", df_name, df.dtypes)
    elif df is not None and df.empty:
        logger.warning("⚠️  ПУСТОЙ DATAFRAME: %s", df_name)
    else:
        logger.error("❌ DATAFRAME НЕОПРЕДЕЛЕН: %s", df_name)


def log_data_quality(df: DataFrame, df_name: str = "DataFrame", logger_name: Optional[str] = None):
    """Логирует информацию о качестве данных с улучшенным форматированием"""
    logger = get_logger(logger_name) if logger_name else get_logger(__name__)

    if df is not None and not df.empty:
        missing_data = df.isnull().sum()
        total_missing = missing_data.sum()
        total_cells = len(df) * len(df.columns)
        completeness = (1 - total_missing / total_cells) * 100 if total_cells > 0 else 0

        logger.info(
            "🔍 КАЧЕСТВО ДАННЫХ: %s | Пропущено: %,d | Заполненность: %.1f%%", df_name, total_missing, completeness
        )

        if total_missing > 0 and logger.isEnabledFor(logging.DEBUG):
            missing_by_column = {col: count for col, count in missing_data.items() if count > 0}
            logger.debug("📝 ПРОПУЩЕНО ПО СТОЛБЦАМ %s: %s", df_name, missing_by_column)

            # Дополнительная статистика
            numeric_cols = df.select_dtypes(include=["number"]).columns
            if len(numeric_cols) > 0:
                logger.debug("📈 СТАТИСТИКА ЧИСЛОВЫХ СТОЛБЦОВ %s:\n%s", df_name, df[numeric_cols].describe())
    elif df is not None and df.empty:
        logger.warning("⚠️  НЕВОЗМОЖНО ПРОВЕРИТЬ КАЧЕСТВО: %s пуст", df_name)
    else:
        logger.error("❌ НЕВОЗМОЖНО ПРОВЕРИТЬ КАЧЕСТВО: %s не определен", df_name)


def log_dict_structure(data: dict, data_name: str = "Dictionary", logger_name: Optional[str] = None):
    """Логирует структуру словаря"""
    logger = get_logger(logger_name) if logger_name else get_logger(__name__)

    if data:
        structure = {key: type(value).__name__ for key, value in data.items()}
        logger.debug("🏗️  СТРУКТУРА %s: %s", data_name, structure)
    else:
        logger.warning("⚠️  ПУСТОЙ СЛОВАРЬ: %s", data_name)
