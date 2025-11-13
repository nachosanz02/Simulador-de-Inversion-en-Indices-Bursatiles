"""
Módulo para el preprocesamiento y limpieza de datos de índices bursátiles
"""

import pandas as pd
import numpy as np
import os


def limpiar_datos(df: pd.DataFrame, nombre_indice: str = "") -> pd.DataFrame:
    """
    Limpia y preprocesa los datos de un índice bursátil
    
    Args:
        df: DataFrame con los datos históricos del índice
        nombre_indice: Nombre del índice (para mensajes informativos)
    
    Returns:
        DataFrame limpio y preprocesado
    """
    df_limpio = df.copy()
    
    print(f"Preprocesando datos de {nombre_indice}...")
    print(f"  Registros originales: {len(df_limpio)}")
    
    # Eliminar filas con valores nulos en columnas críticas
    columnas_criticas = ['Close', 'Open', 'High', 'Low', 'Volume']
    columnas_existentes = [col for col in columnas_criticas if col in df_limpio.columns]
    
    if columnas_existentes:
        df_limpio = df_limpio.dropna(subset=columnas_existentes)
        print(f"  Registros después de eliminar nulos: {len(df_limpio)}")
    
    # Asegurar que el índice es datetime
    if not isinstance(df_limpio.index, pd.DatetimeIndex):
        df_limpio.index = pd.to_datetime(df_limpio.index)
    
    # Asegurar que el índice sea tz-naive (sin timezone)
    if df_limpio.index.tz is not None:
        df_limpio.index = df_limpio.index.tz_localize(None)
    
    # Ordenar por fecha
    df_limpio = df_limpio.sort_index()
    
    # Calcular retornos diarios
    if 'Close' in df_limpio.columns:
        df_limpio['Returns'] = df_limpio['Close'].pct_change()
        df_limpio['Returns'] = df_limpio['Returns'].fillna(0)
    
    # Calcular retornos acumulados
    if 'Returns' in df_limpio.columns:
        df_limpio['Cumulative_Returns'] = (1 + df_limpio['Returns']).cumprod() - 1
    
    # Calcular volatilidad (desviación estándar de retornos en ventana móvil de 30 días)
    if 'Returns' in df_limpio.columns:
        df_limpio['Volatility_30d'] = df_limpio['Returns'].rolling(window=30).std()
    
    print(f"  Registros finales: {len(df_limpio)}")
    print(f"  Rango de fechas: {df_limpio.index.min()} a {df_limpio.index.max()}")
    
    return df_limpio


def preprocesar_todos_indices(datos_indices: dict, guardar: bool = True) -> dict:
    """
    Preprocesa los datos de todos los índices
    
    Args:
        datos_indices: Diccionario con nombres de índices y sus DataFrames
        guardar: Si es True, guarda los datos procesados en data/processed/
    
    Returns:
        Diccionario con los datos preprocesados
    """
    datos_procesados = {}
    
    print("\nPreprocesando datos de todos los índices...")
    
    for nombre_indice, df in datos_indices.items():
        try:
            df_limpio = limpiar_datos(df, nombre_indice)
            datos_procesados[nombre_indice] = df_limpio
            
            # Guardar en CSV si se solicita
            if guardar:
                ruta_processed = os.path.join('data', 'processed')
                os.makedirs(ruta_processed, exist_ok=True)
                nombre_archivo = f"{nombre_indice.replace(' ', '_').replace('&', '')}_processed.csv"
                ruta_completa = os.path.join(ruta_processed, nombre_archivo)
                df_limpio.to_csv(ruta_completa)
                print(f"  Guardado en: {ruta_completa}")
                
        except Exception as e:
            print(f"✗ Error preprocesando {nombre_indice}: {str(e)}")
    
    print(f"\nTotal de índices preprocesados: {len(datos_procesados)}/{len(datos_indices)}")
    return datos_procesados


def cargar_datos_procesados(nombre_indice: str) -> pd.DataFrame:
    """
    Carga datos procesados de un índice desde un archivo CSV en data/processed/
    
    Args:
        nombre_indice: Nombre del índice (ej: 'S&P 500')
    
    Returns:
        DataFrame con los datos procesados
    """
    nombre_archivo = f"{nombre_indice.replace(' ', '_').replace('&', '')}_processed.csv"
    ruta = os.path.join('data', 'processed', nombre_archivo)
    
    if os.path.exists(ruta):
        datos = pd.read_csv(ruta, index_col=0, parse_dates=True)
        return datos
    else:
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")

