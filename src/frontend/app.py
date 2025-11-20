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

<<<<<<< HEAD
from src.backend import data_collection, preprocessing, simulation, visualization, ml_models, analisis_tecnico, inversion_periodica, utils
=======
from src.backend import data_collection, preprocessing, simulation, visualization, ml_models
>>>>>>> 41a77c7b8e0fea3b9dd2af8b141f08f9f0475d9f


# Inicializar la aplicación Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Simulador de Inversión en Índices Bursátiles"

# Índices disponibles
INDICES_DISPONIBLES = list(data_collection.INDICES.keys())


# Layout de la aplicación
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
<<<<<<< HEAD
            html.Div([
                html.H1("📈 Simulador de Inversión en Índices Bursátiles", 
                       className="text-center mb-3"),
                html.P("Simula inversiones pasadas y futuras en los principales índices bursátiles internacionales",
                      className="text-center text-muted mb-2"),
                dbc.Badge("S&P 500 (USD) • FTSE 100 (GBP) • IBEX 35 (EUR) • FTSE MIB (EUR) • CAC 40 (EUR) • DAX 40 (EUR)", 
                         color="info", className="mb-3"),
                dbc.Alert([
                    html.I(className="bi bi-info-circle me-2"),
                    html.Strong("Nota: "),
                    "Los índices se muestran en su divisa original. El S&P 500 está en USD y el FTSE 100 en GBP."
                ], color="info", className="mb-4")
            ], className="mb-4")
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
                            html.Label("Cantidad invertida:"),
                            dcc.Input(
                                id='input-cantidad',
                                type='number',
                                value=1000,
                                min=1,
                                className="form-control mb-2"
                            ),
                            html.Small(id='label-divisa-cantidad', className="text-muted mb-3 d-block"),
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
            ], className="mt-4"),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='grafico-prophet', figure={})
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
                            html.Label("Cantidad mensual:"),
                            dcc.Input(
                                id='input-cantidad-mensual',
                                type='number',
                                value=200,
                                min=1,
                                className="form-control mb-2"
                            ),
                            html.Small(id='label-divisa-mensual', className="text-muted mb-3 d-block"),
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
=======
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
>>>>>>> 41a77c7b8e0fea3b9dd2af8b141f08f9f0475d9f
    
], fluid=True)


<<<<<<< HEAD
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


# Callback para actualizar etiqueta de divisa en simulación
@app.callback(
    Output('label-divisa-cantidad', 'children'),
    Input('dropdown-indice', 'value')
)
def actualizar_label_divisa_cantidad(nombre_indice):
    if nombre_indice is None:
        return ""
    info_divisa = utils.obtener_info_divisa_indice(nombre_indice)
    return f"Divisa del índice: {info_divisa['nombre']} ({info_divisa['codigo']})"


