# Laboratorio 9 — Analítica de clientes

**Estudiante:** Jhadir Abdel Yupanqui Chahua · C28, 6.º A-L

**Curso:** Analítica Empresarial Integrada · TECSUP 2026-II

[Abrir el notebook individual ejecutado](LAB-D9-AEI-PSAYAN-2026-02_YUPANQUI.ipynb).

El notebook contiene una explicación en Markdown antes de cada celda de código, las preguntas 1–9 resueltas, resultados y gráficos guardados, sensibilidad económica y un cierre ejecutivo de ocho líneas. Mantiene el diseño del laboratorio original: limpieza de compras válidas, ventana histórica de 180 días, churn a 90 días, RFM y regresión logística. Se añaden comprobaciones de consistencia y una lectura económica por segmento.

## Ejecución

1. Instalar Python y Jupyter. El entorno utilizado fue Python 3.12.10 en Windows.
2. Instalar las dependencias de `requirements.txt` y abrir el notebook desde esta carpeta.
3. Ejecutar todas las celdas en orden. La primera celda prepara las bibliotecas; las versiones utilizadas se imprimen en la siguiente.
4. Si no existe `datos/online_retail_II.zip`, el notebook descarga el archivo oficial de UCI y lee las dos hojas del Excel. La huella SHA-256 permite identificar el archivo utilizado.

Las figuras incluyen PNG para visualizarse directamente en GitHub y una representación interactiva para Jupyter. La exportación PNG utiliza Kaleido; se conserva Plotly 5 y Kaleido anterior a 1 para evitar una dependencia adicional de Chrome.

No se incluye el archivo de datos en Git. Fuente: Chen, D. (2012), [Online Retail II, UCI ID 502](https://archive.ics.uci.edu/dataset/502/online+retail+ii), [DOI 10.24432/C5CG6D](https://doi.org/10.24432/C5CG6D), licencia CC BY 4.0.

## Alcance de la decisión

La ejecución incluye 2.772 clientes. Entre las políticas evaluadas, validación selecciona contactar a todos: £19.901,28 netos simulados. Al mantener esa política en prueba se contactarían 555 clientes y se simulan £11.789,08 netos, frente a £0 por no contactar. El desglose descriptivo de prueba atribuye £5.246,65 a Regular y £3.150,16 a Hibernating; no constituye una nueva selección de política por segmentos.

La política se selecciona entre los umbrales evaluados usando validación y se aplica a prueba sin reajustarla. Los escenarios de sensibilidad mantienen esta separación. El valor monetario es una simulación bajo supuestos de coste, efectividad, incentivo y margen; no es una ganancia observada ni prueba causal de retención. La segmentación no se usa como predictor y la partición entre clientes de un solo corte no sustituye una validación temporal.

El notebook declara el uso de OpenAI Codex como apoyo para documentación, revisión, respuestas y comprobaciones. No se publica ninguna participación en Canvas desde este repositorio.
