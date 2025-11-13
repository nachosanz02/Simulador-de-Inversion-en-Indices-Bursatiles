"""
Aplicación Dash para el Simulador de Inversión en Índices Bursátiles
"""

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.backend import data_collection, preprocessing, simulation, visualization, ml_models


# Inicializar la aplicación Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Simulador de Inversión en Índices Bursátiles"

# Índices disponibles
INDICES_DISPONIBLES = list(data_collection.INDICES.keys())


# Layout de la aplicación
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("📈 Simulador de Inversión en Índices Bursátiles", 
                   className="text-center mb-4"),
            html.P("Simula inversiones pasadas en los principales índices bursátiles internacionales",
                  className="text-center text-muted mb-4")
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Parámetros de Simulación"),
                dbc.CardBody([
                    html.Label("Selecciona el índice:"),
                    dcc.Dropdown(
                        id='dropdown-indice',
                        options=[{'label': idx, 'value': idx} for idx in INDICES_DISPONIBLES],
                        value=INDICES_DISPONIBLES[0] if INDICES_DISPONIBLES else None,
                        className="mb-3"
                    ),
                    
                    html.Label("Fecha de inversión:"),
                    dcc.DatePickerSingle(
                        id='date-picker',
                        date=datetime.now() - timedelta(days=365*5),
                        display_format='YYYY-MM-DD',
                        className="mb-3"
                    ),
                    
                    html.Label("Cantidad invertida (€):"),
                    dcc.Input(
                        id='input-cantidad',
                        type='number',
                        value=1000,
                        min=1,
                        className="form-control mb-3"
                    ),
                    
                    dbc.Button("Calcular Simulación", id='btn-calcular', 
                              color="primary", className="w-100")
                ])
            ], className="mb-4")
        ], md=4),
        
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Resultados de la Simulación"),
                dbc.CardBody(id='resultados-simulacion')
            ], className="mb-4")
        ], md=8)
    ]),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='grafico-evolucion-indice')
        ], md=6),
        dbc.Col([
            dcc.Graph(id='grafico-evolucion-inversion')
        ], md=6)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Predicción ML"),
                dbc.CardBody(id='prediccion-ml')
            ])
        ], md=12)
    ], className="mt-4"),
    
    # Almacenamiento para datos
    dcc.Store(id='store-datos-indice'),
    dcc.Store(id='store-resultado-simulacion')
    
], fluid=True)


# Callbacks
@app.callback(
    [Output('store-datos-indice', 'data'),
     Output('grafico-evolucion-indice', 'figure')],
    [Input('dropdown-indice', 'value')]
)
def cargar_datos_indice(nombre_indice):
    """Carga los datos del índice seleccionado"""
    if nombre_indice is None:
        return None, {}
    
    try:
        # Intentar cargar datos procesados
        df = preprocessing.cargar_datos_procesados(nombre_indice)
        fig = visualization.grafico_evolucion_indice(df, nombre_indice)
        return df.to_dict('records'), fig
    except FileNotFoundError:
        # Si no existen datos procesados, intentar descargar
        try:
            simbolo = data_collection.INDICES[nombre_indice]
            df = data_collection.descargar_indice(simbolo)
            df = preprocessing.limpiar_datos(df, nombre_indice)
            fig = visualization.grafico_evolucion_indice(df, nombre_indice)
            return df.to_dict('records'), fig
        except Exception as e:
            return None, {
                'data': [],
                'layout': {'title': f'Error: {str(e)}'}
            }


