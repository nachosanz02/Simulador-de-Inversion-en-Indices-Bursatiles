"""
Módulo para la visualización de datos de índices bursátiles e inversiones
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


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
    
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Close'],
        mode='lines',
        name=nombre_indice,
        line=dict(color='#1f77b4', width=2),
        hovertemplate='<b>%{fullData.name}</b><br>' +
                      'Fecha: %{x}<br>' +
                      'Precio: €%{y:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f'Evolución Histórica del {nombre_indice}',
        xaxis_title='Fecha',
        yaxis_title='Precio de Cierre (€)',
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    return fig


def grafico_evolucion_inversion(df_evolucion: pd.DataFrame, nombre_indice: str) -> go.Figure:
    """
    Crea un gráfico con la evolución del valor de una inversión
    
    Args:
        df_evolucion: DataFrame con la evolución de la inversión (debe tener 'Valor_Inversion')
        nombre_indice: Nombre del índice
    
    Returns:
        Figura de Plotly
    """
    fig = go.Figure()
    
    # Línea del valor de la inversión
    fig.add_trace(go.Scatter(
        x=df_evolucion.index,
        y=df_evolucion['Valor_Inversion'],
        mode='lines',
        name='Valor de la Inversión',
        line=dict(color='#2ca02c', width=2),
        hovertemplate='<b>Valor de la Inversión</b><br>' +
                      'Fecha: %{x}<br>' +
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
        annotation_text=f"Inversión inicial: €{cantidad_invertida:,.2f}",
        annotation_position="right"
    )
    
    fig.update_layout(
        title=f'Evolución de la Inversión en {nombre_indice}',
        xaxis_title='Fecha',
        yaxis_title='Valor (€)',
        hovermode='x unified',
        template='plotly_white',
        height=500
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

