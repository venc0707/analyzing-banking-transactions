import json
import pandas as pd
from pandas import DataFrame


pd.set_option("display.max_columns", None)


def search_translations(df: DataFrame) -> list[dict]:
    """Поиск переводов физическим лицам"""
    try:
        list_translations = []
        df_group = df[
            (df["Категория"] == "Переводы")
            & df["Описание"].str.contains(r"^[А-Я]\w+\s[А-Я][.]", case=False, na=False)
        ]
        for i, data in df_group.iterrows():
            translation = {
                "date": data["Дата операции"].strftime("%d.%m.%Y %H:%M:%S"),
                "amount": data["Сумма операции"],
                "category": data["Категория"],
                "description": data["Описание"],
            }
            list_translations.append(translation)
        json_list_translations = json.dumps(
            list_translations, indent=2, ensure_ascii=False
        )
        # print(json_list_translations)
        return json_list_translations

    except Exception as ex:
        print(f"Ошибка: {ex}")


# if __name__ == "__main__":
#     df = open_file_xlsx("../data/operations.xlsx")
#     search_translations(df)
