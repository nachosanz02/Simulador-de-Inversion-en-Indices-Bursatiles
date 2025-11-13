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

from src.backend import data_collection, preprocessing, simulation, visualization, ml_models, analisis_tecnico, inversion_periodica


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
            html.P("Simula inversiones pasadas y futuras en los principales índices bursátiles internacionales",
                  className="text-center text-muted mb-4")
        ])
    ]),
    
    # Tabs para diferentes secciones
    dbc.Tabs([
        dbc.Tab(label="Comparación de Índices", tab_id="tab-comparacion"),
        dbc.Tab(label="Simulación de Inversión", tab_id="tab-simulacion"),
        dbc.Tab(label="Inversión Periódica", tab_id="tab-periodica"),
    ], id="tabs", active_tab="tab-comparacion"),
    
    # Todos los componentes deben estar en el layout inicial (ocultos si no están activos)
    html.Div([
        # Componentes de comparación
        html.Div(id="div-comparacion", children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Selección de Índices"),
                        dbc.CardBody([
                            html.Label("Selecciona los índices a comparar (múltiple selección):"),
                            dcc.Dropdown(
                                id='dropdown-indices-multi',
                                options=[{'label': idx, 'value': idx} for idx in INDICES_DISPONIBLES],
                                value=[INDICES_DISPONIBLES[0]] if INDICES_DISPONIBLES else [],
                                multi=True,
                                className="mb-3"
                            ),
                            dbc.Button("Cargar Índices", id='btn-cargar-indices', 
                                      color="primary", className="w-100")
                        ])
                    ], className="mb-4")
                ], md=12)
            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='grafico-comparacion-multi', figure={})
                ], md=12)
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Análisis Técnico - Señales de Compra/Venta"),
                        dbc.CardBody(id='analisis-tecnico', children="Selecciona índices y haz clic en 'Cargar Índices'")
                    ])
                ], md=12)
            ], className="mt-4")
        ]),
        
        # Componentes de simulación
        html.Div(id="div-simulacion", style={'display': 'none'}, children=[
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
                        dbc.CardBody(id='resultados-simulacion', children="Ingresa los parámetros y haz clic en 'Calcular Simulación'")
                    ], className="mb-4")
                ], md=8)
            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='grafico-evolucion-indice', figure={})
                ], md=6),
                dbc.Col([
                    dcc.Graph(id='grafico-evolucion-inversion', figure={})
                ], md=6)
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Predicción ML"),
                        dbc.CardBody(id='prediccion-ml', children="Carga datos del índice para ver la predicción ML")
                    ])
                ], md=12)
            ], className="mt-4")
        ]),
        
        # Componentes de inversión periódica
        html.Div(id="div-periodica", style={'display': 'none'}, children=[
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Parámetros de Inversión Periódica"),
                        dbc.CardBody([
                            html.Label("Selecciona el índice:"),
                            dcc.Dropdown(
                                id='dropdown-indice-periodica',
                                options=[{'label': idx, 'value': idx} for idx in INDICES_DISPONIBLES],
                                value=INDICES_DISPONIBLES[0] if INDICES_DISPONIBLES else None,
                                className="mb-3"
                            ),
                            html.Label("Cantidad mensual (€):"),
                            dcc.Input(
                                id='input-cantidad-mensual',
                                type='number',
                                value=200,
                                min=1,
                                className="form-control mb-3"
                            ),
                            html.Label("Años de inversión:"),
                            dcc.Slider(
                                id='slider-anos',
                                min=1,
                                max=30,
                                step=1,
                                value=20,
                                marks={i: str(i) for i in range(0, 31, 5)},
                                className="mb-3"
                            ),
                            html.Div(id='display-anos', className="mb-3"),
                            dbc.Button("Calcular Proyección", id='btn-calcular-periodica', 
                                      color="primary", className="w-100")
                        ])
                    ], className="mb-4")
                ], md=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Resultados de la Proyección"),
                        dbc.CardBody(id='resultados-periodica', children="Ingresa los parámetros y haz clic en 'Calcular Proyección'")
                    ], className="mb-4")
                ], md=8)
            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='grafico-inversion-periodica', figure={})
                ], md=12)
            ])
        ])
    ]),
    
    # Almacenamiento para datos
    dcc.Store(id='store-datos-indices', data={}),
    dcc.Store(id='store-datos-indice', data=None),
    dcc.Store(id='store-resultado-simulacion', data=None)
    
], fluid=True)


