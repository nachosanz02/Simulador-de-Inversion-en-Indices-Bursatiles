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


def formatear_precio(precio: float, divisa: str) -> str:
    """
    Formatea un precio con su símbolo de divisa
    
    Args:
        precio: Precio a formatear
        divisa: Código de divisa (USD, EUR, GBP)
    
    Returns:
        String formateado con símbolo de divisa
    """
    simbolos = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£'
    }
    simbolo = simbolos.get(divisa, divisa)
    return f"{simbolo}{precio:,.2f}"


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

