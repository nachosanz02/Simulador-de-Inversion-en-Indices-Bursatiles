"""
Módulo para la simulación de inversiones en índices bursátiles
"""

import pandas as pd
import os


def calcular_valor_inversion(df: pd.DataFrame, fecha_inversion: str, 
                             cantidad: float, nombre_indice: str = "") -> dict:
    """
    Calcula el valor actual de una inversión realizada en una fecha específica
    
    Args:
        df: DataFrame con datos históricos del índice (debe tener columna 'Close')
        fecha_inversion: Fecha de inversión en formato 'YYYY-MM-DD'
        cantidad: Cantidad de dinero invertida
        nombre_indice: Nombre del índice (para mensajes informativos)
    
    Returns:
        Diccionario con información de la inversión:
        - valor_actual: Valor actual de la inversión
        - ganancia_perdida: Ganancia o pérdida absoluta
        - retorno_porcentual: Retorno porcentual
        - precio_compra: Precio del índice en la fecha de inversión
        - precio_actual: Precio actual del índice
        - fecha_inversion: Fecha de inversión
        - fecha_actual: Fecha más reciente disponible
    """
    # Convertir fecha a datetime y asegurar que sea tz-naive
    fecha_inv = pd.to_datetime(fecha_inversion)
    if fecha_inv.tz is not None:
        fecha_inv = fecha_inv.tz_localize(None)
    
    # Asegurar que el índice del DataFrame sea tz-naive
    if df.index.tz is not None:
        df = df.copy()
        df.index = df.index.tz_localize(None)
    
    # Obtener la fecha más reciente disponible
    fecha_actual = df.index.max()
    
    # Verificar que la fecha de inversión esté en el rango de datos
    if fecha_inv < df.index.min():
        raise ValueError(f"La fecha de inversión ({fecha_inversion}) es anterior a los datos disponibles ({df.index.min()})")
    
    if fecha_inv > fecha_actual:
        raise ValueError(f"La fecha de inversión ({fecha_inversion}) es posterior a los datos disponibles ({fecha_actual})")
    
    # Obtener el precio más cercano a la fecha de inversión (si no hay datos exactos, usar el siguiente día hábil)
    precios_disponibles = df[df.index >= fecha_inv]
    
    if precios_disponibles.empty:
        raise ValueError(f"No hay datos disponibles desde la fecha de inversión ({fecha_inversion})")
    
    precio_compra = precios_disponibles.iloc[0]['Close']
    precio_actual = df.iloc[-1]['Close']
    
    # Calcular número de "acciones" o unidades del índice compradas
    unidades_compradas = cantidad / precio_compra
    
    # Calcular valor actual
    valor_actual = unidades_compradas * precio_actual
    
    # Calcular ganancia/pérdida
    ganancia_perdida = valor_actual - cantidad
    
    # Calcular retorno porcentual
    retorno_porcentual = (ganancia_perdida / cantidad) * 100
    
    resultado = {
        'valor_actual': round(valor_actual, 2),
        'ganancia_perdida': round(ganancia_perdida, 2),
        'retorno_porcentual': round(retorno_porcentual, 2),
        'precio_compra': round(precio_compra, 2),
        'precio_actual': round(precio_actual, 2),
        'unidades_compradas': round(unidades_compradas, 6),
        'cantidad_invertida': cantidad,
        'fecha_inversion': fecha_inv.strftime('%Y-%m-%d'),
        'fecha_actual': fecha_actual.strftime('%Y-%m-%d'),
        'nombre_indice': nombre_indice
    }
    
    return resultado


def obtener_evolucion_inversion(df: pd.DataFrame, fecha_inversion: str, 
                                cantidad: float) -> pd.DataFrame:
    """
    Obtiene la evolución del valor de la inversión desde la fecha de inversión hasta hoy
    
    Args:
        df: DataFrame con datos históricos del índice
        fecha_inversion: Fecha de inversión en formato 'YYYY-MM-DD'
        cantidad: Cantidad de dinero invertida
    
    Returns:
        DataFrame con la evolución del valor de la inversión
    """
    fecha_inv = pd.to_datetime(fecha_inversion)
    # Asegurar que sea tz-naive
    if fecha_inv.tz is not None:
        fecha_inv = fecha_inv.tz_localize(None)
    
    # Asegurar que el índice del DataFrame sea tz-naive
    if df.index.tz is not None:
        df = df.copy()
        df.index = df.index.tz_localize(None)
    
    # Filtrar datos desde la fecha de inversión
    datos_desde_inversion = df[df.index >= fecha_inv].copy()
    
    if datos_desde_inversion.empty:
        raise ValueError(f"No hay datos disponibles desde la fecha de inversión ({fecha_inversion})")
    
    precio_compra = datos_desde_inversion.iloc[0]['Close']
    unidades_compradas = cantidad / precio_compra
    
    # Calcular el valor de la inversión en cada fecha
    datos_desde_inversion['Valor_Inversion'] = datos_desde_inversion['Close'] * unidades_compradas
    datos_desde_inversion['Ganancia_Perdida'] = datos_desde_inversion['Valor_Inversion'] - cantidad
    datos_desde_inversion['Retorno_Porcentual'] = (datos_desde_inversion['Ganancia_Perdida'] / cantidad) * 100
    
    return datos_desde_inversion[['Close', 'Valor_Inversion', 'Ganancia_Perdida', 'Retorno_Porcentual']]

