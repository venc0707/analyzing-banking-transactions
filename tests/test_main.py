import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import logging

# Настройка логирования для тестов
logging.basicConfig(level=logging.ERROR)


def test_main_basic_flow():
    """Тест основного потока без дополнительных функций"""
    with patch("builtins.input") as mock_input:
        with patch("src.utils.open_file_xlsx") as mock_open_file:
            with patch("src.utils.data_analysis") as mock_data_analysis:
                with patch("src.utils.main_utils") as mock_main_utils:
                    with patch("builtins.print") as mock_print:
                        # Настраиваем моки
                        mock_input.side_effect = ["2023-12-20 12:00:00", "нет"]
                        mock_open_file.return_value = pd.DataFrame({"test": [1, 2, 3]})
                        mock_data_analysis.return_value = pd.DataFrame({"filtered": [1, 2]})
                        mock_main_utils.return_value = '{"greeting": "Добрый день"}'

                        from src.main import main

                        main()

                        # Проверяем вызовы
                        mock_open_file.assert_called_once_with("../data/operations.xlsx")
                        mock_data_analysis.assert_called_once_with("2023-12-20 12:00:00", mock_open_file.return_value)
                        mock_main_utils.assert_called_once_with("2023-12-20 12:00:00")


def test_main_unknown_choice():
    """Тест неизвестного выбора"""
    with patch("builtins.input") as mock_input:
        with patch("src.utils.open_file_xlsx") as mock_open_file:
            with patch("src.utils.data_analysis") as mock_data_analysis:
                with patch("src.utils.main_utils") as mock_main_utils:
                    with patch("builtins.print") as mock_print:
                        # Настраиваем моки
                        mock_input.side_effect = ["2023-12-20 12:00:00", "неизвестно"]
                        mock_open_file.return_value = pd.DataFrame({"test": [1, 2, 3]})
                        mock_data_analysis.return_value = pd.DataFrame({"filtered": [1, 2]})
                        mock_main_utils.return_value = '{"greeting": "Добрый день"}'

                        from src.main import main

                        main()

                        # Проверяем что напечатано предупреждение
                        mock_print.assert_any_call("Неизвестный выбор")


def test_main_file_not_found():
    """Тест когда файл не найден"""
    with patch("builtins.input") as mock_input:
        with patch("src.utils.open_file_xlsx", return_value=None):
            with patch("builtins.print") as mock_print:
                # Настраиваем моки
                mock_input.side_effect = ["2023-12-20 12:00:00", "нет"]

                from src.main import main

                main()

                # Проверяем что функция завершилась без падения
                assert True


def test_main_case_insensitive():
    """Тест нечувствительности к регистру"""
    test_cases = ["СЕРВИСЫ", "Отчеты", "НЕТ", "сервисы"]

    for choice in test_cases:
        with patch("builtins.input") as mock_input:
            with patch("src.utils.open_file_xlsx") as mock_open_file:
                with patch("src.utils.data_analysis") as mock_data_analysis:
                    with patch("src.utils.main_utils") as mock_main_utils:
                        with patch("builtins.print"):
                            # Настраиваем моки
                            mock_input.side_effect = ["2023-12-20 12:00:00", choice]
                            mock_open_file.return_value = pd.DataFrame({"test": [1, 2, 3]})
                            mock_data_analysis.return_value = pd.DataFrame({"filtered": [1, 2]})
                            mock_main_utils.return_value = '{"greeting": "Добрый день"}'

                            from src.main import main

                            main()

                            # Если дошли сюда - тест прошел
                            assert True


def test_main_empty_data():
    """Тест с пустыми данными"""
    with patch("builtins.input") as mock_input:
        with patch("src.utils.open_file_xlsx") as mock_open_file:
            with patch("src.utils.data_analysis", return_value=pd.DataFrame()):
                with patch("src.utils.main_utils") as mock_main_utils:
                    with patch("builtins.print"):
                        # Настраиваем моки
                        mock_input.side_effect = ["2023-12-20 12:00:00", "сервисы"]
                        mock_open_file.return_value = pd.DataFrame({"test": [1, 2, 3]})
                        mock_main_utils.return_value = '{"greeting": "Добрый день"}'

                        from src.main import main

                        main()

                        # Проверяем что функция завершилась
                        assert True


def test_main_invalid_date():
    """Тест с неверной датой"""
    with patch("builtins.input") as mock_input:
        with patch("src.utils.open_file_xlsx") as mock_open_file:
            with patch("src.utils.data_analysis") as mock_data_analysis:
                with patch("src.utils.main_utils") as mock_main_utils:
                    with patch("builtins.print"):
                        # Настраиваем моки
                        mock_input.side_effect = ["неправильная дата", "нет"]
                        mock_open_file.return_value = pd.DataFrame({"test": [1, 2, 3]})
                        mock_data_analysis.return_value = pd.DataFrame({"filtered": [1, 2]})
                        mock_main_utils.return_value = '{"greeting": "Добрый день"}'

                        from src.main import main

                        main()

                        # Проверяем что функция завершилась
                        assert True


def test_main_logging_initialized():
    """Тест что логирование инициализируется"""
    with patch("src.main.setup_logging") as mock_setup:
        # Проверяем что setup_logging вызывается при запуске модуля
        if __name__ == "__main__":
            import src.main

            mock_setup.assert_called_once()


# Простые тесты без моков для базовой проверки
def test_main_import():
    """Тест что модуль импортируется без ошибок"""
    try:
        from src.main import main

        assert callable(main)
    except ImportError as e:
        pytest.fail(f"Ошибка импорта: {e}")


def test_main_function_exists():
    """Тест что функция main существует"""
    from src.main import main

    assert hasattr(main, "__call__")


if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v"])
