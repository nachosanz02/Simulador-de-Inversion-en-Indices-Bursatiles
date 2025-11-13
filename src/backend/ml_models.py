"""
Módulo para modelos de Machine Learning para predecir retornos de índices bursátiles
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')


def construir_variables_explicativas(df: pd.DataFrame, ventana_retornos: int = 5, 
                                    ventana_volatilidad: int = 30) -> pd.DataFrame:
    """
    Construye variables explicativas para el modelo de ML
    
    Args:
        df: DataFrame con datos históricos (debe tener 'Close' y 'Returns')
        ventana_retornos: Ventana para calcular retornos pasados
        ventana_volatilidad: Ventana para calcular volatilidad
    
    Returns:
        DataFrame con las variables explicativas
    """
    df_features = df.copy()
    
    if 'Returns' not in df_features.columns:
        df_features['Returns'] = df_features['Close'].pct_change()
    
    # Retornos pasados (lag features)
    for lag in range(1, ventana_retornos + 1):
        df_features[f'Return_lag_{lag}'] = df_features['Returns'].shift(lag)
    
    # Media móvil de retornos
    for ventana in [5, 10, 20]:
        df_features[f'MA_Return_{ventana}d'] = df_features['Returns'].rolling(window=ventana).mean()
    
    # Volatilidad (desviación estándar de retornos)
    df_features['Volatility'] = df_features['Returns'].rolling(window=ventana_volatilidad).std()
    
    # Media móvil del precio
    for ventana in [10, 20, 50]:
        df_features[f'MA_Price_{ventana}d'] = df_features['Close'].rolling(window=ventana).mean()
        # Ratio precio/MA
        df_features[f'Price_MA_Ratio_{ventana}d'] = df_features['Close'] / df_features[f'MA_Price_{ventana}d']
    
    # RSI simplificado (basado en retornos)
    ganancias = df_features['Returns'].where(df_features['Returns'] > 0, 0)
    perdidas = -df_features['Returns'].where(df_features['Returns'] < 0, 0)
    ganancia_promedio = ganancias.rolling(window=14).mean()
    perdida_promedio = perdidas.rolling(window=14).mean()
    rs = ganancia_promedio / (perdida_promedio + 1e-10)
    df_features['RSI'] = 100 - (100 / (1 + rs))
    
    return df_features


def preparar_datos_entrenamiento(df_features: pd.DataFrame) -> tuple:
    """
    Prepara los datos para entrenamiento del modelo
    
    Args:
        df_features: DataFrame con variables explicativas
    
    Returns:
        Tupla (X, y) donde X son las features y y es el target (retorno del siguiente mes)
    """
    # Target: retorno del siguiente mes (aproximadamente 20 días hábiles)
    df_features['Target'] = df_features['Returns'].shift(-20)
    
    # Seleccionar columnas de features (excluir Close, Returns, Target y otras no numéricas)
    columnas_excluir = ['Open', 'High', 'Low', 'Volume', 'Close', 'Returns', 'Target', 
                        'Cumulative_Returns', 'Volatility_30d']
    columnas_features = [col for col in df_features.columns 
                         if col not in columnas_excluir and df_features[col].dtype in ['float64', 'int64']]
    
    X = df_features[columnas_features].copy()
    y = df_features['Target'].copy()
    
    # Eliminar filas con NaN
    mask = ~(X.isna().any(axis=1) | y.isna())
    X = X[mask]
    y = y[mask]
    
    return X, y


def entrenar_modelo_ridge(X: pd.DataFrame, y: pd.Series, alpha: float = 1.0) -> tuple:
    """
    Entrena un modelo Ridge para predecir retornos
    
    Args:
        X: Features
        y: Target (retornos futuros)
        alpha: Parámetro de regularización Ridge
    
    Returns:
        Tupla (modelo, métricas) donde métricas es un diccionario con RMSE y MAE
    """
    # Usar TimeSeriesSplit para validación temporal
    tscv = TimeSeriesSplit(n_splits=5)
    
    modelos = []
    metricas_cv = {'RMSE': [], 'MAE': []}
    
    for train_idx, val_idx in tscv.split(X):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
        
        modelo = Ridge(alpha=alpha)
        modelo.fit(X_train, y_train)
        
        y_pred = modelo.predict(X_val)
        
        rmse = np.sqrt(mean_squared_error(y_val, y_pred))
        mae = mean_absolute_error(y_val, y_pred)
        
        metricas_cv['RMSE'].append(rmse)
        metricas_cv['MAE'].append(mae)
        modelos.append(modelo)
    
    # Entrenar modelo final con todos los datos
    modelo_final = Ridge(alpha=alpha)
    modelo_final.fit(X, y)
    
    # Calcular métricas promedio
    metricas = {
        'RMSE': np.mean(metricas_cv['RMSE']),
        'MAE': np.mean(metricas_cv['MAE']),
        'RMSE_std': np.std(metricas_cv['RMSE']),
        'MAE_std': np.std(metricas_cv['MAE'])
    }
    
    return modelo_final, metricas


def predecir_retorno_futuro(modelo, df_features: pd.DataFrame) -> float:
    """
    Predice el retorno del siguiente mes usando el modelo entrenado
    
    Args:
        modelo: Modelo Ridge entrenado
        df_features: DataFrame con variables explicativas (debe tener la última fila completa)
    
    Returns:
        Retorno predicho (como decimal, ej: 0.05 = 5%)
    """
    # Obtener la última fila con todas las features
    columnas_excluir = ['Open', 'High', 'Low', 'Volume', 'Close', 'Returns', 'Target',
                        'Cumulative_Returns', 'Volatility_30d']
    columnas_features = [col for col in df_features.columns 
                         if col not in columnas_excluir and df_features[col].dtype in ['float64', 'int64']]
    
    X_ultimo = df_features[columnas_features].iloc[[-1]]
    
    # Verificar que no haya NaN
    if X_ultimo.isna().any().any():
        raise ValueError("La última fila tiene valores NaN. Se necesitan datos más recientes.")
    
    retorno_predicho = modelo.predict(X_ultimo)[0]
    
    return retorno_predicho


def entrenar_y_predecir_indice(df: pd.DataFrame, nombre_indice: str) -> dict:
    """
    Función completa: construye features, entrena modelo y predice retorno futuro
    
    Args:
        df: DataFrame con datos históricos del índice
        nombre_indice: Nombre del índice
    
    Returns:
        Diccionario con el modelo, métricas y predicción
    """
    print(f"\nEntrenando modelo para {nombre_indice}...")
    
    # Construir variables explicativas
    df_features = construir_variables_explicativas(df)
    
    # Preparar datos
    X, y = preparar_datos_entrenamiento(df_features)
    
    if len(X) == 0:
        raise ValueError("No hay suficientes datos para entrenar el modelo")
    
    print(f"  Datos de entrenamiento: {len(X)} registros")
    print(f"  Features: {len(X.columns)} variables")
    
    # Entrenar modelo
    modelo, metricas = entrenar_modelo_ridge(X, y)
    
    print(f"  RMSE: {metricas['RMSE']:.4f} (±{metricas['RMSE_std']:.4f})")
    print(f"  MAE: {metricas['MAE']:.4f} (±{metricas['MAE_std']:.4f})")
    
    # Predecir retorno futuro
    try:
        retorno_predicho = predecir_retorno_futuro(modelo, df_features)
        print(f"  Retorno predicho (próximo mes): {retorno_predicho*100:.2f}%")
    except Exception as e:
        print(f"  ⚠ No se pudo predecir: {str(e)}")
        retorno_predicho = None
    
    return {
        'modelo': modelo,
        'metricas': metricas,
        'retorno_predicho': retorno_predicho,
        'features': X.columns.tolist()
    }