# Callback para cambiar tabs - mostrar/ocultar divs
@app.callback(
    [Output('div-comparacion', 'style'),
     Output('div-simulacion', 'style'),
     Output('div-periodica', 'style')],
    Input('tabs', 'active_tab')
)
def render_tab_content(active_tab):
    if active_tab == "tab-comparacion":
        return {'display': 'block'}, {'display': 'none'}, {'display': 'none'}
    elif active_tab == "tab-simulacion":
        return {'display': 'none'}, {'display': 'block'}, {'display': 'none'}
    elif active_tab == "tab-periodica":
        return {'display': 'none'}, {'display': 'none'}, {'display': 'block'}
    return {'display': 'block'}, {'display': 'none'}, {'display': 'none'}


# Callback para mostrar años seleccionados
@app.callback(
    Output('display-anos', 'children'),
    Input('slider-anos', 'value')
)
def display_anos(value):
    return html.P(f"Años seleccionados: {value}", className="text-center")


# Callback para cargar múltiples índices
@app.callback(
    [Output('store-datos-indices', 'data'),
     Output('grafico-comparacion-multi', 'figure'),
     Output('analisis-tecnico', 'children')],
    [Input('btn-cargar-indices', 'n_clicks')],
    [State('dropdown-indices-multi', 'value')]
)
def cargar_indices_multiples(n_clicks, indices_seleccionados):
    if n_clicks is None or not indices_seleccionados:
        return {}, {}, "Selecciona al menos un índice y haz clic en 'Cargar Índices'"
    
    datos_indices = {}
    analisis_html = []
    
    try:
        for nombre_indice in indices_seleccionados:
            try:
                df = preprocessing.cargar_datos_procesados(nombre_indice)
            except FileNotFoundError:
                simbolo = data_collection.INDICES[nombre_indice]
                df = data_collection.descargar_indice(simbolo)
                df = preprocessing.limpiar_datos(df, nombre_indice)
            
            datos_indices[nombre_indice] = df
            
            # Análisis técnico para cada índice
            analisis = analisis_tecnico.calcular_indicadores_compra_venta(df)
            
            color_señal = "success" if analisis['señal'] == 'COMPRA' else "danger" if analisis['señal'] == 'VENTA' else "warning"
            icono = "🟢" if analisis['señal'] == 'COMPRA' else "🔴" if analisis['señal'] == 'VENTA' else "🟡"
            
            analisis_html.append(
                dbc.Card([
                    dbc.CardHeader(f"{icono} {nombre_indice}"),
                    dbc.CardBody([
                        html.H5(f"Señal: {analisis['señal']}", className=f"text-{color_señal}"),
                        html.P(analisis['recomendacion']),
                        html.P([
                            html.Strong("RSI: "), f"{analisis['rsi']:.2f}",
                            html.Br(),
                            html.Strong("Precio actual: "), f"€{analisis['precio_actual']:,.2f}",
                            html.Br(),
                            html.Strong("Volatilidad anual: "), f"{analisis['volatilidad']:.2f}%"
                        ], className="small")
                    ])
                ], className="mb-3")
            )
        
        # Crear gráfico comparativo
        fig = visualization.grafico_comparacion_indices_multiple(datos_indices, indices_seleccionados)
        
        # Guardar datos en formato serializable
        datos_serializados = {}
        for nombre, df in datos_indices.items():
            df_con_indice = df.reset_index()
            datos_serializados[nombre] = df_con_indice.to_dict('records')
        
        return datos_serializados, fig, analisis_html
        
    except Exception as e:
        return {}, {'data': [], 'layout': {'title': f'Error: {str(e)}'}}, f"Error: {str(e)}"


