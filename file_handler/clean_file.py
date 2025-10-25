import polars as pl
from utils.mapeo import dict_area, dict_carreras, dict_facultades, mapping


class DataFrameCleaner:

    @staticmethod
    def _renombrar_columnas(df: pl.DataFrame) -> pl.DataFrame:
        return df.rename({
            'dni': 'DNI',
            'apellidos_nombres': 'APELLIDOS Y NOMBRES',
            'puntaje': 'PUNTAJE',
            'condicion': 'CONDICION',
            'anio': 'AÑO',
            'periodo': 'PERIODO',
            'modalidad_ingreso': 'MODALIDAD',
            'carrera': 'CARRERA'
        })

    @staticmethod
    def _convertir_tipos_basicos(df: pl.DataFrame) -> pl.DataFrame:
        return df.with_columns([
            pl.col("DNI").cast(pl.Utf8).str.strip_chars(),
            pl.col('APELLIDOS Y NOMBRES').str.to_uppercase().str.strip_chars(),
            pl.when(pl.col('MODALIDAD').is_null() | (pl.col('MODALIDAD') == ""))
                .then(pl.lit('ORDINARIA'))
                .otherwise(pl.col('MODALIDAD'))
                .alias('MODALIDAD'),
            pl.when(pl.col('PERIODO').is_null() | (pl.col('PERIODO') == ""))
                .then(pl.lit('I'))
                .otherwise(pl.col('PERIODO'))
                .alias('PERIODO')
        ])
    
    @staticmethod
    def _normalizar_modalidad(df: pl.DataFrame) -> pl.DataFrame:
        def normalizar_modalidad(x):
            return mapping.get(x, x)

        return (
            df.with_columns(
                pl.col("MODALIDAD")
                .str.replace(r"^\d+\s+", "")
                .alias("MODALIDAD")
            )
            .with_columns(
                pl.col("MODALIDAD")
                .map_elements(normalizar_modalidad, return_dtype=pl.Utf8)
                .alias("MODALIDAD")
            )
        )

    @staticmethod
    def _limpiar_carrera(df: pl.DataFrame) -> pl.DataFrame:
        return df.with_columns(
            pl.col('CARRERA').str.replace(r"^.*?:\s*", "").str.strip_chars()
        )

    @staticmethod
    def _normalizar_carrera(df: pl.DataFrame) -> pl.DataFrame:
        def normalizar_carrera(x):
            if not x or x == '':
                return x
            return dict_carreras.get(x, x)

        return df.with_columns(
            pl.col('CARRERA')
            .map_elements(normalizar_carrera, return_dtype=pl.Utf8)
            .alias('CARRERA')
        )

    @staticmethod
    def _agregar_facultad_y_area(df: pl.DataFrame) -> pl.DataFrame:
        def agregar_facultad(x):
            if not x or x == '':
                return ''
            return dict_facultades.get(x, '')

        def agregar_area(x):
            if not x or x == '':
                return ''
            return dict_area.get(x, '')

        return df.with_columns([
            pl.col('CARRERA')
            .map_elements(agregar_facultad, return_dtype=pl.Utf8)
            .alias('FACULTAD'),
            pl.col('CARRERA')
            .map_elements(agregar_area, return_dtype=pl.Utf8)
            .alias('AREA'),
        ])

    @staticmethod
    def _ordenar_resultado(df: pl.DataFrame) -> pl.DataFrame:
        if 'orden_original' in df.columns:
            return df.sort('orden_original')
        return df

    @staticmethod
    def main_cleaner(df: pl.DataFrame) -> pl.DataFrame:
        return (
            df
            .pipe(DataFrameCleaner._renombrar_columnas)
            .pipe(DataFrameCleaner._convertir_tipos_basicos)
            .pipe(DataFrameCleaner._normalizar_modalidad)
            .pipe(DataFrameCleaner._limpiar_carrera)
            .pipe(DataFrameCleaner._normalizar_carrera)
            .pipe(DataFrameCleaner._agregar_facultad_y_area)
            .pipe(DataFrameCleaner._ordenar_resultado)
        )

    @staticmethod
    def clean_dataframe(df: pl.DataFrame) -> pl.DataFrame:
        # Metodo Legacy
        return DataFrameCleaner.main_cleaner(df)
