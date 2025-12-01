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
        title=dict(text=f'Evolución Histórica del {nombre_indice} ({divisa})', x=0.5, xanchor='center'),
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
    
    # Encontrar la fecha más antigua común (para normalizar al 100% al inicio)
    # y la fecha más reciente (para mostrar hasta hoy)
    fechas_minimas = []
    fechas_maximas = []
    for nombre_indice in indices_seleccionados:
        if nombre_indice in datos_indices:
            df = datos_indices[nombre_indice]
            if 'Close' in df.columns and len(df) > 0:
                fechas_minimas.append(df.index.min())
                fechas_maximas.append(df.index.max())
    
    if not fechas_minimas or not fechas_maximas:
        return fig
    
    # Fecha de inicio común: la más reciente de las fechas mínimas (para que todos tengan datos desde ahí)
    fecha_inicio_comun = max(fechas_minimas)
    # Fecha final: mostrar hasta hoy (la más reciente disponible de cada índice)
    # No limitamos a una fecha común, cada índice muestra hasta su fecha más reciente
    
    for i, nombre_indice in enumerate(indices_seleccionados):
        if nombre_indice in datos_indices:
            df = datos_indices[nombre_indice]
            if 'Close' in df.columns and len(df) > 0:
                # Filtrar datos desde la fecha de inicio común hasta hoy (fecha máxima de cada índice)
                df_filtrado = df[df.index >= fecha_inicio_comun].copy()
                
                if len(df_filtrado) > 0:
                    # Normalizar al 0% en la fecha de inicio común (mostrar crecimiento porcentual)
                    precio_referencia = df_filtrado['Close'].iloc[0]
                    valores_normalizados = ((df_filtrado['Close'] / precio_referencia) - 1) * 100
                    
                    fig.add_trace(go.Scatter(
                        x=df_filtrado.index,
                        y=valores_normalizados,
                        mode='lines',
                        name=nombre_indice,
                        line=dict(color=colores[i % len(colores)], width=2.5),
                        hovertemplate=f'<b>{nombre_indice}</b><br>' +
                                      'Fecha: %{x}<br>' +
                                      'Crecimiento: %{y:.2f}%<br>' +
                                      'Precio: %{customdata:,.2f}<extra></extra>',
                        customdata=df_filtrado['Close']
                    ))
    
    # Calcular el rango del eje Y basado en los valores de crecimiento porcentual
    # Encontrar el valor máximo y mínimo de todos los índices para ajustar el rango
    valores_maximos = []
    valores_minimos = []
    for nombre_indice in indices_seleccionados:
        if nombre_indice in datos_indices:
            df = datos_indices[nombre_indice]
            if 'Close' in df.columns and len(df) > 0:
                df_filtrado = df[df.index >= fecha_inicio_comun].copy()
                if len(df_filtrado) > 0:
                    precio_referencia = df_filtrado['Close'].iloc[0]
                    valores_normalizados = ((df_filtrado['Close'] / precio_referencia) - 1) * 100
                    valores_maximos.append(valores_normalizados.max())
                    valores_minimos.append(valores_normalizados.min())
    
    # Ajustar el rango del eje Y: empezar desde 0% (o un poco menos para mejor visualización)
    y_min = -10
    if valores_minimos:
        y_min = min(0, min(valores_minimos) * 1.1)  # 10% de margen por debajo del mínimo
    
    y_max = 100
    if valores_maximos:
        y_max = max(valores_maximos) * 1.1  # 10% de margen por encima del máximo
    
    fig.update_layout(
        title=dict(text='Comparación de Índices Bursátiles (Crecimiento desde fecha inicial)', x=0.5, xanchor='center'),
        xaxis_title='Fecha',
        yaxis_title='Crecimiento (%)',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(range=[y_min, y_max])
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
                      'Valor: €%{y:,.2f}<br>' +
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
        title=dict(text=f'Evolución de la Inversión en {nombre_indice} ({divisa})', x=0.5, xanchor='center'),
        xaxis_title='Fecha',
        yaxis_title=f'Valor ({divisa})',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="right", x=1.02)
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
    
    # Datos de proyección anual (ya no se usan para puntos, pero se mantienen por si se necesitan)
    proyeccion = resultado_simulacion['proyeccion_futura']
    
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
    
    
    # Crear título con información adicional
    titulo_completo = f'Proyección de Inversión Periódica - {resultado_simulacion["nombre_indice"]} ({divisa})<br><sub>Inicio: {resultado_simulacion["fecha_inicio"]} | Fin proyectado: {resultado_simulacion["fecha_fin_proyectada"]}</sub>'
    
    fig.update_layout(
        title=dict(text=titulo_completo, x=0.5, xanchor='center'),
        xaxis_title='Fecha',
        yaxis_title=f'Valor ({divisa})',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="right", x=1.02)
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
    fecha_max_historica = resultado_prophet.get('fecha_max_historica', None)
    prediccion_futura = resultado_prophet['prediccion_futura']
    
    # Separar histórico y futuro usando fecha_max_historica
    if fecha_max_historica is not None:
        # Asegurar que fecha_max_historica sea timezone-naive
        if isinstance(fecha_max_historica, pd.Timestamp):
            if fecha_max_historica.tz is not None:
                fecha_max_historica = fecha_max_historica.tz_localize(None)
        else:
            fecha_max_historica = pd.to_datetime(fecha_max_historica)
            if fecha_max_historica.tz is not None:
                fecha_max_historica = fecha_max_historica.tz_localize(None)
        
        # Asegurar que las fechas de predicción sean timezone-naive
        prediccion['ds'] = pd.to_datetime(prediccion['ds'])
        if prediccion['ds'].dt.tz is not None:
            prediccion['ds'] = prediccion['ds'].dt.tz_localize(None)
        
        # Separar: histórico hasta fecha_max_historica (incluida), futuro después
        historico = prediccion[prediccion['ds'] <= fecha_max_historica].copy()
        futuro = prediccion[prediccion['ds'] > fecha_max_historica].copy()
    elif len(prediccion_futura) > 0:
        # Fallback: usar la primera fecha futura
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
        # Convertir fechas a datetime de Python para evitar problemas con Plotly
        fechas_historico = pd.to_datetime(historico_reciente['ds']).dt.tz_localize(None).tolist()
        valores_historico = historico_reciente['yhat'].tolist()
        
        fig.add_trace(go.Scatter(
            x=fechas_historico,
            y=valores_historico,
            mode='lines',
            name='Ajuste Histórico',
            line=dict(color='#1f77b4', width=2),
            hovertemplate='<b>Ajuste Histórico</b><br>' +
                          'Fecha: %{x}<br>' +
                          f'Precio: {simbolo_divisa}%{{y:,.2f}}<extra></extra>'
        ))
    
    # Línea de predicción futura
    if len(futuro) > 0:
        # Convertir fechas a datetime de Python para evitar problemas con Plotly
        fechas_futuro = pd.to_datetime(futuro['ds']).dt.tz_localize(None).tolist()
        valores_futuro = futuro['yhat'].tolist()
        valores_upper = futuro['yhat_upper'].tolist()
        valores_lower = futuro['yhat_lower'].tolist()
        
        fig.add_trace(go.Scatter(
            x=fechas_futuro,
            y=valores_futuro,
            mode='lines',
            name='Predicción Prophet',
            line=dict(color='#2ca02c', width=3, dash='dash'),
            hovertemplate='<b>Predicción</b><br>' +
                          'Fecha: %{x}<br>' +
                          f'Precio predicho: {simbolo_divisa}%{{y:,.2f}}<extra></extra>'
        ))
        
        # Intervalo de confianza superior
        fig.add_trace(go.Scatter(
            x=fechas_futuro,
            y=valores_upper,
            mode='lines',
            name='Intervalo Superior',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Intervalo de confianza inferior (relleno)
        fig.add_trace(go.Scatter(
            x=fechas_futuro,
            y=valores_lower,
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
        # Convertir Timestamp a datetime de Python para evitar problemas con Plotly
        if isinstance(fecha_presente, pd.Timestamp):
            fecha_presente_dt = fecha_presente.to_pydatetime()
        else:
            fecha_presente_dt = pd.to_datetime(fecha_presente).to_pydatetime()
        
        # Usar add_shape en lugar de add_vline para evitar errores con tipos
        fig.add_shape(
            type="line",
            x0=fecha_presente_dt,
            x1=fecha_presente_dt,
            y0=0,
            y1=1,
            yref="paper",
            line=dict(color="gray", width=1, dash="dot")
        )
        
        # Agregar anotación de texto
        try:
            fig.add_annotation(
                x=fecha_presente_dt,
                y=1,
                yref="paper",
                text="Hoy",
                showarrow=False,
                xanchor="center",
                yshift=10
            )
        except:
            # Si falla, simplemente no agregar la anotación
            pass
    
    # Punto del precio actual - debe mostrar el precio REAL del mercado en la fecha de "Hoy"
    # Nota: Es normal que no coincida exactamente con la línea azul (ajuste Prophet) porque
    # Prophet suaviza los datos. El punto rojo representa el valor real del mercado.
    if fecha_max_historica is not None:
        # Convertir fecha_max_historica a datetime de Python
        fecha_max_historica_clean = fecha_max_historica
        if isinstance(fecha_max_historica_clean, pd.Timestamp):
            if fecha_max_historica_clean.tz is not None:
                fecha_max_historica_clean = fecha_max_historica_clean.tz_localize(None)
            fecha_hoy_dt = fecha_max_historica_clean.to_pydatetime()
        else:
            fecha_hoy_dt = pd.to_datetime(fecha_max_historica_clean).tz_localize(None).to_pydatetime()
        
        # Obtener el valor del ajuste Prophet en esa fecha para comparación (opcional en tooltip)
        ajuste_prophet_hoy = None
        if len(historico) > 0:
            # Asegurar que las fechas del histórico sean timezone-naive para comparación
            historico['ds'] = pd.to_datetime(historico['ds'])
            if historico['ds'].dt.tz is not None:
                historico['ds'] = historico['ds'].dt.tz_localize(None)
            
            historico_en_hoy = historico[historico['ds'] == fecha_max_historica_clean]
            if len(historico_en_hoy) > 0:
                ajuste_prophet_hoy = historico_en_hoy['yhat'].iloc[0]
        
        # El punto rojo muestra el precio REAL del mercado (precio_actual)
        # Este es el valor Close del último día disponible del índice
        tooltip_text = f'<b>Precio Actual (Real)</b><br>' + \
                      f'Fecha: %{{x}}<br>' + \
                      f'Precio real: {simbolo_divisa}{precio_actual:,.2f}<extra></extra>'
        
        if ajuste_prophet_hoy is not None:
            tooltip_text = f'<b>Precio Actual (Real)</b><br>' + \
                          f'Fecha: %{{x}}<br>' + \
                          f'Precio real: {simbolo_divisa}{precio_actual:,.2f}<br>' + \
                          f'Ajuste Prophet: {simbolo_divisa}{ajuste_prophet_hoy:,.2f}<extra></extra>'
        
        fig.add_trace(go.Scatter(
            x=[fecha_hoy_dt],
            y=[precio_actual],  # Usar el precio REAL del mercado
            mode='markers',
            name='Precio Actual',
            marker=dict(size=10, color='red', symbol='circle'),
            hovertemplate=tooltip_text
        ))
    
    # Punto del precio predicho (30 días) - REMOVIDO según solicitud anterior
    
    fig.update_layout(
        title=dict(text=f'Predicción Prophet - {nombre_indice} ({divisa})', x=0.5, xanchor='center'),
        xaxis_title='Fecha',
        yaxis_title=f'Precio ({divisa})',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="right", x=1.02)
    )
    
    return fig



