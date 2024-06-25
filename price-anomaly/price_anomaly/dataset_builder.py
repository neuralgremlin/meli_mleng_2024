import re
import sqlite3
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from price_anomaly import load_config


class DatasetBuilder:
    def __init__(self):
        self.config = load_config()

    def build(self, database_path: Path, output_dir: Path):
        df = self.read_data(database_path)
        df = self.create_new_features(df)
        df = self.label_outliers(df, "PRICE", "ITEM_ID")
        df.to_csv(output_dir, index=False)

    @staticmethod
    def read_data(data_path: Path) -> pd.DataFrame:
        return pd.read_csv(data_path)

    def create_new_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df["item_mean_price"] = df.groupby("ITEM_ID")["PRICE"].transform("mean")
        df["price_deviation"] = df["PRICE"] - df["item_mean_price"]
        df["item_count"] = df.groupby("ITEM_ID")["ITEM_ID"].transform("count")
        df["DOMINANTES"] = df["ITEM_ID"].where(df["item_count"] > 500, other="OTROS")

        return df

    def label_outliers(
        self, df: pd.DataFrame, column: str, group_col: str
    ) -> pd.DataFrame:
        anomalies = pd.DataFrame()
        for item in df[group_col].unique():
            item_data = df[df[group_col] == item]
            Q1 = item_data[column].quantile(0.25)
            Q3 = item_data[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            item_anomalies = item_data[
                (item_data[column] < lower_bound) | (item_data[column] > upper_bound)
            ]
            anomalies = pd.concat([anomalies, item_anomalies])

        df["manual_label"] = 0  # 0 indica normal
        df.loc[anomalies.index, "manual_label"] = 1

        return df
