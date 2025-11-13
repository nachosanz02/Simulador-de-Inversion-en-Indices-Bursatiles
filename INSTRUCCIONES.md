# Instrucciones de Instalación y Uso

## 1. Crear y Activar el Entorno Virtual

### En Windows (PowerShell):
```powershell
# Crear el entorno virtual (solo la primera vez)
python -m venv venv

# Activar el entorno virtual - OPCIÓN 1 (PowerShell)
.\venv\Scripts\Activate.ps1

# Si tienes problemas con la política de ejecución, usa OPCIÓN 2:
venv\Scripts\activate.bat

# O OPCIÓN 3: Ejecutar Python directamente desde el entorno virtual
venv\Scripts\python.exe run_dashboard.py
```

**Si tienes problemas con la política de ejecución en PowerShell:**
```powershell
# Método 1: Cambiar política (puede requerir permisos de administrador)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Método 2: Usar CMD en lugar de PowerShell
# Abre CMD y ejecuta: venv\Scripts\activate.bat

# Método 3: Usar Python directamente sin activar
venv\Scripts\python.exe -m pip install -r requirements.txt
venv\Scripts\python.exe run_dashboard.py
```

### En Windows (CMD):
```cmd
# Crear el entorno virtual (solo la primera vez)
python -m venv venv

# Activar el entorno virtual
venv\Scripts\activate.bat
```

### En Linux/Mac:
```bash
# Crear el entorno virtual (solo la primera vez)
python -m venv venv

# Activar el entorno virtual
source venv/bin/activate
```

## 2. Instalar Dependencias

**Una vez activado el entorno virtual** (verás `(venv)` al inicio de tu terminal), instala las dependencias:

```bash
pip install -r requirements.txt
```

**Si no puedes activar el entorno virtual**, puedes instalar directamente:
```bash
# En Windows PowerShell/CMD
venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 3. Descargar Datos (Opcional)

Si quieres descargar los datos históricos de los índices antes de usar el dashboard:

```bash
python main.py --descargar
```

## 4. Ejecutar el Dashboard

```bash
python run_dashboard.py
```

O también puedes usar:

```bash
python main.py --dashboard
```

## 5. Acceder al Dashboard

Una vez que veas el mensaje "Dash is running on http://127.0.0.1:8050/", abre tu navegador y ve a:

```
http://127.0.0.1:8050
```

## 6. Detener el Servidor

Presiona `Ctrl + C` en la terminal para detener el servidor.

## Notas Importantes

- **Mantén la terminal abierta** mientras uses el dashboard
- El entorno virtual debe estar **activado** antes de ejecutar cualquier comando
- Si instalas nuevas dependencias, actualiza el archivo `requirements.txt` con: `pip freeze > requirements.txt`

