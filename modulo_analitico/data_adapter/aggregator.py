"""
DEMAND-24 — Agregación de Datos

Responsable de transformar datos diarios a semanales.
Alineación a lunes como inicio de semana (ISO-8601).

Cumple con:
- Regla I: Inmutabilidad (todos los DataFrames se retornan como copias)
- Regla VI: Integridad de Datos Temporales (agregación correcta)
"""

from typing import Optional
import pandas as pd

from ..config.ml_config import MLConfig


class DataAggregator:
    """
    Agrega datos diarios a nivel semanal.
    
    Responsabilidades:
    - Transformar daily → weekly (suma ventas, promedio promociones)
    - Alinear a lunes como inicio de semana (W-SUN)
    - Manejar semanas parciales correctamente
    """

    def __init__(self, config: Optional[MLConfig] = None):
        self.config = config or MLConfig()

    def aggregate_daily_to_weekly(
        self,
        df: pd.DataFrame,
        group_by_family: bool = True,
    ) -> pd.DataFrame:
        """
        Agrega datos diarios a nivel semanal.
        
        Args:
            df: DataFrame diario con columnas: date, store_nbr, family, sales, onpromotion
            group_by_family: Si True, agrega por (store_nbr, family, week).
                            Si False, agrega solo por (store_nbr, week).
        
        Returns:
            DataFrame semanal con columnas:
            - week_start (lunes)
            - store_nbr
            - family (si group_by_family=True)
            - sales (suma semanal)
            - onpromotion (promedio semanal)
            - n_days (días con datos en la semana)
        """
        df_copy = df.copy()

        df_copy["week_start"] = df_copy["date"].dt.to_period("W-SUN").dt.start_time

        group_cols = ["store_nbr", "week_start"]
        if group_by_family:
            group_cols.insert(1, "family")

        weekly_df = df_copy.groupby(group_cols).agg(
            sales=("sales", "sum"),
            onpromotion=("onpromotion", "mean"),
            n_days=("date", "count"),
        ).reset_index()

        weekly_df["onpromotion"] = weekly_df["onpromotion"].round(2)

        return weekly_df.copy()

    def calculate_weekly_stats(
        self,
        df: pd.DataFrame,
        group_by_family: bool = True,
    ) -> pd.DataFrame:
        """
        Calcula estadísticas semanales adicionales.
        
        Args:
            df: DataFrame diario
            group_by_family: Si True, calcula stats por (store_nbr, family)
        
        Returns:
            DataFrame con estadísticas semanales:
            - sales_mean, sales_std, sales_min, sales_max
            - onpromotion_sum (días con promoción)
        """
        df_copy = df.copy()

        df_copy["week_start"] = df_copy["date"].dt.to_period("W-SUN").dt.start_time

        group_cols = ["store_nbr", "week_start"]
        if group_by_family:
            group_cols.insert(1, "family")

        stats_df = df_copy.groupby(group_cols)["sales"].agg(
            ["mean", "std", "min", "max", "count"]
        ).reset_index()

        stats_df.columns = group_cols + ["sales_mean", "sales_std", "sales_min", "sales_max", "n_days"]
        stats_df["sales_std"] = stats_df["sales_std"].fillna(0)

        promo_df = df_copy.groupby(group_cols)["onpromotion"].agg(
            ["sum", "mean"]
        ).reset_index()
        promo_df.columns = group_cols + ["onpromotion_days", "onpromotion_mean"]

        result = stats_df.merge(promo_df, on=group_cols, how="left")

        return result.copy()

    def get_week_boundaries(
        self,
        df: pd.DataFrame,
    ) -> tuple[pd.Timestamp, pd.Timestamp]:
        """
        Obtiene los límites de semanas en el dataset.
        
        Args:
            df: DataFrame con columna date
        
        Returns:
            Tuple con (primera_fecha_lunes, ultima_fecha_lunes)
        """
        df_copy = df.copy()
        df_copy["week_start"] = df_copy["date"].dt.to_period("W-SUN").dt.start_time

        first_week = df_copy["week_start"].min()
        last_week = df_copy["week_start"].max()

        return first_week, last_week

    def create_complete_week_index(
        self,
        df: pd.DataFrame,
        group_by_family: bool = True,
    ) -> pd.DataFrame:
        """
        Crea un índice completo de semanas para detectar huecos.
        
        Args:
            df: DataFrame semanal
            group_by_family: Si True, crea índice por (store_nbr, family)
        
        Returns:
            DataFrame con todas las combinaciones posibles de (store_nbr, family, week)
        """
        df_copy = df.copy()

        df_copy["week_start"] = pd.to_datetime(df_copy["week_start"])

        all_stores = df_copy["store_nbr"].unique()
        all_weeks = pd.date_range(
            start=df_copy["week_start"].min(),
            end=df_copy["week_start"].max(),
            freq="W-MON",
        )

        if group_by_family:
            all_families = df_copy["family"].unique()

            index_df = pd.MultiIndex.from_product(
                [all_stores, all_families, all_weeks],
                names=["store_nbr", "family", "week_start"],
            ).to_frame(index=False)
        else:
            index_df = pd.MultiIndex.from_product(
                [all_stores, all_weeks],
                names=["store_nbr", "week_start"],
            ).to_frame(index=False)

        return index_df.copy()

    def fill_missing_weeks(
        self,
        df: pd.DataFrame,
        complete_index: pd.DataFrame,
        fill_value: float = 0.0,
    ) -> pd.DataFrame:
        """
        Rellena semanas faltantes con un valor (ej: 0 para ventas).
        
        Args:
            df: DataFrame semanal incompleto
            complete_index: Índice completo generado por create_complete_week_index
            fill_value: Valor para rellenar semanas sin datos
        
        Returns:
            DataFrame completo con todas las semanas
        """
        df_copy = df.copy()
        df_copy["week_start"] = pd.to_datetime(df_copy["week_start"])

        merge_cols = ["store_nbr", "week_start"]
        if "family" in df_copy.columns and "family" in complete_index.columns:
            merge_cols.insert(1, "family")

        complete_df = complete_index.merge(df_copy, on=merge_cols, how="left")

        numeric_cols = complete_df.select_dtypes(include=["float64", "int64"]).columns
        complete_df[numeric_cols] = complete_df[numeric_cols].fillna(fill_value)

        return complete_df.copy()
