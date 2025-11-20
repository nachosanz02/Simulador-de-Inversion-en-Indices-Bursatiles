"""
Script principal para ejecutar el simulador de inversión en índices bursátiles
"""

import os
import sys

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(__file__))

from src.backend import data_collection, preprocessing
from src.frontend.app import app


def descargar_y_preprocesar_datos():
    """Descarga y preprocesa todos los datos de índices"""
    print("=" * 60)
    print("DESCARGA Y PREPROCESAMIENTO DE DATOS")
    print("=" * 60)
    
    # Descargar datos
    datos_raw = data_collection.descargar_todos_indices(guardar=True)
    
    # Preprocesar datos
    datos_procesados = preprocessing.preprocesar_todos_indices(datos_raw, guardar=True)
    
    print("\n" + "=" * 60)
    print("PROCESO COMPLETADO")
    print("=" * 60)
    print(f"Índices procesados: {len(datos_procesados)}")
    
    return datos_procesados


def ejecutar_dashboard():
    """Ejecuta la aplicación Dash"""
    print("\n" + "=" * 60)
    print("INICIANDO DASHBOARD")
    print("=" * 60)
    print("Abre tu navegador en: http://127.0.0.1:8050")
    print("Presiona Ctrl+C para detener el servidor")
    print("=" * 60 + "\n")
    
<<<<<<< HEAD
    app.run(debug=True, host='127.0.0.1', port=8050)
=======
    app.run_server(debug=True, host='127.0.0.1', port=8050)
>>>>>>> 41a77c7b8e0fea3b9dd2af8b141f08f9f0475d9f


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Simulador de Inversión en Índices Bursátiles')
    parser.add_argument('--descargar', action='store_true', 
                       help='Descarga y preprocesa los datos de índices')
    parser.add_argument('--dashboard', action='store_true',
                       help='Ejecuta el dashboard interactivo')
    
    args = parser.parse_args()
    
    if args.descargar:
        descargar_y_preprocesar_datos()
    elif args.dashboard:
        ejecutar_dashboard()
    else:
        # Por defecto, ejecutar dashboard
        ejecutar_dashboard()

