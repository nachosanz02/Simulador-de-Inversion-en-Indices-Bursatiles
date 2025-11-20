"""
Módulo para la recopilación de datos históricos de índices bursátiles
desde Yahoo Finance
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
import os


# Símbolos de los índices en Yahoo Finance
INDICES = {
    'S&P 500': '^GSPC',
    'FTSE 100': '^FTSE',
    'IBEX 35': '^IBEX',
    'FTSE MIB': 'FTSEMIB.MI',
    'CAC 40': '^FCHI',
    'DAX 40': '^GDAXI'
}

<<<<<<< HEAD
# Divisas de cada índice
DIVISAS = {
    'S&P 500': 'USD',
    'FTSE 100': 'GBP',
    'IBEX 35': 'EUR',
    'FTSE MIB': 'EUR',
    'CAC 40': 'EUR',
    'DAX 40': 'EUR'
}

=======
>>>>>>> 41a77c7b8e0fea3b9dd2af8b141f08f9f0475d9f

def descargar_indice(simbolo: str, fecha_inicio: str = None, fecha_fin: str = None) -> pd.DataFrame:
    """
    Descarga datos históricos de un índice bursátil desde Yahoo Finance
    
    Args:
        simbolo: Símbolo del índice en Yahoo Finance (ej: '^GSPC' para S&P 500)
        fecha_inicio: Fecha de inicio en formato 'YYYY-MM-DD'. Si es None, descarga desde el inicio disponible
        fecha_fin: Fecha de fin en formato 'YYYY-MM-DD'. Si es None, usa la fecha actual
    
    Returns:
        DataFrame con los datos históricos del índice
    """
    ticker = yf.Ticker(simbolo)
    
    if fecha_inicio is None:
        # Descargar desde el inicio disponible
        datos = ticker.history(period="max")
    else:
        datos = ticker.history(start=fecha_inicio, end=fecha_fin)
    
    return datos


def descargar_todos_indices(fecha_inicio: str = None, fecha_fin: str = None, 
                           guardar: bool = True) -> dict:
    """
    Descarga datos históricos de todos los índices definidos
    
    Args:
        fecha_inicio: Fecha de inicio en formato 'YYYY-MM-DD'
        fecha_fin: Fecha de fin en formato 'YYYY-MM-DD'
        guardar: Si es True, guarda los datos en archivos CSV en data/raw/
    
    Returns:
        Diccionario con los nombres de los índices como claves y DataFrames como valores
    """
    datos_indices = {}
    
    print("Descargando datos históricos de índices bursátiles...")
    
    for nombre_indice, simbolo in INDICES.items():
        try:
            print(f"Descargando {nombre_indice} ({simbolo})...")
            datos = descargar_indice(simbolo, fecha_inicio, fecha_fin)
            
            if not datos.empty:
                datos_indices[nombre_indice] = datos
                print(f"✓ {nombre_indice}: {len(datos)} registros descargados")
                
                # Guardar en CSV si se solicita
                if guardar:
                    ruta_raw = os.path.join('data', 'raw')
                    os.makedirs(ruta_raw, exist_ok=True)
                    nombre_archivo = f"{nombre_indice.replace(' ', '_').replace('&', '')}.csv"
                    ruta_completa = os.path.join(ruta_raw, nombre_archivo)
                    datos.to_csv(ruta_completa)
                    print(f"  Guardado en: {ruta_completa}")
            else:
                print(f"⚠ {nombre_indice}: No se pudieron descargar datos")
                
        except Exception as e:
            print(f"✗ Error descargando {nombre_indice}: {str(e)}")
    
    print(f"\nTotal de índices descargados: {len(datos_indices)}/{len(INDICES)}")
    return datos_indices


def cargar_datos_desde_csv(nombre_indice: str) -> pd.DataFrame:
    """
    Carga datos de un índice desde un archivo CSV en data/raw/
    
    Args:
        nombre_indice: Nombre del índice (ej: 'S&P 500')
    
    Returns:
        DataFrame con los datos históricos
    """
    nombre_archivo = f"{nombre_indice.replace(' ', '_').replace('&', '')}.csv"
    ruta = os.path.join('data', 'raw', nombre_archivo)
    
    if os.path.exists(ruta):
        datos = pd.read_csv(ruta, index_col=0, parse_dates=True)
        return datos
    else:
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")


if __name__ == "__main__":
    # Ejemplo de uso: descargar todos los índices
    datos = descargar_todos_indices()
    print("\nDatos descargados exitosamente!")

