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

# Prophet para pronósticos de series temporales
def _check_prophet_available():
    """Verifica dinámicamente si Prophet está disponible"""
    try:
        import prophet
        return True
    except ImportError:
        return False
    except Exception:
        # Si hay otro error, asumimos que está instalado
        return True

# Variable global que se verifica dinámicamente
PROPHET_AVAILABLE = _check_prophet_available()


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


def entrenar_prophet(df: pd.DataFrame, periodos_futuros: int = 30) -> dict:
    """
    Entrena un modelo Prophet para predecir precios futuros
    Usa escala logarítmica para datos financieros (mejor para crecimiento exponencial)
    
    Args:
        df: DataFrame con datos históricos (debe tener índice datetime y columna 'Close')
        periodos_futuros: Número de días a predecir hacia el futuro
    
    Returns:
        Diccionario con el modelo, predicciones y métricas
    """
    # Importar Prophet aquí para asegurar que esté disponible
    try:
        from prophet import Prophet
    except ImportError as e:
        raise ImportError(f"Prophet no está instalado. Instala con: pip install prophet. Error: {str(e)}")
    
    # IMPORTANTE: Guardar la fecha máxima histórica ANTES de cualquier procesamiento
    # Esta es la fecha real del último dato disponible (ej: 20 de noviembre 2025)
    fecha_max_historica_original = df.index.max()
    
    # Guardar el precio REAL del último día disponible ANTES de cualquier procesamiento
    precio_actual_real = df['Close'].iloc[-1]
    
    # Asegurar que la fecha sea timezone-naive
    if isinstance(fecha_max_historica_original, pd.Timestamp):
        if fecha_max_historica_original.tz is not None:
            fecha_max_historica_original = fecha_max_historica_original.tz_localize(None)
    
    # Preparar datos para Prophet (requiere columnas 'ds' y 'y')
    # Asegurar que no haya valores negativos o cero
    precios = df['Close'].values.copy()
    if (precios <= 0).any():
        raise ValueError("Los precios no pueden ser negativos o cero para Prophet")
    
    # Usar escala logarítmica para datos financieros (mejor para crecimiento exponencial)
    # Esto es más apropiado para índices bursátiles que tienden a crecer exponencialmente
    precios_log = np.log(precios)
    
    # Asegurar que el índice sea timezone-naive antes de crear df_prophet
    df_index_clean = df.index.copy()
    if df_index_clean.tz is not None:
        df_index_clean = df_index_clean.tz_localize(None)
    
    df_prophet = pd.DataFrame({
        'ds': df_index_clean,
        'y': precios_log  # Usar logaritmo de precios
    })
    
    # Eliminar valores NaN si los hay
    df_prophet = df_prophet.dropna()
    
    if len(df_prophet) < 90:
        raise ValueError("Se necesitan al menos 90 días de datos históricos para Prophet")
    
    # Usar más datos históricos para mejor captura de patrones y estacionalidades
    # 5 años permite capturar ciclos económicos completos y estacionalidades anuales
    # PERO la predicción debe empezar desde fecha_max_historica_original (hoy)
    max_datos_historicos = 1825  # ~5 años (mejor que 3 años para patrones a largo plazo)
    df_prophet_entrenamiento = df_prophet.copy()
    if len(df_prophet_entrenamiento) > max_datos_historicos:
        df_prophet_entrenamiento = df_prophet_entrenamiento.tail(max_datos_historicos).reset_index(drop=False)
        if 'index' in df_prophet_entrenamiento.columns:
            df_prophet_entrenamiento = df_prophet_entrenamiento.drop(columns=['index'])
    
    # DIVISIÓN TRAIN/TEST: Usar los últimos 180 días (6 meses) como test para evaluación más robusta
    # Esto permite evaluar mejor el rendimiento del modelo en diferentes condiciones de mercado
    dias_test = 180  # 6 meses (más robusto que 90 días)
    split_idx = len(df_prophet_entrenamiento) - dias_test
    
    if split_idx < 90:
        # Si no hay suficientes datos para train después del split, usar 80/20 split
        # Pero asegurar al menos 90 días de test si es posible
        split_idx = max(int(len(df_prophet_entrenamiento) * 0.8), len(df_prophet_entrenamiento) - 180)
        dias_test = len(df_prophet_entrenamiento) - split_idx
    
    df_train = df_prophet_entrenamiento.iloc[:split_idx].copy()
    df_test = df_prophet_entrenamiento.iloc[split_idx:].copy()
    
    # Crear y entrenar modelo Prophet optimizado para datos financieros
    modelo = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,  # Desactivado (menos relevante para índices)
        daily_seasonality=False,
        seasonality_mode='additive',
        changepoint_prior_scale=0.1,  # Un poco más flexible que antes
        changepoint_range=0.95,  # Permitir cambios en el 95% de los datos
        interval_width=0.80,
        growth='linear',  # Crecimiento lineal en escala logarítmica = exponencial en escala normal
        n_changepoints=20  # Más changepoints para capturar mejor las tendencias
    )
    
    # Entrenar SOLO con datos de entrenamiento
    modelo.fit(df_train)
    
    # IMPORTANTE: La predicción debe empezar desde fecha_max_historica_original (hoy)
    # Calcular cuántos días hay desde el último dato de entrenamiento hasta hoy
    ultima_fecha_train = df_train['ds'].max()
    if isinstance(ultima_fecha_train, pd.Timestamp) and ultima_fecha_train.tz is not None:
        ultima_fecha_train = ultima_fecha_train.tz_localize(None)
    
    dias_desde_train_hasta_hoy = (fecha_max_historica_original - ultima_fecha_train).days
    
    # Asegurar que no sea negativo (por si hay algún problema con las fechas)
    if dias_desde_train_hasta_hoy < 0:
        dias_desde_train_hasta_hoy = 0
    
    periodos_minimos = max(30, periodos_futuros)
    
    # Crear fechas futuras: incluir desde el último dato de entrenamiento hasta hoy + periodos futuros
    # Esto asegura que la predicción incluya hasta hoy y luego los periodos futuros
    dias_totales = dias_desde_train_hasta_hoy + periodos_minimos
    futuro = modelo.make_future_dataframe(periods=dias_totales)
    
    # Hacer predicción (en escala logarítmica)
    prediccion_log = modelo.predict(futuro)
    
    # Convertir de vuelta a escala normal (exponencial de la predicción logarítmica)
    prediccion = prediccion_log.copy()
    prediccion['yhat'] = np.exp(prediccion_log['yhat'])
    prediccion['yhat_lower'] = np.exp(prediccion_log['yhat_lower'])
    prediccion['yhat_upper'] = np.exp(prediccion_log['yhat_upper'])
    
    # Asegurar que las predicciones no sean negativas
    prediccion['yhat'] = prediccion['yhat'].clip(lower=0.01)
    
    # Calcular métricas en el conjunto de TEST (datos que el modelo no vio durante entrenamiento)
    fecha_max_train = df_train['ds'].max()
    fecha_max_test = df_test['ds'].max()
    
    # Predicciones en el período de test
    prediccion_test = prediccion[
        (prediccion['ds'] > fecha_max_train) & 
        (prediccion['ds'] <= fecha_max_test)
    ].copy()
    
    if len(prediccion_test) > 0:
        prediccion_test.set_index('ds', inplace=True)
        
        # Alinear índices para comparar con datos reales de test
        indices_test = prediccion_test.index.intersection(df_test['ds'].values)
        if len(indices_test) > 0:
            # Convertir índices de test a datetime si es necesario
            df_test_indexed = df_test.set_index('ds')
            df_test_aligned = df_test_indexed.loc[indices_test, 'y']
            pred_test_aligned = prediccion_test.loc[indices_test, 'yhat']
            
            # Convertir de vuelta a escala normal (df_test tiene valores en log)
            df_test_aligned_normal = np.exp(df_test_aligned)
            
            # Calcular métricas en escala normal
            rmse = np.sqrt(mean_squared_error(df_test_aligned_normal, pred_test_aligned))
            mae = mean_absolute_error(df_test_aligned_normal, pred_test_aligned)
        else:
            rmse = None
            mae = None
    else:
        rmse = None
        mae = None
    
    # Obtener predicción futura (después del último dato disponible)
    fecha_max_historica = fecha_max_historica_original
    
    # Convertir las fechas de predicción a timezone-naive si es necesario
    prediccion['ds'] = pd.to_datetime(prediccion['ds'])
    if prediccion['ds'].dt.tz is not None:
        prediccion['ds'] = prediccion['ds'].dt.tz_localize(None)
    
    # Filtrar predicción futura: SOLO fechas DESPUÉS de la fecha histórica máxima (hoy)
    # El día de hoy está en los datos históricos, la predicción empieza desde mañana
    prediccion_futura = prediccion[prediccion['ds'] > fecha_max_historica].copy()
    
    # Asegurar que tengamos al menos los periodos mínimos solicitados de predicción futura
    if len(prediccion_futura) < periodos_minimos:
        # Si no hay suficientes días, extender la predicción
        ultima_fecha = prediccion_futura['ds'].max() if len(prediccion_futura) > 0 else fecha_max_historica
        # Convertir a Timestamp si es necesario y asegurar que sea timezone-naive
        if isinstance(ultima_fecha, pd.Timestamp):
            if ultima_fecha.tz is not None:
                ultima_fecha = ultima_fecha.tz_localize(None)
        else:
            ultima_fecha = pd.to_datetime(ultima_fecha)
            if ultima_fecha.tz is not None:
                ultima_fecha = ultima_fecha.tz_localize(None)
        
        # Usar pd.Timedelta con frecuencia explícita para evitar el error
        fecha_inicio_adicional = ultima_fecha + pd.Timedelta('1D')
        fechas_adicionales = pd.date_range(
            start=fecha_inicio_adicional,
            periods=periodos_minimos - len(prediccion_futura),
            freq='D'
        )
        # Extender con el último valor predicho (extrapolación simple)
        if len(prediccion_futura) > 0:
            ultimo_valor = prediccion_futura['yhat'].iloc[-1]
            ultimo_lower = prediccion_futura['yhat_lower'].iloc[-1]
            ultimo_upper = prediccion_futura['yhat_upper'].iloc[-1]
            
            extension = pd.DataFrame({
                'ds': fechas_adicionales,
                'yhat': [ultimo_valor] * len(fechas_adicionales),
                'yhat_lower': [ultimo_lower] * len(fechas_adicionales),
                'yhat_upper': [ultimo_upper] * len(fechas_adicionales)
            })
            prediccion_futura = pd.concat([prediccion_futura, extension], ignore_index=True)
    
    # Obtener precio predicho (30 días o el periodo mínimo)
    precio_predicho_30d = None
    retorno_predicho_30d = None
    
    # Usar el precio real guardado al inicio (del DataFrame completo, no truncado)
    precio_actual = precio_actual_real
    
    if len(prediccion_futura) >= 30:
        # Usar el día 30 de la predicción
        precio_predicho_30d = max(0.01, prediccion_futura['yhat'].iloc[29])
        if precio_actual > 0:
            retorno_predicho_30d = ((precio_predicho_30d / precio_actual) - 1)
    elif len(prediccion_futura) > 0:
        # Si hay menos de 30 días, usar el último disponible
        precio_predicho_30d = max(0.01, prediccion_futura['yhat'].iloc[-1])
        if precio_actual > 0:
            retorno_predicho_30d = ((precio_predicho_30d / precio_actual) - 1)
    
    return {
        'modelo': modelo,
        'prediccion_completa': prediccion,
        'prediccion_futura': prediccion_futura,
        'fecha_max_historica': fecha_max_historica,  # Guardar la fecha máxima histórica
        'precio_predicho_30d': precio_predicho_30d,
        'precio_actual': precio_actual,  # Usar el precio real guardado al inicio
        'retorno_predicho_30d': retorno_predicho_30d,
        'metricas': {
            'RMSE': rmse,
            'MAE': mae
        }
    }