# Callback para actualizar etiqueta de divisa en inversión periódica
@app.callback(
    Output('label-divisa-mensual', 'children'),
    Input('dropdown-indice-periodica', 'value')
)
def actualizar_label_divisa_mensual(nombre_indice):
    if nombre_indice is None:
        return ""
    info_divisa = utils.obtener_info_divisa_indice(nombre_indice)
    return f"Divisa del índice: {info_divisa['nombre']} ({info_divisa['codigo']})"


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
            
            # Obtener información de divisa
            info_divisa = utils.obtener_info_divisa_indice(nombre_indice)
            simbolo_divisa = info_divisa['simbolo']
            divisa = info_divisa['codigo']
            
            analisis_html.append(
                dbc.Card([
                    dbc.CardHeader([
                        f"{icono} {nombre_indice} ",
                        dbc.Badge(divisa, color="info", className="ms-2")
                    ]),
                    dbc.CardBody([
                        html.H5(f"Señal: {analisis['señal']}", className=f"text-{color_señal}"),
                        html.P(analisis['recomendacion']),
                        html.P([
                            html.Strong("RSI: "), f"{analisis['rsi']:.2f}",
                            html.Br(),
                            html.Strong("Precio actual: "), f"{simbolo_divisa}{analisis['precio_actual']:,.2f} ({divisa})",
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
=======
# Callbacks
>>>>>>> 41a77c7b8e0fea3b9dd2af8b141f08f9f0475d9f
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
<<<<<<< HEAD
        df = preprocessing.cargar_datos_procesados(nombre_indice)
        fig = visualization.grafico_evolucion_indice(df, nombre_indice)
        df_con_indice = df.reset_index()
        return df_con_indice.to_dict('records'), fig
    except FileNotFoundError:
=======
        # Intentar cargar datos procesados
        df = preprocessing.cargar_datos_procesados(nombre_indice)
        fig = visualization.grafico_evolucion_indice(df, nombre_indice)
        return df.to_dict('records'), fig
    except FileNotFoundError:
        # Si no existen datos procesados, intentar descargar
>>>>>>> 41a77c7b8e0fea3b9dd2af8b141f08f9f0475d9f
        try:
            simbolo = data_collection.INDICES[nombre_indice]
            df = data_collection.descargar_indice(simbolo)
            df = preprocessing.limpiar_datos(df, nombre_indice)
            fig = visualization.grafico_evolucion_indice(df, nombre_indice)
<<<<<<< HEAD
            df_con_indice = df.reset_index()
            return df_con_indice.to_dict('records'), fig
        except Exception as e:
            return None, {'data': [], 'layout': {'title': f'Error: {str(e)}'}}
=======
            return df.to_dict('records'), fig
        except Exception as e:
            return None, {
                'data': [],
                'layout': {'title': f'Error: {str(e)}'}
            }
>>>>>>> 41a77c7b8e0fea3b9dd2af8b141f08f9f0475d9f


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
<<<<<<< HEAD
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
        
        # Obtener información de divisa
        info_divisa = utils.obtener_info_divisa_indice(nombre_indice)
        divisa = info_divisa['codigo']
        simbolo_divisa = info_divisa['simbolo']
        
        resultado = simulation.calcular_valor_inversion(df, fecha_inversion, cantidad, nombre_indice)
        df_evolucion = simulation.obtener_evolucion_inversion(df, fecha_inversion, cantidad)
        fig = visualization.grafico_evolucion_inversion(df_evolucion, nombre_indice, divisa)
        
        color_retorno = "success" if resultado['retorno_porcentual'] >= 0 else "danger"
        icono = "📈" if resultado['retorno_porcentual'] >= 0 else "📉"
        
        # Advertencia si la divisa no es EUR
        advertencia_divisa = None
        if divisa != 'EUR':
            advertencia_divisa = dbc.Alert([
                html.Strong("⚠️ Nota sobre divisas: "),
                f"El {nombre_indice} cotiza en {info_divisa['nombre']} ({divisa}). ",
                "Los valores mostrados están en la divisa del índice. ",
                "Si invertiste en euros, ten en cuenta que también hay riesgo de cambio de divisa."
            ], color="warning", className="mb-3")
        
        resultados_html = [
            html.H4(f"{icono} Resultados de la Simulación", className="mb-3"),
            advertencia_divisa,
            dbc.Row([
                dbc.Col([
                    html.P("Valor Actual:", className="mb-1"),
                    html.H3(f"{simbolo_divisa}{resultado['valor_actual']:,.2f}", className="text-primary"),
                    html.Small(f"({divisa})", className="text-muted")
=======
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
>>>>>>> 41a77c7b8e0fea3b9dd2af8b141f08f9f0475d9f
                ], md=4),
                dbc.Col([
                    html.P("Ganancia/Pérdida:", className="mb-1"),
                    html.H3([
                        resultado['ganancia_perdida'] >= 0 and "+" or "",
<<<<<<< HEAD
                        f"{simbolo_divisa}{resultado['ganancia_perdida']:,.2f}"
                    ], className=f"text-{color_retorno}"),
                    html.Small(f"({divisa})", className="text-muted")
=======
                        f"€{resultado['ganancia_perdida']:,.2f}"
                    ], className=f"text-{color_retorno}")
>>>>>>> 41a77c7b8e0fea3b9dd2af8b141f08f9f0475d9f
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
<<<<<<< HEAD
                html.Strong("Precio de compra: "), f"{simbolo_divisa}{resultado['precio_compra']:,.2f} ({divisa})",
                html.Br(),
                html.Strong("Precio actual: "), f"{simbolo_divisa}{resultado['precio_actual']:,.2f} ({divisa})",
=======
                html.Strong("Precio de compra: "), f"€{resultado['precio_compra']:,.2f}",
                html.Br(),
                html.Strong("Precio actual: "), f"€{resultado['precio_actual']:,.2f}",
>>>>>>> 41a77c7b8e0fea3b9dd2af8b141f08f9f0475d9f
                html.Br(),
                html.Strong("Fecha actual: "), resultado['fecha_actual']
            ])
        ]
        
        return resultados_html, resultado, fig
        
    except Exception as e:
        return f"Error: {str(e)}", None, {}


@app.callback(
<<<<<<< HEAD
    [Output('prediccion-ml', 'children'),
     Output('grafico-prophet', 'figure')],
=======
    Output('prediccion-ml', 'children'),
>>>>>>> 41a77c7b8e0fea3b9dd2af8b141f08f9f0475d9f
    [Input('store-datos-indice', 'data'),
     Input('dropdown-indice', 'value')]
)
def mostrar_prediccion_ml(datos_indice, nombre_indice):
    """Muestra la predicción del modelo ML"""
    if datos_indice is None or nombre_indice is None:
<<<<<<< HEAD
        return "Carga datos del índice para ver la predicción ML", {}
    
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
        
        # Entrenar ambos modelos (Ridge y Prophet)
        resultados_ml = ml_models.entrenar_ridge_y_prophet(df, nombre_indice)
        
        contenido = []
        
        # Resultados de Ridge
        if 'ridge' in resultados_ml and 'retorno_predicho' in resultados_ml['ridge']:
            resultado_ridge = resultados_ml['ridge']
            retorno_pred = resultado_ridge['retorno_predicho']
            if retorno_pred is not None:
                color = "success" if retorno_pred >= 0 else "danger"
                icono = "📈" if retorno_pred >= 0 else "📉"
                
                contenido.append(
                    html.Div([
                        html.H5(f"{icono} Predicción Ridge (Retornos)"),
                        html.P([
                            html.Strong("Retorno estimado para el próximo mes: "),
                            html.Span(f"{retorno_pred*100:.2f}%", className=f"text-{color}")
                        ]),
                        html.P([
                            html.Strong("Métricas:"),
                            html.Br(),
                            f"RMSE: {resultado_ridge['metricas']['RMSE']:.4f}",
                            html.Br(),
                            f"MAE: {resultado_ridge['metricas']['MAE']:.4f}"
                        ], className="text-muted small")
                    ], className="mb-4")
                )
        
        # Resultados de Prophet
        if 'prophet' in resultados_ml and 'retorno_predicho_30d' in resultados_ml['prophet']:
            resultado_prophet = resultados_ml['prophet']
            retorno_prophet = resultado_prophet['retorno_predicho_30d']
            if retorno_prophet is not None:
                color = "success" if retorno_prophet >= 0 else "danger"
                icono = "📈" if retorno_prophet >= 0 else "📉"
                
                contenido.append(
                    html.Div([
                        html.H5(f"{icono} Predicción Prophet (Precios)"),
                        html.P([
                            html.Strong("Precio actual: "), f"€{resultado_prophet['precio_actual']:,.2f}",
                            html.Br(),
                            html.Strong("Precio predicho (30 días): "), f"€{resultado_prophet['precio_predicho_30d']:,.2f}",
                            html.Br(),
                            html.Strong("Retorno estimado (30 días): "),
                            html.Span(f"{retorno_prophet*100:.2f}%", className=f"text-{color}")
                        ]),
                        html.P([
                            html.Strong("Métricas:"),
                            html.Br(),
                            f"RMSE: {resultado_prophet['metricas']['RMSE']:.4f}" if resultado_prophet['metricas']['RMSE'] else "RMSE: N/A",
                            html.Br(),
                            f"MAE: {resultado_prophet['metricas']['MAE']:.4f}" if resultado_prophet['metricas']['MAE'] else "MAE: N/A"
                        ], className="text-muted small")
                    ])
                )
        elif 'prophet' in resultados_ml and 'error' in resultados_ml['prophet']:
            contenido.append(
                html.Div([
                    html.P(f"⚠ Prophet: {resultados_ml['prophet']['error']}", className="text-warning small")
                ])
            )
        
        # Crear gráfico de Prophet si está disponible
        figura_prophet = {}
        if 'prophet' in resultados_ml and 'error' not in resultados_ml['prophet']:
            try:
                figura_prophet = visualization.grafico_prophet_prediccion(
                    resultados_ml['prophet'], nombre_indice
                )
            except Exception as e:
                figura_prophet = {'data': [], 'layout': {'title': f'Error en gráfico Prophet: {str(e)}'}}
        
        if contenido:
            return contenido, figura_prophet
        else:
            return "No se pudo generar la predicción ML", figura_prophet
            
    except Exception as e:
        return f"Error en predicción ML: {str(e)}", {}


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
        
        # Obtener años de historia analizados
        años_historia_usados = resultado.get('años_historia_analizados', 10)
        volatilidad_anual = resultado.get('volatilidad_anual', 0)
        
        # Obtener información de divisa
        info_divisa = utils.obtener_info_divisa_indice(nombre_indice)
        divisa = info_divisa['codigo']
        simbolo_divisa = info_divisa['simbolo']
        
        # Advertencia si la divisa no es EUR
        advertencia_divisa = None
        if divisa != 'EUR':
            advertencia_divisa = dbc.Alert([
                html.Strong("⚠️ Nota sobre divisas: "),
                f"El {nombre_indice} cotiza en {info_divisa['nombre']} ({divisa}). ",
                "Los valores mostrados están en la divisa del índice. ",
                "Si inviertes en euros, ten en cuenta que también hay riesgo de cambio de divisa."
            ], color="warning", className="mb-3")
        
        resultados_html = [
            html.H4("📊 Resultados de la Proyección", className="mb-3"),
            advertencia_divisa,
            dbc.Row([
                dbc.Col([
                    html.P("Valor Proyectado:", className="mb-1"),
                    html.H3(f"{simbolo_divisa}{resultado['valor_final']:,.2f}", className="text-success"),
                    html.Small(f"({divisa})", className="text-muted")
                ], md=4),
                dbc.Col([
                    html.P("Tu Contribución:", className="mb-1"),
                    html.H3(f"{simbolo_divisa}{resultado['total_invertido']:,.2f}", className="text-primary"),
                    html.Small(f"({divisa})", className="text-muted")
                ], md=4),
                dbc.Col([
                    html.P("Ganancia Proyectada:", className="mb-1"),
                    html.H3(f"{simbolo_divisa}{resultado['ganancia_total']:,.2f}", 
                           className=f"text-{color}"),
                    html.Small(f"({divisa})", className="text-muted")
                ], md=4)
            ]),
            html.Hr(),
            html.P([
                html.Strong("Retorno total: "), f"{resultado['retorno_total']:.2f}%",
                html.Br(),
                html.Strong("Retorno anual promedio: "), f"{resultado['retorno_anual_promedio']:.2f}%",
                html.Br(),
                html.Strong("Período: "), f"{resultado['fecha_inicio']} a {resultado['fecha_fin_proyectada']}"
            ]),
            html.Hr(),
            dbc.Alert([
                html.H6("ℹ️ Sobre el Rango de Incertidumbre", className="mb-2"),
                html.P([
                    f"Basado en el análisis de los últimos {años_historia_usados:.1f} años, ",
                    f"el {resultado['nombre_indice']} ha tenido una volatilidad anual promedio del ",
                    html.Strong(f"{volatilidad_anual:.2f}%"),
                    ". ",
                    "El área sombreada en el gráfico muestra el rango de posibles valores (68% de confianza) basado en esta volatilidad histórica. ",
                    html.Br(),
                    html.Small([
                        "Nota: La banda inferior es más pequeña (0.7x) porque los valores no pueden ser negativos, ",
                        "mientras que la banda superior es más amplia (1.3x) ya que el crecimiento potencial es ilimitado."
                    ], className="text-muted")
                ])
            ], color="info", className="mt-3")
        ]
        
        return resultados_html, fig
        
    except Exception as e:
        return f"Error: {str(e)}", {}


if __name__ == '__main__':
    app.run(debug=True, port=8050)
=======
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

>>>>>>> 41a77c7b8e0fea3b9dd2af8b141f08f9f0475d9f
