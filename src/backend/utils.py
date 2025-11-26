"""
Utilidades generales para el proyecto
"""

from . import data_collection


def obtener_divisa_indice(nombre_indice: str) -> str:
    """
    Obtiene la divisa de un índice
    
    Args:
        nombre_indice: Nombre del índice
    
    Returns:
        Símbolo de la divisa (USD, EUR, GBP, etc.)
    """
    return data_collection.DIVISAS.get(nombre_indice, 'EUR')


def obtener_info_divisa_indice(nombre_indice: str) -> dict:
    """
    Obtiene información completa sobre la divisa de un índice
    
    Args:
        nombre_indice: Nombre del índice
    
    Returns:
        Diccionario con información de divisa
    """
    divisa = obtener_divisa_indice(nombre_indice)
    simbolo = {'USD': '$', 'EUR': '€', 'GBP': '£'}.get(divisa, divisa)
    
    return {
        'codigo': divisa,
        'simbolo': simbolo,
        'nombre': {
            'USD': 'Dólares estadounidenses',
            'EUR': 'Euros',
            'GBP': 'Libras esterlinas'
        }.get(divisa, divisa)
    }


def obtener_info_indice(nombre_indice: str) -> dict:
    """
    Obtiene información completa sobre un índice (origen, descripción, etc.)
    
    Args:
        nombre_indice: Nombre del índice
    
    Returns:
        Diccionario con información del índice
    """
    info_indices = {
        'S&P 500': {
            'pais': 'Estados Unidos',
            'descripcion': 'Índice de las 500 empresas más grandes de Estados Unidos. Representa aproximadamente el 80% del valor total del mercado de acciones estadounidense.',
            'bolsa': 'NYSE y NASDAQ'
        },
        'FTSE 100': {
            'pais': 'Reino Unido',
            'descripcion': 'Índice de las 100 empresas más grandes de la Bolsa de Londres (LSE). Es el principal indicador del mercado de valores británico.',
            'bolsa': 'London Stock Exchange (LSE)'
        },
        'IBEX 35': {
            'pais': 'España',
            'descripcion': 'Índice de las 35 empresas más líquidas y representativas del mercado español. Es el principal indicador de la Bolsa de Madrid.',
            'bolsa': 'Bolsas y Mercados Españoles (BME)'
        },
        'FTSE MIB': {
            'pais': 'Italia',
            'descripcion': 'Índice de las 40 empresas más importantes de la Bolsa de Milán. Es el principal indicador del mercado de valores italiano.',
            'bolsa': 'Borsa Italiana'
        },
        'CAC 40': {
            'pais': 'Francia',
            'descripcion': 'Índice de las 40 empresas más grandes de la Bolsa de París. Es el principal indicador del mercado de valores francés.',
            'bolsa': 'Euronext Paris'
        },
        'DAX 40': {
            'pais': 'Alemania',
            'descripcion': 'Índice de las 40 empresas más importantes de la Bolsa de Fráncfort. Es el principal indicador del mercado de valores alemán.',
            'bolsa': 'Frankfurt Stock Exchange'
        }
    }
    
    return info_indices.get(nombre_indice, {
        'pais': 'Desconocido',
        'descripcion': 'Información no disponible',
        'bolsa': 'Desconocida'
    })