# Callbacks para simulación de inversión (mantener los existentes)
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
        df = preprocessing.cargar_datos_procesados(nombre_indice)
        fig = visualization.grafico_evolucion_indice(df, nombre_indice)
        df_con_indice = df.reset_index()
        return df_con_indice.to_dict('records'), fig
    except FileNotFoundError:
        try:
            simbolo = data_collection.INDICES[nombre_indice]
            df = data_collection.descargar_indice(simbolo)
            df = preprocessing.limpiar_datos(df, nombre_indice)
            fig = visualization.grafico_evolucion_indice(df, nombre_indice)
            df_con_indice = df.reset_index()
            return df_con_indice.to_dict('records'), fig
        except Exception as e:
            return None, {'data': [], 'layout': {'title': f'Error: {str(e)}'}}


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
        df = pd.DataFrame(datos_indice)
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
        elif 'index' in df.columns:
            df['index'] = pd.to_datetime(df['index'])
            df.set_index('index', inplace=True)
        else:
            df.index = pd.to_datetime(df.index)
        
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)
        
        resultado = simulation.calcular_valor_inversion(df, fecha_inversion, cantidad, nombre_indice)
        df_evolucion = simulation.obtener_evolucion_inversion(df, fecha_inversion, cantidad)
        fig = visualization.grafico_evolucion_inversion(df_evolucion, nombre_indice)
        
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
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
        elif 'index' in df.columns:
            df['index'] = pd.to_datetime(df['index'])
            df.set_index('index', inplace=True)
        else:
            df.index = pd.to_datetime(df.index)
        
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)
        
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


# Callback para inversión periódica
@app.callback(
    [Output('resultados-periodica', 'children'),
     Output('grafico-inversion-periodica', 'figure')],
    [Input('btn-calcular-periodica', 'n_clicks')],
    [State('dropdown-indice-periodica', 'value'),
     State('input-cantidad-mensual', 'value'),
     State('slider-anos', 'value')]
)
def calcular_inversion_periodica(n_clicks, nombre_indice, cantidad_mensual, años):
    """Calcula la proyección de inversión periódica"""
    if n_clicks is None or nombre_indice is None or cantidad_mensual is None or años is None:
        return "Ingresa los parámetros y haz clic en 'Calcular Proyección'", {}
    
    try:
        df = preprocessing.cargar_datos_procesados(nombre_indice)
    except FileNotFoundError:
        try:
            simbolo = data_collection.INDICES[nombre_indice]
            df = data_collection.descargar_indice(simbolo)
            df = preprocessing.limpiar_datos(df, nombre_indice)
        except Exception as e:
            return f"Error cargando datos: {str(e)}", {}
    
    try:
        resultado = inversion_periodica.simular_inversion_periodica(
            df, cantidad_mensual, años, nombre_indice
        )
        
        fig = visualization.grafico_inversion_periodica(resultado)
        
        color = "success" if resultado['retorno_total'] >= 0 else "danger"
        
        resultados_html = [
            html.H4("📊 Resultados de la Proyección", className="mb-3"),
            dbc.Row([
                dbc.Col([
                    html.P("Valor Proyectado:", className="mb-1"),
                    html.H3(f"€{resultado['valor_final']:,.2f}", className="text-success")
                ], md=4),
                dbc.Col([
                    html.P("Tu Contribución:", className="mb-1"),
                    html.H3(f"€{resultado['total_invertido']:,.2f}", className="text-primary")
                ], md=4),
                dbc.Col([
                    html.P("Ganancia Proyectada:", className="mb-1"),
                    html.H3(f"€{resultado['ganancia_total']:,.2f}", 
                           className=f"text-{color}")
                ], md=4)
            ]),
            html.Hr(),
            html.P([
                html.Strong("Retorno total: "), f"{resultado['retorno_total']:.2f}%",
                html.Br(),
                html.Strong("Retorno anual promedio: "), f"{resultado['retorno_anual_promedio']:.2f}%",
                html.Br(),
                html.Strong("Período: "), f"{resultado['fecha_inicio']} a {resultado['fecha_fin']}"
            ])
        ]
        
        return resultados_html, fig
        
    except Exception as e:
        return f"Error: {str(e)}", {}


if __name__ == '__main__':
    app.run(debug=True, port=8050)