@app.callback(
    [Output('resultados-simulacion', 'children'),
     Output('store-resultado-simulacion', 'data'),
     Output('grafico-evolucion-inversion', 'figure')],
    [Input('btn-calcular', 'n_clicks')],
    [State('dropdown-indice', 'value'),
     State('date-picker', 'date'),
     State('input-cantidad', 'value'),
     State('store-datos-indice', 'data')]
)
def calcular_simulacion(n_clicks, nombre_indice, fecha_inversion, cantidad, datos_indice):
    """Calcula la simulación de inversión"""
    if n_clicks is None or nombre_indice is None or fecha_inversion is None or cantidad is None:
        return "Ingresa los parámetros y haz clic en 'Calcular Simulación'", None, {}
    
    if datos_indice is None:
        return "Error: No hay datos disponibles del índice seleccionado", None, {}
    
    try:
        # Convertir datos de vuelta a DataFrame
        df = pd.DataFrame(datos_indice)
        df.index = pd.to_datetime(df.index)
        
        # Calcular simulación
        resultado = simulation.calcular_valor_inversion(
            df, fecha_inversion, cantidad, nombre_indice
        )
        
        # Obtener evolución
        df_evolucion = simulation.obtener_evolucion_inversion(
            df, fecha_inversion, cantidad
        )
        
        # Crear gráfico
        fig = visualization.grafico_evolucion_inversion(df_evolucion, nombre_indice)
        
        # Formatear resultados
        color_retorno = "success" if resultado['retorno_porcentual'] >= 0 else "danger"
        icono = "📈" if resultado['retorno_porcentual'] >= 0 else "📉"
        
        resultados_html = [
            html.H4(f"{icono} Resultados de la Simulación", className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.P("Valor Actual:", className="mb-1"),
                    html.H3(f"€{resultado['valor_actual']:,.2f}", className="text-primary")
                ], md=4),
                dbc.Col([
                    html.P("Ganancia/Pérdida:", className="mb-1"),
                    html.H3([
                        resultado['ganancia_perdida'] >= 0 and "+" or "",
                        f"€{resultado['ganancia_perdida']:,.2f}"
                    ], className=f"text-{color_retorno}")
                ], md=4),
                dbc.Col([
                    html.P("Retorno:", className="mb-1"),
                    html.H3(f"{resultado['retorno_porcentual']:.2f}%", 
                           className=f"text-{color_retorno}")
                ], md=4)
            ]),
            html.Hr(),
            html.P([
                html.Strong("Fecha de inversión: "), resultado['fecha_inversion'],
                html.Br(),
                html.Strong("Precio de compra: "), f"€{resultado['precio_compra']:,.2f}",
                html.Br(),
                html.Strong("Precio actual: "), f"€{resultado['precio_actual']:,.2f}",
                html.Br(),
                html.Strong("Fecha actual: "), resultado['fecha_actual']
            ])
        ]
        
        return resultados_html, resultado, fig
        
    except Exception as e:
        return f"Error: {str(e)}", None, {}


@app.callback(
    Output('prediccion-ml', 'children'),
    [Input('store-datos-indice', 'data'),
     Input('dropdown-indice', 'value')]
)
def mostrar_prediccion_ml(datos_indice, nombre_indice):
    """Muestra la predicción del modelo ML"""
    if datos_indice is None or nombre_indice is None:
        return "Carga datos del índice para ver la predicción ML"
    
    try:
        df = pd.DataFrame(datos_indice)
        df.index = pd.to_datetime(df.index)
        
        resultado_ml = ml_models.entrenar_y_predecir_indice(df, nombre_indice)
        
        retorno_pred = resultado_ml['retorno_predicho']
        if retorno_pred is not None:
            color = "success" if retorno_pred >= 0 else "danger"
            icono = "📈" if retorno_pred >= 0 else "📉"
            
            return [
                html.H5(f"{icono} Predicción del Modelo ML"),
                html.P([
                    html.Strong("Retorno estimado para el próximo mes: "),
                    html.Span(f"{retorno_pred*100:.2f}%", className=f"text-{color}")
                ]),
                html.P([
                    html.Strong("Métricas del modelo:"),
                    html.Br(),
                    f"RMSE: {resultado_ml['metricas']['RMSE']:.4f}",
                    html.Br(),
                    f"MAE: {resultado_ml['metricas']['MAE']:.4f}"
                ], className="text-muted small")
            ]
        else:
            return "No se pudo generar la predicción ML"
            
    except Exception as e:
        return f"Error en predicción ML: {str(e)}"


if __name__ == '__main__':
    app.run_server(debug=True, port=8050)

