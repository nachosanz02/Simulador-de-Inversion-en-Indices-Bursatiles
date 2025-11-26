"""
Módulo para la recopilación de datos históricos de índices bursátiles
desde Yahoo Finance
"""

import yfinance as yf
import pandas as pd
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

# Divisas de cada índice
DIVISAS = {
    'S&P 500': 'USD',
    'FTSE 100': 'GBP',
    'IBEX 35': 'EUR',
    'FTSE MIB': 'EUR',
    'CAC 40': 'EUR',
    'DAX 40': 'EUR'
}


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


def descargar_tipo_cambio(par_divisas: str, fecha_inicio: str = None, fecha_fin: str = None) -> pd.Series:
    """
    Descarga tipo de cambio histórico desde Yahoo Finance
    
    Args:
        par_divisas: Par de divisas en formato 'EURUSD' o 'EURGBP'
        fecha_inicio: Fecha de inicio en formato 'YYYY-MM-DD'
        fecha_fin: Fecha de fin en formato 'YYYY-MM-DD'
    
    Returns:
        Series con los tipos de cambio históricos (Close), con índice sin timezone
    """
    # Yahoo Finance usa el formato 'EURUSD=X' para pares de divisas
    simbolo = f"{par_divisas}=X"
    
    try:
        ticker = yf.Ticker(simbolo)
        
        if fecha_inicio is None:
            datos = ticker.history(period="max")
        else:
            datos = ticker.history(start=fecha_inicio, end=fecha_fin)
        
        if not datos.empty:
            # Asegurar que el índice no tenga timezone
            if datos.index.tz is not None:
                datos.index = datos.index.tz_localize(None)
            
            return datos['Close']
        else:
            # Intentar con formato alternativo si el primero falla
            print(f"No se encontraron datos para {simbolo}, intentando formato alternativo...")
            return pd.Series(dtype=float)
    except Exception as e:
        print(f"Error descargando tipo de cambio {par_divisas} ({simbolo}): {str(e)}")
        # Intentar con símbolos alternativos
        simbolos_alternativos = {
            'EURUSD': ['EURUSD=X', 'EUR=X', 'EURUSD'],
            'EURGBP': ['EURGBP=X', 'EURGBP'],
            'USD': ['EURUSD=X'],  # Para USD, usamos EURUSD y luego invertimos
            'GBP': ['EURGBP=X']   # Para GBP, usamos EURGBP y luego invertimos
        }
        
        if par_divisas in simbolos_alternativos:
            for simbolo_alt in simbolos_alternativos[par_divisas]:
                try:
                    ticker = yf.Ticker(simbolo_alt)
                    if fecha_inicio is None:
                        datos = ticker.history(period="max")
                    else:
                        datos = ticker.history(start=fecha_inicio, end=fecha_fin)
                    
                    if not datos.empty:
                        if datos.index.tz is not None:
                            datos.index = datos.index.tz_localize(None)
                        return datos['Close']
                except:
                    continue
        
        return pd.Series(dtype=float)


def obtener_tipos_cambio_eur(fecha_inicio: str = None, fecha_fin: str = None) -> dict:
    """
    Obtiene tipos de cambio históricos para convertir a EUR
    
    Args:
        fecha_inicio: Fecha de inicio en formato 'YYYY-MM-DD'
        fecha_fin: Fecha de fin en formato 'YYYY-MM-DD'
    
    Returns:
        Diccionario con tipos de cambio:
        - 'EURUSD': cuántos USD por 1 EUR (Series)
        - 'EURGBP': cuántos GBP por 1 EUR (Series)
    """
    tipos_cambio = {}
    
    # Intentar descargar EUR/USD (cuántos USD por 1 EUR)
    try:
        ticker = yf.Ticker('EURUSD=X')
        if fecha_inicio is None:
            datos = ticker.history(period="max")
        else:
            datos = ticker.history(start=fecha_inicio, end=fecha_fin)
        
        if not datos.empty:
            if datos.index.tz is not None:
                datos.index = datos.index.tz_localize(None)
            tipos_cambio['EURUSD'] = datos['Close']
    except Exception as e:
        # Si falla, intentar con el método inverso
        try:
            ticker = yf.Ticker('USDEUR=X')
            if fecha_inicio is None:
                datos = ticker.history(period="max")
            else:
                datos = ticker.history(start=fecha_inicio, end=fecha_fin)
            
            if not datos.empty:
                if datos.index.tz is not None:
                    datos.index = datos.index.tz_localize(None)
                # Invertir: si USDEUR = X, entonces EURUSD = 1/X
                tipos_cambio['EURUSD'] = 1 / datos['Close']
        except:
            pass
    
    # Intentar descargar EUR/GBP (cuántos GBP por 1 EUR)
    try:
        ticker = yf.Ticker('EURGBP=X')
        if fecha_inicio is None:
            datos = ticker.history(period="max")
        else:
            datos = ticker.history(start=fecha_inicio, end=fecha_fin)
        
        if not datos.empty:
            if datos.index.tz is not None:
                datos.index = datos.index.tz_localize(None)
            tipos_cambio['EURGBP'] = datos['Close']
    except Exception as e:
        # Si falla, intentar con el método inverso
        try:
            ticker = yf.Ticker('GBPEUR=X')
            if fecha_inicio is None:
                datos = ticker.history(period="max")
            else:
                datos = ticker.history(start=fecha_inicio, end=fecha_fin)
            
            if not datos.empty:
                if datos.index.tz is not None:
                    datos.index = datos.index.tz_localize(None)
                # Invertir: si GBPEUR = X, entonces EURGBP = 1/X
                tipos_cambio['EURGBP'] = 1 / datos['Close']
        except:
            pass
    
    return tipos_cambio


if __name__ == "__main__":
    # Ejemplo de uso: descargar todos los índices
    datos = descargar_todos_indices()
    print("\nDatos descargados exitosamente!")