def entrenar_ridge_y_prophet(df: pd.DataFrame, nombre_indice: str, periodos_futuros: int = 30) -> dict:
    """
    Entrena tanto Ridge como Prophet y devuelve ambos resultados
    
    Args:
        df: DataFrame con datos históricos del índice
        nombre_indice: Nombre del índice
        periodos_futuros: Número de días a predecir hacia el futuro (por defecto 30)
    
    Returns:
        Diccionario con resultados de ambos modelos
    """
    resultados = {}
    
    # Modelo Ridge (para retornos)
    try:
        resultado_ridge = entrenar_y_predecir_indice(df, nombre_indice)
        resultados['ridge'] = resultado_ridge
    except Exception as e:
        resultados['ridge'] = {'error': str(e)}
    
    # Modelo Prophet (para precios)
    try:
        # Intentar usar Prophet - la función entrenar_prophet maneja el import internamente
        resultado_prophet = entrenar_prophet(df, periodos_futuros=periodos_futuros)
        resultados['prophet'] = resultado_prophet
    except ImportError as ie:
        resultados['prophet'] = {'error': f'Prophet no está instalado. Instala con: pip install prophet. Error: {str(ie)}'}
    except Exception as e:
        # Capturar cualquier otro error y mostrarlo
        resultados['prophet'] = {'error': f'Error con Prophet: {str(e)}'}
    
    return resultados
