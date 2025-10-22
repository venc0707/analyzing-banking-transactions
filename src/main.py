from src.utils import main_utils, open_file_xlsx, data_analysis
from src.services import search_translations
from src.reports import spending_by_category
from utils_logs.logger_utils import get_logger, log_execution_time
from config.logging_config import setup_logging

logger = get_logger(__name__)


def main():
    """главная функция проекта"""
    logger.info("🚀 ЗАПУСК ГЛАВНОЙ ФУНКЦИИ ПРОЕКТА")

    try:
        with log_execution_time("Работа главной функции", __name__):
            # Логируем ввод пользователя
            logger.info("⏰ ОЖИДАНИЕ ВВОДА ДАТЫ ОТ ПОЛЬЗОВАТЕЛЯ")
            current_time = input('Введите дату и время в формате: "YYYY-MM-DD HH:MM:SS" ')
            logger.info("📅 ПОЛЬЗОВАТЕЛЬ ВВЕЛ ДАТУ: %s", current_time)

            # загружаем данные
            logger.info("📁 НАЧАЛО ЗАГРУЗКИ ДАННЫХ")
            df = open_file_xlsx("../data/operations.xlsx")
            logger.info("✅ ДАННЫЕ ЗАГРУЖЕНЫ ИЗ ФАЙЛА")

            logger.info("🔍 ЗАПУСК АНАЛИЗА ДАННЫХ ПО ПЕРИОДУ")
            df_analysis = data_analysis(current_time, df)
            logger.info("✅ АНАЛИЗ ДАННЫХ ЗАВЕРШЕН")

            # получение страницы "Главная"
            logger.info("🏠 ФОРМИРОВАНИЕ ГЛАВНОЙ СТРАНИЦЫ")
            home = main_utils(current_time)
            logger.info("✅ ГЛАВНАЯ СТРАНИЦА СФОРМИРОВАНА")
            print(home)

            logger.info("❓ ОЖИДАНИЕ ВЫБОРА ДОПОЛНИТЕЛЬНЫХ ФУНКЦИЙ")
            additional_functions = input('Есть вкладки: "Отчеты" "Сервисы", "нет" - ничего не делать ').lower()
            logger.info("🎯 ПОЛЬЗОВАТЕЛЬ ВЫБРАЛ: %s", additional_functions)

            if additional_functions == "нет":
                logger.info("➡️  ПОЛЬЗОВАТЕЛЬ ВЫБРАЛ ЗАВЕРШЕНИЕ БЕЗ ДОПОЛНИТЕЛЬНЫХ ФУНКЦИЙ")
                pass
            elif additional_functions == "сервисы":
                logger.info("🛠️  ЗАПУСК РАЗДЕЛА 'СЕРВИСЫ'")
                print("В данный момент из сервисов доступны только: 'Поиск переводов физическим лицам'")

                logger.info("🔍 ВЫПОЛНЕНИЕ ПОИСКА ПЕРЕВОДОВ ФИЗИЧЕСКИМ ЛИЦАМ")
                print(df_analysis)
                search = search_translations(df_analysis)
                logger.info("✅ ПОИСК ПЕРЕВОДОВ ЗАВЕРШЕН | Найдено записей: %s", len(search) if search else 0)
                print(search)
            elif additional_functions == "отчеты":
                logger.info("📊 ЗАПУСК РАЗДЕЛА 'ОТЧЕТЫ'")
                print("Из отчетов в данный момент доступен только отчет: 'Траты по категории за последние 90 дней'")

                logger.info("💰 ФОРМИРОВАНИЕ ОТЧЕТА ПО КАТЕГОРИИ 'ПЕРЕВОДЫ'")
                report = spending_by_category(transactions=df, category="Переводы", date=current_time)
                logger.info(
                    "✅ ОТЧЕТ ПО КАТЕГОРИИ СФОРМИРОВАН | Записей в отчете: %s",
                    len(report) if hasattr(report, "__len__") else "N/A",
                )
                print(report)
            else:
                logger.warning("⚠️  НЕИЗВЕСТНЫЙ ВЫБОР ПОЛЬЗОВАТЕЛЯ: %s", additional_functions)
                print("Неизвестный выбор")

        logger.info("🎯 ГЛАВНАЯ ФУНКЦИЯ УСПЕШНО ЗАВЕРШЕНА")
    except Exception as e:
        logger.error("❌ КРИТИЧЕСКАЯ ОШИБКА В ГЛАВНОЙ ФУНКЦИИ | Тип: %s", type(e).__name__, exc_info=True)
        print(f"Произошла ошибка: {e}")

    finally:
        logger.info("🏁 ЗАВЕРШЕНИЕ РАБОТЫ ПРИЛОЖЕНИЯ")


if __name__ == "__main__":
    setup_logging()
    main()
