"""
Módulo para simulación de inversión periódica (dollar-cost averaging)
Proyecta inversiones futuras desde hoy
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def simular_inversion_periodica(df: pd.DataFrame, cantidad_mensual: float, 
                                años: int, nombre_indice: str = "") -> dict:
    """
    Simula una inversión periódica mensual FUTURA desde hoy
    
    Args:
        df: DataFrame con datos históricos del índice
        cantidad_mensual: Cantidad a invertir cada mes (€)
        años: Número de años de inversión FUTUROS
        nombre_indice: Nombre del índice
    
    Returns:
        Diccionario con resultados de la simulación
    """
    # Asegurar que el índice sea tz-naive
    if df.index.tz is not None:
        df = df.copy()
        df.index = df.index.tz_localize(None)
    
    # Fecha de inicio: HOY (última fecha disponible)
    fecha_inicio = df.index.max()
    precio_actual = df['Close'].iloc[-1]
    
    # Calcular retorno promedio histórico (últimos 10 años o todos los disponibles)
    años_historia = min(10, (df.index.max() - df.index.min()).days / 365.25)
    fecha_historia = fecha_inicio - pd.DateOffset(years=int(años_historia))
    df_historia = df[df.index >= fecha_historia].copy()
    
    if len(df_historia) < 20:
        df_historia = df.copy()
    
    # Calcular retorno promedio mensual histórico
    retornos_mensuales = df_historia['Close'].resample('M').last().pct_change().dropna()
    retorno_mensual_promedio = retornos_mensuales.mean()
    retorno_mensual_std = retornos_mensuales.std()
    
    # También calcular retorno anual promedio
    retorno_anual_promedio = retornos_mensuales.mean() * 12 * 100
    
    # Simular inversión mensual desde hoy hacia el futuro
    evolución = []
    unidades_totales = 0
    total_invertido = 0
    
    # Fecha actual para la simulación
    fecha_simulacion = fecha_inicio
    
    # Generar fechas mensuales futuras (incluyendo el mes inicial)
    fechas_futuras = pd.date_range(start=fecha_inicio, periods=años * 12 + 1, freq='MS')
    
    # Precio actual que irá creciendo
    precio_actual_sim = precio_actual
    
    for i, fecha_proyectada in enumerate(fechas_futuras):
        if i == 0:
            # Mes inicial: solo registramos el estado inicial
            evolución.append({
                'fecha': fecha_simulacion,
                'precio': precio_actual,
                'unidades_totales': 0,
                'total_invertido': 0,
                'valor_actual': 0,
                'ganancia': 0,
                'retorno_porcentual': 0
            })
        else:
            # Aplicar crecimiento al precio (usando retorno promedio)
            precio_actual_sim = precio_actual_sim * (1 + retorno_mensual_promedio)
            
            # Invertir cantidad mensual al precio proyectado
            unidades_compradas = cantidad_mensual / precio_actual_sim
            unidades_totales += unidades_compradas
            total_invertido += cantidad_mensual
            
            # Calcular valor del portfolio (unidades * precio actual)
            valor_portfolio = unidades_totales * precio_actual_sim
            
            ganancia = valor_portfolio - total_invertido
            retorno_porcentual = (ganancia / total_invertido * 100) if total_invertido > 0 else 0
            
            evolución.append({
                'fecha': fecha_proyectada,
                'precio': precio_actual_sim,
                'unidades_totales': unidades_totales,
                'total_invertido': total_invertido,
                'valor_actual': valor_portfolio,
                'ganancia': ganancia,
                'retorno_porcentual': retorno_porcentual
            })
    
    # Valor final proyectado
    valor_final = evolución[-1]['valor_actual']
    ganancia_total = valor_final - total_invertido
    retorno_total = (ganancia_total / total_invertido * 100) if total_invertido > 0 else 0
    
    # Proyección anual (resumen por años)
    proyeccion_anual = []
    for año in range(1, años + 1):
        mes_indice = año * 12
        if mes_indice < len(evolución):
            dato_año = evolución[mes_indice]
            proyeccion_anual.append({
                'año': fecha_inicio.year + año,
                'valor_proyectado': dato_año['valor_actual'],
                'contribucion_total': dato_año['total_invertido']
            })
    
    return {
        'valor_final': round(valor_final, 2),
        'total_invertido': round(total_invertido, 2),
        'ganancia_total': round(ganancia_total, 2),
        'retorno_total': round(retorno_total, 2),
        'unidades_totales': round(unidades_totales, 6),
        'precio_actual': round(precio_actual, 2),
        'precio_final_proyectado': round(evolución[-1]['precio'], 2),
        'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
        'fecha_fin_proyectada': fechas_futuras[-1].strftime('%Y-%m-%d'),
        'evolucion': evolución,
        'proyeccion_futura': proyeccion_anual,
        'retorno_anual_promedio': round(retorno_anual_promedio, 2),
        'retorno_mensual_promedio': round(retorno_mensual_promedio * 100, 2),
        'nombre_indice': nombre_indice
    }
