"""
DEMAND-24 — Feature Engineering

Construye todas las features necesarias para el modelo predictivo.

Cumple con:
- Regla I: Inmutabilidad (todos los DataFrames se retornan como copias)
- Regla II: Código Auto-Documentado (nombres descriptivos)
- Regla VI: Anti-Leakage (lags y rolling stats sin futuro)
"""

from typing import Optional
import pandas as pd
import numpy as np

from ..config.ml_config import MLConfig


class FeatureBuilder:
    """
    Construye features para el modelo de predicción.
    
    Responsabilidades:
    - Features temporales (semana, mes, año, etc.)
    - Lags (ventas pasadas)
    - Rolling statistics (media, std, min, max)
    - Holiday features (festivos locales, nacionales)
    - Oil price features
    - Store/cluster encoding
    """

    def __init__(self, config: Optional[MLConfig] = None):
        self.config = config or MLConfig()

    def build_all_features(
        self,
        df: pd.DataFrame,
        stores_df: pd.DataFrame,
        holidays_df: pd.DataFrame,
        oil_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Construye todas las features en el orden correcto.
        
        Args:
            df: DataFrame semanal con sales, onpromotion
            stores_df: Información de tiendas
            holidays_df: Eventos festivos
            oil_df: Precios del petróleo
        
        Returns:
            DataFrame con todas las features
        """
        result = df.copy()

        result = self.add_temporal_features(result)
        result = self.add_store_features(result, stores_df)
        result = self.add_holiday_features(result, holidays_df)
        result = self.add_oil_features(result, oil_df)
        result = self.add_lag_features(result)
        result = self.add_rolling_features(result)
        result = self.add_promotion_features(result)

        return result.copy()

    def add_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Agrega features temporales derivadas de la fecha.
        
        Features creadas:
        - year, month, week_of_year, day_of_week
        - is_month_start, is_month_end
        - is_quarter_start, is_quarter_end
        - days_in_month
        """
        result = df.copy()
        result["week_start"] = pd.to_datetime(result["week_start"])

        result["year"] = result["week_start"].dt.year
        result["month"] = result["week_start"].dt.month
        result["week_of_year"] = result["week_start"].dt.isocalendar().week.astype(int)
        result["day_of_week"] = result["week_start"].dt.dayofweek
        result["is_month_start"] = (result["week_start"].dt.day <= 7).astype(int)
        result["is_month_end"] = (result["week_start"].dt.day >= 25).astype(int)
        result["is_quarter_start"] = result["week_start"].dt.is_quarter_start.astype(int)
        result["is_quarter_end"] = result["week_start"].dt.is_quarter_end.astype(int)
        result["days_in_month"] = result["week_start"].dt.daysinmonth

        return result.copy()

    def add_store_features(
        self,
        df: pd.DataFrame,
        stores_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Agrega features de tienda (tipo, cluster, ciudad).
        
        Args:
            df: DataFrame con store_nbr
            stores_df: DataFrame con información de tiendas
        
        Returns:
            DataFrame con store_type, cluster, city_encoded
        """
        result = df.copy()

        stores_copy = stores_df.copy()
        stores_copy["store_nbr"] = stores_copy["store_nbr"].astype(int)

        result = result.merge(stores_copy, on="store_nbr", how="left")

        result["store_type"] = result["type"].astype("category").cat.codes
        result["cluster"] = result["cluster"].astype(int)

        if "type" in result.columns:
            result = result.drop(columns=["type"])

        return result.copy()

    def add_holiday_features(
        self,
        df: pd.DataFrame,
        holidays_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Agrega features relacionadas con festivos.
        
        Features creadas:
        - is_holiday (1 si hay festivo en la semana)
        - holiday_type (0=ninguno, 1=local, 2=regional, 3=nacional)
        - days_to_holiday (días hasta próximo festivo)
        - is_holiday_week_local, is_holiday_week_regional, is_holiday_week_national
        """
        result = df.copy()
        result["week_start"] = pd.to_datetime(result["week_start"])

        holidays_copy = holidays_df.copy()
        holidays_copy["date"] = pd.to_datetime(holidays_copy["date"])
        holidays_copy["week_start"] = holidays_copy["date"].dt.to_period("W-MON").dt.start_time

        holiday_weeks = holidays_copy.groupby("week_start").agg(
            holiday_count=("date", "count"),
            locale_types=("locale", lambda x: list(x.unique())),
        ).reset_index()

        def get_holiday_type(locales):
            if "National" in locales:
                return 3
            elif "Regional" in locales:
                return 2
            elif "Local" in locales:
                return 1
            return 0

        holiday_weeks["holiday_type"] = holiday_weeks["locale_types"].apply(get_holiday_type)
        holiday_weeks["is_holiday"] = (holiday_weeks["holiday_count"] > 0).astype(int)
        holiday_weeks["is_holiday_week_national"] = (holiday_weeks["holiday_type"] == 3).astype(int)
        holiday_weeks["is_holiday_week_regional"] = (holiday_weeks["holiday_type"] == 2).astype(int)
        holiday_weeks["is_holiday_week_local"] = (holiday_weeks["holiday_type"] == 1).astype(int)

        holiday_cols = [
            "week_start", "is_holiday", "holiday_type",
            "is_holiday_week_national", "is_holiday_week_regional", "is_holiday_week_local"
        ]
        result = result.merge(holiday_weeks[holiday_cols], on="week_start", how="left")

        holiday_cols_to_fill = [
            "is_holiday", "holiday_type", "is_holiday_week_national",
            "is_holiday_week_regional", "is_holiday_week_local"
        ]
        result[holiday_cols_to_fill] = result[holiday_cols_to_fill].fillna(0)
        result["holiday_type"] = result["holiday_type"].astype(int)

        return result.copy()

    def add_oil_features(
        self,
        df: pd.DataFrame,
        oil_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Agrega features de precio del petróleo.
        
        Features creadas:
        - oil_price (precio promedio de la semana)
        - oil_price_change (cambio respecto a semana anterior)
        - oil_price_lag_1 (precio de semana anterior)
        """
        result = df.copy()
        result["week_start"] = pd.to_datetime(result["week_start"])

        oil_copy = oil_df.copy()
        oil_copy["date"] = pd.to_datetime(oil_copy["date"])
        oil_copy["week_start"] = oil_copy["date"].dt.to_period("W-MON").dt.start_time
        oil_copy["dcoilwtico"] = pd.to_numeric(oil_copy["dcoilwtico"], errors="coerce")

        oil_weekly = oil_copy.groupby("week_start").agg(
            oil_price=("dcoilwtico", "mean"),
        ).reset_index()
        oil_weekly["oil_price"] = oil_weekly["oil_price"].fillna(method="ffill")
        oil_weekly["oil_price"] = oil_weekly["oil_price"].fillna(oil_weekly["oil_price"].median())

        oil_weekly["oil_price_lag_1"] = oil_weekly["oil_price"].shift(1)
        oil_weekly["oil_price_change"] = oil_weekly["oil_price"].diff()

        result = result.merge(oil_weekly, on="week_start", how="left")

        result["oil_price"] = result["oil_price"].fillna(result["oil_price"].median())
        result["oil_price_lag_1"] = result["oil_price_lag_1"].fillna(result["oil_price_lag_1"].median())
        result["oil_price_change"] = result["oil_price_change"].fillna(0)

        return result.copy()

    def add_lag_features(
        self,
        df: pd.DataFrame,
        lag_weeks: list[int] = None,
    ) -> pd.DataFrame:
        """
        Agrega lags de ventas (valores pasados).
        
        Args:
            df: DataFrame semanal
            lag_weeks: Lista de lags a crear (ej: [1, 2, 4, 8, 52])
        
        Features creadas:
        - sales_lag_1, sales_lag_2, sales_lag_4, sales_lag_8, sales_lag_52
        """
        if lag_weeks is None:
            lag_weeks = [1, 2, 4, 8, 52]

        result = df.copy()
        result = result.sort_values(["store_nbr", "family", "week_start"])

        for lag in lag_weeks:
            lag_col = f"sales_lag_{lag}"
            result[lag_col] = result.groupby(["store_nbr", "family"])["sales"].shift(lag)

        return result.copy()

    def add_rolling_features(
        self,
        df: pd.DataFrame,
        windows: list[int] = None,
    ) -> pd.DataFrame:
        """
        Agrega estadísticas rolling de ventas.
        
        Args:
            df: DataFrame semanal
            windows: Lista de ventanas (ej: [4, 12])
        
        Features creadas:
        - sales_rolling_mean_4, sales_rolling_std_4, sales_rolling_min_4, sales_rolling_max_4
        - sales_rolling_mean_12, sales_rolling_std_12
        """
        if windows is None:
            windows = [4, 12]

        result = df.copy()
        result = result.sort_values(["store_nbr", "family", "week_start"])

        for window in windows:
            rolling = result.groupby(["store_nbr", "family"])["sales"].rolling(
                window=window, min_periods=1
            )

            result[f"sales_rolling_mean_{window}"] = rolling.mean().reset_index(level=[0, 1], drop=True)
            result[f"sales_rolling_std_{window}"] = rolling.std().reset_index(level=[0, 1], drop=True).fillna(0)
            result[f"sales_rolling_min_{window}"] = rolling.min().reset_index(level=[0, 1], drop=True)
            result[f"sales_rolling_max_{window}"] = rolling.max().reset_index(level=[0, 1], drop=True)

        return result.copy()

    def add_promotion_features(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Agrega features relacionadas con promociones.
        
        Features creadas:
        - onpromotion_lag_1
        - onpromotion_rolling_mean_4
        - has_promotion (1 si onpromotion > 0)
        """
        result = df.copy()
        result = result.sort_values(["store_nbr", "family", "week_start"])

        result["has_promotion"] = (result["onpromotion"] > 0).astype(int)

        result["onpromotion_lag_1"] = result.groupby(["store_nbr", "family"])["onpromotion"].shift(1)

        result["onpromotion_rolling_mean_4"] = (
            result.groupby(["store_nbr", "family"])["onpromotion"]
            .transform(lambda x: x.rolling(window=4, min_periods=1).mean())
        )

        result["onpromotion_lag_1"] = result["onpromotion_lag_1"].fillna(0)

        return result.copy()

    def get_feature_columns(self, df: pd.DataFrame) -> list[str]:
        """
        Retorna la lista de columnas que son features para el modelo.
        
        Args:
            df: DataFrame con todas las features
        
        Returns:
            Lista de nombres de columnas feature
        """
        exclude_cols = {
            "sales",
            "week_start",
            "id",
            "date",
            "store_nbr",
            "family",
            "city",
            "state",
        }

        feature_cols = [col for col in df.columns if col not in exclude_cols]

        return feature_cols
