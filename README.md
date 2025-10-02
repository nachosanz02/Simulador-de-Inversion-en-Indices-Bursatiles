Desarrollo-de-aplicacines-para-la-visualizacion-de-datos

Simulador de Inversión en Indices Bursatiles 

Descripción

Este proyecto desarrolla un dashboard interactivo para simular inversiones pasadas en los principales índices bursátiles internacionales: S&P 500, FTSE 100, IBEX 35, FTSE MIB, CAC 40 y DAX 40.
El objetivo es acercar la inversión a estudiantes, pequeños ahorradores y cualquier persona interesada en mejorar su educación financiera. El usuario podrá introducir una fecha de inversión y una  cantidad, y descubrir cuánto valdría hoy esa inversión, además de visualizar la evolución histórica de los índices seleccionados.

Objetivos

- Facilitar la comprensión de cómo evoluciona una inversión a lo largo del tiempo.  
- Crear un simulador gratuito y accesible desde GitHub.  
- Presentar la información de forma clara y visual, sin necesidad de conocimientos financieros avanzados.  
- Promover la educación financiera básica mediante un caso práctico real.

Plan Inicial de Trabajo

1. Recopilación de datos: descaragar series historcas de los diferentes indices en yahoo Finance o por medio de la API de Yahoo
2. Preprocesamiento: Aunque haya visto de manera rapida que los datos están limpios, volver a analizarlo y realizar el preprocesamiento.
3. Simulación: Calculo automatico del valor actual dado una fecha de inversion, en que se ha invertido y la cantidad de dinero invertida
4. Visualización: representación gráfica de la evolución de los índices y de la inversión simulada.
5. Aplicación de técnicas de ML:
	- Construcción de variables explicativas (retornos pasados, medias móviles, volatilidad).  
   - Entrenamiento de un modelo de regresión lineal / Ridge para predecir el retorno del siguiente mes. 
   - Evaluación con validación temporal (`TimeSeriesSplit`) y métricas de error (RMSE, MAE).  
   - Mostrar en el dashboard el retorno estimado como información complementaria.  
6. Dashboard: Contruccion de aplicacion interactiva que combine lo realizado anteriormente
   
