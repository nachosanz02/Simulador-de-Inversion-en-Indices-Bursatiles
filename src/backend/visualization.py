"""
Módulo para la visualización de datos de índices bursátiles e inversiones
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


from . import utils


def grafico_evolucion_indice(df: pd.DataFrame, nombre_indice: str) -> go.Figure:
    """
    Crea un gráfico de línea con la evolución histórica del índice
    
    Args:
        df: DataFrame con datos históricos del índice
        nombre_indice: Nombre del índice
    
    Returns:
        Figura de Plotly
    """
    fig = go.Figure()
    info_divisa = utils.obtener_info_divisa_indice(nombre_indice)
    divisa = info_divisa['codigo']
    simbolo_divisa = info_divisa['simbolo']
    
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Close'],
        mode='lines',
        name=nombre_indice,
        line=dict(color='#1f77b4', width=2),
        hovertemplate='<b>%{fullData.name}</b><br>' +
                      'Fecha: %{x}<br>' +
                      f'Precio: {simbolo_divisa}%{{y:,.2f}}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f'Evolución Histórica del {nombre_indice} ({divisa})',
        xaxis_title='Fecha',
        yaxis_title=f'Precio de Cierre ({divisa})',
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    return fig


def grafico_comparacion_indices_multiple(datos_indices: dict, indices_seleccionados: list) -> go.Figure:
    """
    Crea un gráfico comparativo de múltiples índices seleccionados (normalizados)
    Normaliza todos los índices a partir de una fecha común (la más reciente disponible)
    para comparar correctamente índices en distintas divisas
    
    Args:
        datos_indices: Diccionario con todos los índices y sus DataFrames
        indices_seleccionados: Lista de nombres de índices a comparar
    
    Returns:
        Figura de Plotly
    """
    fig = go.Figure()
    
    colores = px.colors.qualitative.Set1
    
    # Encontrar la fecha más reciente común entre todos los índices
    fechas_maximas = []
    for nombre_indice in indices_seleccionados:
        if nombre_indice in datos_indices:
            df = datos_indices[nombre_indice]
            if 'Close' in df.columns and len(df) > 0:
                fechas_maximas.append(df.index.max())
    
    if not fechas_maximas:
        return fig
    
    # Usar la fecha más reciente común (o la más antigua de las máximas para tener datos de todos)
    fecha_referencia = min(fechas_maximas)
    
    # También encontrar la fecha más antigua común para el rango del gráfico
    fechas_minimas = []
    for nombre_indice in indices_seleccionados:
        if nombre_indice in datos_indices:
            df = datos_indices[nombre_indice]
            if 'Close' in df.columns and len(df) > 0:
                # Filtrar solo datos hasta la fecha de referencia
                df_filtrado = df[df.index <= fecha_referencia]
                if len(df_filtrado) > 0:
                    fechas_minimas.append(df_filtrado.index.min())
    
    fecha_inicio_comun = max(fechas_minimas) if fechas_minimas else fecha_referencia - pd.DateOffset(years=10)
    
    for i, nombre_indice in enumerate(indices_seleccionados):
        if nombre_indice in datos_indices:
            df = datos_indices[nombre_indice]
            if 'Close' in df.columns and len(df) > 0:
                # Filtrar datos hasta la fecha de referencia
                df_filtrado = df[df.index <= fecha_referencia].copy()
                df_filtrado = df_filtrado[df_filtrado.index >= fecha_inicio_comun]
                
                if len(df_filtrado) > 0:
                    # Normalizar al 100% en la fecha de referencia (última fecha común)
                    precio_referencia = df_filtrado['Close'].iloc[-1]
                    valores_normalizados = (df_filtrado['Close'] / precio_referencia) * 100
                    
                    fig.add_trace(go.Scatter(
                        x=df_filtrado.index,
                        y=valores_normalizados,
                        mode='lines',
                        name=nombre_indice,
                        line=dict(color=colores[i % len(colores)], width=2.5),
                        hovertemplate=f'<b>{nombre_indice}</b><br>' +
                                      'Fecha: %{x}<br>' +
                                      'Valor normalizado: %{y:.2f}%<br>' +
                                      'Precio: %{customdata:,.2f}<extra></extra>',
                        customdata=df_filtrado['Close']
                    ))
    
    fig.update_layout(
        title='Comparación de Índices Bursátiles (Normalizados al 100% en fecha común)',
        xaxis_title='Fecha',
        yaxis_title='Valor Normalizado (%)',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def grafico_evolucion_inversion(df_evolucion: pd.DataFrame, nombre_indice: str, divisa_inversion: str = None) -> go.Figure:
    """
    Crea un gráfico con la evolución del valor de una inversión
    
    Args:
        df_evolucion: DataFrame con la evolución de la inversión (debe tener 'Valor_Inversion')
        nombre_indice: Nombre del índice
        divisa_inversion: Divisa de la inversión (si es None, usa la del índice)
    
    Returns:
        Figura de Plotly
    """
    fig = go.Figure()
    
    if divisa_inversion is None:
        info_divisa = utils.obtener_info_divisa_indice(nombre_indice)
        divisa = info_divisa['codigo']
        simbolo_divisa = info_divisa['simbolo']
    else:
        info_divisa = utils.obtener_info_divisa_indice(nombre_indice)
        divisa = divisa_inversion
        simbolo_divisa = {'USD': '$', 'EUR': '€', 'GBP': '£'}.get(divisa, divisa)
    
    # Línea del valor de la inversión
    fig.add_trace(go.Scatter(
        x=df_evolucion.index,
        y=df_evolucion['Valor_Inversion'],
        mode='lines',
        name='Valor de la Inversión',
        line=dict(color='#2ca02c', width=2),
        hovertemplate='<b>Valor de la Inversión</b><br>' +
                      'Fecha: %{x}<br>' +
                      f'Valor: {simbolo_divisa}%{{y:,.2f}}<br>' +
                      'Retorno: %{customdata:.2f}%<extra></extra>',
        customdata=df_evolucion['Retorno_Porcentual']
    ))
    
    # Línea de referencia (cantidad invertida)
    cantidad_invertida = df_evolucion['Valor_Inversion'].iloc[0] - df_evolucion['Ganancia_Perdida'].iloc[0]
    fig.add_hline(
        y=cantidad_invertida,
        line_dash="dash",
        line_color="gray",
        annotation_text=f"Inversión inicial: {simbolo_divisa}{cantidad_invertida:,.2f}",
        annotation_position="right"
    )
    
    fig.update_layout(
        title=f'Evolución de la Inversión en {nombre_indice} ({divisa})',
        xaxis_title='Fecha',
        yaxis_title=f'Valor ({divisa})',
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    return fig


def grafico_inversion_periodica(resultado_simulacion: dict) -> go.Figure:
    """
    Crea un gráfico de proyección de inversión periódica FUTURA desde hoy
    
    Args:
        resultado_simulacion: Diccionario con resultados de simulación periódica
    
    Returns:
        Figura de Plotly
    """
    fig = go.Figure()
    
    # Obtener información de divisa
    nombre_indice = resultado_simulacion.get('nombre_indice', '')
    info_divisa = utils.obtener_info_divisa_indice(nombre_indice)
    divisa = info_divisa['codigo']
    simbolo_divisa = info_divisa['simbolo']
    
    # Datos de evolución mensual
    evolucion = resultado_simulacion['evolucion']
    fechas = [pd.to_datetime(e['fecha']) for e in evolucion]
    valores = [e['valor_actual'] for e in evolucion]
    contribuciones = [e['total_invertido'] for e in evolucion]
    
    # Datos de proyección anual (para mostrar puntos clave)
    proyeccion = resultado_simulacion['proyeccion_futura']
    años_proy = [pd.Timestamp(f"{p['año']}-01-01") for p in proyeccion]
    valores_anuales = [p['valor_proyectado'] for p in proyeccion]
    contribuciones_anuales = [p['contribucion_total'] for p in proyeccion]
    
    # Línea de valor proyectado (verde con área sombreada)
    fig.add_trace(go.Scatter(
        x=fechas,
        y=valores,
        mode='lines',
        name='Valor Proyectado',
        line=dict(color='#2ca02c', width=3),
        fill='tozeroy',
        fillcolor='rgba(44, 160, 44, 0.2)',
        hovertemplate='<b>Valor Proyectado</b><br>' +
                      'Fecha: %{x}<br>' +
                      f'Valor: {simbolo_divisa}%{{y:,.0f}}<extra></extra>'
    ))
    
    # Línea de contribución (azul)
    fig.add_trace(go.Scatter(
        x=fechas,
        y=contribuciones,
        mode='lines',
        name='Tu Contribución',
        line=dict(color='#1f77b4', width=2.5, dash='dash'),
        hovertemplate='<b>Tu Contribución</b><br>' +
                      'Fecha: %{x}<br>' +
                      f'Contribución: {simbolo_divisa}%{{y:,.0f}}<extra></extra>'
    ))
    
    # Área sombreada para incertidumbre (rango basado en volatilidad histórica)
    if len(valores) > 0:
        # Usar rangos de incertidumbre del resultado de simulación si están disponibles
        if 'evolucion' in resultado_simulacion and len(resultado_simulacion['evolucion']) > 0:
            # Verificar si los datos tienen rangos calculados
            primer_punto = resultado_simulacion['evolucion'][0]
            if 'valor_min' in primer_punto and 'valor_max' in primer_punto:
                valores_min = [p['valor_min'] for p in resultado_simulacion['evolucion']]
                valores_max = [p['valor_max'] for p in resultado_simulacion['evolucion']]
            else:
                # Fallback: usar volatilidad si está disponible
                if 'volatilidad_mensual' in resultado_simulacion:
                    vol = resultado_simulacion['volatilidad_mensual'] / 100
                    # Calcular rango usando volatilidad acumulada
                    valores_min = []
                    valores_max = []
                    for i, v in enumerate(valores):
                        meses = i
                        if meses > 0:
                            vol_acum = vol * np.sqrt(meses)
                            valores_min.append(max(0, v * (1 - vol_acum)))
                            valores_max.append(v * (1 + vol_acum))
                        else:
                            valores_min.append(v)
                            valores_max.append(v)
                else:
                    # Fallback final: usar ±20% si no hay datos de volatilidad
                    valores_min = [v * 0.8 for v in valores]
                    valores_max = [v * 1.2 for v in valores]
        else:
            # Fallback: usar ±20% si no hay datos
            valores_min = [v * 0.8 for v in valores]
            valores_max = [v * 1.2 for v in valores]
        
        fig.add_trace(go.Scatter(
            x=fechas,
            y=valores_max,
            mode='lines',
            name='Rango Superior',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Crear datos para el tooltip con ambos valores (min y max)
        valores_max_aligned = valores_max[:len(valores_min)]
        valores_min_aligned = valores_min
        
        fig.add_trace(go.Scatter(
            x=fechas,
            y=valores_min,
            mode='lines',
            name='Rango de Incertidumbre',
            fill='tonexty',
            fillcolor='rgba(44, 160, 44, 0.1)',
            line=dict(width=0),
            hovertemplate='<b>Rango de Incertidumbre</b><br>' +
                          'Fecha: %{x}<br>' +
                          f'Mínimo: {simbolo_divisa}%{{y:,.0f}}<br>' +
                          f'Máximo: {simbolo_divisa}%{{customdata:,.0f}}<extra></extra>',
            customdata=valores_max_aligned
        ))
    
    # Añadir puntos anuales destacados
    if len(años_proy) > 0:
        fig.add_trace(go.Scatter(
            x=años_proy,
            y=valores_anuales,
            mode='markers',
            name='Valores Anuales',
            marker=dict(size=8, color='#2ca02c', symbol='circle'),
            hovertemplate='<b>%{fullData.name}</b><br>' +
                          'Año: %{x|%Y}<br>' +
                          f'Valor: {simbolo_divisa}%{{y:,.0f}}<extra></extra>',
            showlegend=False
        ))
    
    # Crear título con información adicional
    titulo_completo = f'Proyección de Inversión Periódica - {resultado_simulacion["nombre_indice"]} ({divisa})<br><sub>Inicio: {resultado_simulacion["fecha_inicio"]} | Fin proyectado: {resultado_simulacion["fecha_fin_proyectada"]}</sub>'
    
    fig.update_layout(
        title=titulo_completo,
        xaxis_title='Fecha',
        yaxis_title=f'Valor ({divisa})',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def grafico_comparacion_indices(datos_indices: dict) -> go.Figure:
    """
    Crea un gráfico comparativo de la evolución de todos los índices (normalizados)
    
    Args:
        datos_indices: Diccionario con nombres de índices y sus DataFrames
    
    Returns:
        Figura de Plotly
    """
    fig = go.Figure()
    
    colores = px.colors.qualitative.Set3
    
    for i, (nombre_indice, df) in enumerate(datos_indices.items()):
        if 'Close' in df.columns:
            # Normalizar al 100% en la primera fecha común
            precio_inicial = df['Close'].iloc[0]
            valores_normalizados = (df['Close'] / precio_inicial) * 100
            
            fig.add_trace(go.Scatter(
                x=df.index,
                y=valores_normalizados,
                mode='lines',
                name=nombre_indice,
                line=dict(color=colores[i % len(colores)], width=2),
                hovertemplate=f'<b>{nombre_indice}</b><br>' +
                              'Fecha: %{x}<br>' +
                              'Valor normalizado: %{y:.2f}%<extra></extra>'
            ))
    
    fig.update_layout(
        title='Comparación de Índices Bursátiles (Normalizados al 100%)',
        xaxis_title='Fecha',
        yaxis_title='Valor Normalizado (%)',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def grafico_prophet_prediccion(resultado_prophet: dict, nombre_indice: str) -> go.Figure:
    """
    Crea un gráfico con las predicciones de Prophet mostrando datos históricos,
    predicción futura e intervalos de confianza
    
    Args:
        resultado_prophet: Diccionario con resultados de Prophet
        nombre_indice: Nombre del índice
    
    Returns:
        Figura de Plotly
    """
    fig = go.Figure()
    
    # Obtener información de divisa
    info_divisa = utils.obtener_info_divisa_indice(nombre_indice)
    divisa = info_divisa['codigo']
    simbolo_divisa = info_divisa['simbolo']
    
    prediccion = resultado_prophet['prediccion_completa']
    precio_actual = resultado_prophet['precio_actual']
    
    # Obtener la fecha de la última predicción futura para separar histórico y futuro
    # Prophet incluye los datos históricos + los periodos futuros
    # Necesitamos encontrar dónde termina el histórico
    prediccion_futura = resultado_prophet['prediccion_futura']
    
    if len(prediccion_futura) > 0:
        # La primera fecha futura es donde empieza la predicción
        fecha_inicio_futuro = prediccion_futura['ds'].iloc[0]
        historico = prediccion[prediccion['ds'] < fecha_inicio_futuro]
        futuro = prediccion[prediccion['ds'] >= fecha_inicio_futuro]
    else:
        # Si no hay predicción futura, todo es histórico
        historico = prediccion
        futuro = pd.DataFrame()
    
    # Línea de datos históricos (solo últimos 2 años para claridad)
    if len(historico) > 0:
        historico_reciente = historico.tail(500)  # Últimos ~2 años
        fig.add_trace(go.Scatter(
            x=historico_reciente['ds'],
            y=historico_reciente['yhat'],
            mode='lines',
            name='Ajuste Histórico',
            line=dict(color='#1f77b4', width=2),
            hovertemplate='<b>Ajuste Histórico</b><br>' +
                          'Fecha: %{x}<br>' +
                          f'Precio: {simbolo_divisa}%{{y:,.2f}}<extra></extra>'
        ))
    
    # Línea de predicción futura
    if len(futuro) > 0:
        fig.add_trace(go.Scatter(
            x=futuro['ds'],
            y=futuro['yhat'],
            mode='lines',
            name='Predicción Prophet',
            line=dict(color='#2ca02c', width=3, dash='dash'),
            hovertemplate='<b>Predicción</b><br>' +
                          'Fecha: %{x}<br>' +
                          f'Precio predicho: {simbolo_divisa}%{{y:,.2f}}<extra></extra>'
        ))
        
        # Intervalo de confianza superior
        fig.add_trace(go.Scatter(
            x=futuro['ds'],
            y=futuro['yhat_upper'],
            mode='lines',
            name='Intervalo Superior',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Intervalo de confianza inferior (relleno)
        fig.add_trace(go.Scatter(
            x=futuro['ds'],
            y=futuro['yhat_lower'],
            mode='lines',
            name='Intervalo de Confianza (80%)',
            fill='tonexty',
            fillcolor='rgba(44, 160, 44, 0.2)',
            line=dict(width=0),
            hovertemplate='<b>Intervalo de Confianza</b><br>' +
                          'Fecha: %{x}<br>' +
                          f'Rango: {simbolo_divisa}%{{y:,.2f}}<extra></extra>'
        ))
    
    # Línea vertical indicando el presente
    if len(historico) > 0 and len(futuro) > 0:
        fecha_presente = historico['ds'].iloc[-1]
        fig.add_vline(
            x=fecha_presente,
            line_dash="dot",
            line_color="gray",
            annotation_text="Hoy",
            annotation_position="top"
        )
    
    # Punto del precio actual
    if len(historico) > 0:
        fecha_ultima = historico['ds'].iloc[-1]
        fig.add_trace(go.Scatter(
            x=[fecha_ultima],
            y=[precio_actual],
            mode='markers',
            name='Precio Actual',
            marker=dict(size=10, color='red', symbol='circle'),
            hovertemplate='<b>Precio Actual</b><br>' +
                          'Fecha: %{x}<br>' +
                          f'Precio: {simbolo_divisa}%{{y:,.2f}}<extra></extra>'
        ))
    
    # Punto del precio predicho (30 días)
    if 'precio_predicho_30d' in resultado_prophet and resultado_prophet['precio_predicho_30d']:
        if len(futuro) > 0:
            fecha_predicha = futuro['ds'].iloc[-1]
            precio_predicho = resultado_prophet['precio_predicho_30d']
            fig.add_trace(go.Scatter(
                x=[fecha_predicha],
                y=[precio_predicho],
                mode='markers',
                name='Precio Predicho (30d)',
                marker=dict(size=10, color='green', symbol='star'),
                hovertemplate='<b>Precio Predicho (30 días)</b><br>' +
                              'Fecha: %{x}<br>' +
                              f'Precio: {simbolo_divisa}%{{y:,.2f}}<extra></extra>'
            ))
    
    fig.update_layout(
        title=f'Predicción Prophet - {nombre_indice} ({divisa})',
        xaxis_title='Fecha',
        yaxis_title=f'Precio ({divisa})',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def grafico_retornos_diarios(df: pd.DataFrame, nombre_indice: str) -> go.Figure:
    """
    Crea un gráfico de barras con los retornos diarios del índice
    
    Args:
        df: DataFrame con datos históricos (debe tener columna 'Returns')
        nombre_indice: Nombre del índice
    
    Returns:
        Figura de Plotly
    """
    if 'Returns' not in df.columns:
        raise ValueError("El DataFrame debe tener una columna 'Returns'")
    
    fig = go.Figure()
    
    # Colores: verde para positivos, rojo para negativos
    colores = ['#2ca02c' if x >= 0 else '#d62728' for x in df['Returns']]
    
    fig.add_trace(go.Bar(
        x=df.index,
        y=df['Returns'] * 100,  # Convertir a porcentaje
        marker_color=colores,
        name='Retornos Diarios',
        hovertemplate='<b>Retorno Diario</b><br>' +
                      'Fecha: %{x}<br>' +
                      'Retorno: %{y:.2f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title=f'Retornos Diarios del {nombre_indice}',
        xaxis_title='Fecha',
        yaxis_title='Retorno (%)',
        template='plotly_white',
        height=400
    )
    
    return fig
