import pandas as pd
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from src.utils import open_file_xlsx


def spending_by_category(
    transactions: pd.DataFrame, category: str, date: Optional[str] = None
) -> pd.DataFrame:
    """Траты по категории"""
    try:
        if date:
            end_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        else:
            end_date = datetime.now()
        df["Дата операции"] = pd.to_datetime(
            df["Дата операции"], format="%d.%m.%Y %H:%M:%S"
        )
        start_date = end_date - timedelta(days=90)
        filtered_df = df[
            (df["Дата операции"] >= start_date)
            & (df["Дата операции"] <= end_date)
            & (df["Категория"] == category)
        ]
        return filtered_df
    except Exception as ex:
        print(f"Ошибка: {ex}")


if __name__ == "__main__":
    df = open_file_xlsx("../data/operations.xlsx")
    spending_by_category(df, "Переводы", "2019-01-10 16:26:00")
