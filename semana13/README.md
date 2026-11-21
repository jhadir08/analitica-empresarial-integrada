# Laboratorio D13 — Auditoría de un modelo

El notebook aplica una regresión logística a UCI Adult (ID 2), calcula métricas globales y por subgrupos, compara umbrales, agrupa SHAP por variable original y documenta hallazgos y controles de gobierno.

## Contenido

- `LAB-D13-AEI-PSAYAN-2026-02_YUPANQUI.ipynb`: desarrollo ejecutado, respuestas, ejercicios y conclusiones.
- `requirements.txt`: dependencias para reproducir el análisis.

## Ejecución

Abrir el notebook en Google Colab o Jupyter y ejecutar todas las celdas en orden. La celda inicial instala `ucimlrepo`, `shap` y `plotly`; luego el notebook descarga UCI Adult mediante su ID 2. Requiere conexión a internet para descargar los datos.

La ejecución utilizada para generar los resultados fija `random_state=42`, una partición estratificada 75/25 y una muestra SHAP de 500 registros con semilla 42.

## Alcance y limitaciones

UCI Adult predice si el ingreso anual supera USD 50 000 a partir de datos del censo de Estados Unidos de 1994. No contiene aprobaciones de préstamos, morosidad ni pérdidas crediticias. Por ello, el modelo sirve para el ejercicio académico de auditoría y **no debe utilizarse para evaluar solicitudes de crédito**. Las brechas descriptivas y SHAP requieren análisis de contexto; SHAP no prueba causalidad. El checklist tampoco constituye certificación legal ni evidencia de controles organizacionales implantados.

## Fuentes

- [UCI Machine Learning Repository — Adult](https://archive.ics.uci.edu/dataset/2/adult)
- Ley N.º 29733 y DS N.º 016-2024-JUS.
- Ley N.º 31814 y DS N.º 115-2025-PCM.
- DAMA-DMBOK, 2.ª edición revisada.
