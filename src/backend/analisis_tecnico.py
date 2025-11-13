"""
Módulo para análisis técnico y señales de compra/venta
"""

import pandas as pd
import numpy as np


def calcular_indicadores_compra_venta(df: pd.DataFrame) -> dict:
    """
    Calcula indicadores técnicos para determinar si es buen momento para comprar o vender
    
    Args:
        df: DataFrame con datos históricos (debe tener 'Close')
    
    Returns:
        Diccionario con señales y recomendaciones
    """
    if 'Close' not in df.columns or len(df) < 50:
        return {
            'señal': 'NEUTRAL',
            'recomendacion': 'Datos insuficientes',
            'confianza': 0,
            'indicadores': {}
        }
    
    # Calcular medias móviles
    ma_20 = df['Close'].rolling(window=20).mean()
    ma_50 = df['Close'].rolling(window=50).mean()
    ma_200 = df['Close'].rolling(window=200).mean()
    
    precio_actual = df['Close'].iloc[-1]
    
    # Calcular RSI (Relative Strength Index)
    if 'Returns' not in df.columns:
        returns = df['Close'].pct_change()
    else:
        returns = df['Returns']
    
    ganancias = returns.where(returns > 0, 0)
    perdidas = -returns.where(returns < 0, 0)
    
    avg_gain = ganancias.rolling(window=14).mean()
    avg_loss = perdidas.rolling(window=14).mean()
    
    rs = avg_gain / (avg_loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))
    rsi_actual = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
    
    # Calcular MACD
    ema_12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema_26 = df['Close'].ewm(span=26, adjust=False).mean()
    macd = ema_12 - ema_26
    signal = macd.ewm(span=9, adjust=False).mean()
    macd_actual = macd.iloc[-1] if not pd.isna(macd.iloc[-1]) else 0
    signal_actual = signal.iloc[-1] if not pd.isna(signal.iloc[-1]) else 0
    
    # Calcular volatilidad
    volatilidad = returns.rolling(window=30).std().iloc[-1] * np.sqrt(252) * 100  # Anualizada
    
    # Señales
    señales = []
    confianza = 0
    
    # Señal 1: Medias móviles
    if len(ma_20) > 0 and len(ma_50) > 0:
        ma_20_actual = ma_20.iloc[-1] if not pd.isna(ma_20.iloc[-1]) else precio_actual
        ma_50_actual = ma_50.iloc[-1] if not pd.isna(ma_50.iloc[-1]) else precio_actual
        
        if precio_actual > ma_20_actual > ma_50_actual:
            señales.append('COMPRA (Tendencia alcista)')
            confianza += 25
        elif precio_actual < ma_20_actual < ma_50_actual:
            señales.append('VENTA (Tendencia bajista)')
            confianza -= 25
    
    # Señal 2: RSI
    if rsi_actual < 30:
        señales.append('COMPRA (Oversold)')
        confianza += 20
    elif rsi_actual > 70:
        señales.append('VENTA (Overbought)')
        confianza -= 20
    elif 30 <= rsi_actual <= 70:
        señales.append('NEUTRAL (RSI normal)')
    
    # Señal 3: MACD
    if macd_actual > signal_actual and macd.iloc[-2] <= signal.iloc[-2]:
        señales.append('COMPRA (Cruce MACD alcista)')
        confianza += 15
    elif macd_actual < signal_actual and macd.iloc[-2] >= signal.iloc[-2]:
        señales.append('VENTA (Cruce MACD bajista)')
        confianza -= 15
    
    # Determinar señal final
    if confianza >= 30:
        señal_final = 'COMPRA'
        recomendacion = 'Indicadores sugieren que puede ser un buen momento para comprar'
    elif confianza <= -30:
        señal_final = 'VENTA'
        recomendacion = 'Indicadores sugieren que puede ser un buen momento para vender'
    else:
        señal_final = 'NEUTRAL'
        recomendacion = 'Indicadores muestran señales mixtas, considera esperar'
    
    return {
        'señal': señal_final,
        'recomendacion': recomendacion,
        'confianza': abs(confianza),
        'rsi': round(rsi_actual, 2),
        'macd': round(macd_actual, 2),
        'volatilidad': round(volatilidad, 2) if not pd.isna(volatilidad) else 0,
        'precio_actual': round(precio_actual, 2),
        'ma_20': round(ma_20.iloc[-1], 2) if len(ma_20) > 0 and not pd.isna(ma_20.iloc[-1]) else None,
        'ma_50': round(ma_50.iloc[-1], 2) if len(ma_50) > 0 and not pd.isna(ma_50.iloc[-1]) else None,
        'señales_detalle': señales
    }

