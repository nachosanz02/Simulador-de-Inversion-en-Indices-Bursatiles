"""
Script simple para ejecutar el dashboard
Ejecuta este archivo con: python run_dashboard.py
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(__file__))

from src.frontend.app import app

if __name__ == '__main__':
    print("\n" + "="*60)
    print("INICIANDO DASHBOARD")
    print("="*60)
    print("\nEl dashboard se está iniciando...")
    print("Abre tu navegador y ve a: http://127.0.0.1:8050")
    print("\nIMPORTANTE: Mantén esta ventana abierta mientras uses el dashboard")
    print("Presiona Ctrl+C para detener el servidor")
    print("="*60 + "\n")
    
    try:
        app.run_server(debug=True, host='127.0.0.1', port=8050)
    except KeyboardInterrupt:
        print("\n\nDashboard detenido. ¡Hasta luego!")

