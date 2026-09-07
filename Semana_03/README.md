# Semana 3 — La métrica que importa

**Estudiante:** Jhadir Abdel Yupanqui Chahua  
**Curso:** Analítica Empresarial Integrada, TECSUP 2026-II.

[Abrir notebook ejecutado](LAB-D3-AEI-PSAYAN-2026-02_YUPANQUI.ipynb)

## Contenido

- Conceptos aplicados: dato, métrica, indicador, KPI, meta, North Star, driver y guardrail.
- Descarga y auditoría de Online Retail (UCI): 541 909 registros, 8 columnas originales y 38 países.
- Recurrencia calculada desde la segunda factura válida usando todo el historial antes de recortar la ventana.
- North Star, clientes y frecuencia; guardrails de cancelación, concentración Top 10 y Top 1.
- Cinco ejercicios de aplicación en Polars, DuckDB y Plotly, con preguntas e interpretaciones respondidas.
- Diccionario de KPI, informe ejecutivo, ticket de salida y controles de consistencia.

## Ejecutar

Entorno verificado: Python 3.12, Polars 1.17.1, DuckDB 1.1.3 y Plotly 5.24.1.

```bash
python -m pip install ucimlrepo==0.0.7 polars==1.17.1 duckdb==1.1.3 plotly==5.24.1 pandas pyarrow matplotlib nbformat nbclient ipykernel jupyter
python -m jupyter nbconvert --execute --to notebook --inplace LAB-D3-AEI-PSAYAN-2026-02_YUPANQUI.ipynb
```

Se necesita conexión a UCI para descargar los datos. Los gráficos incluyen una vista estática para GitHub y una representación interactiva para entornos compatibles. No se requiere Colab. La última celda exporta las métricas y el resumen de validación en el directorio de ejecución.

## Resultados y límites

Junio presenta la mayor caída comparable de compras recurrentes: −9,44 %. Mayo, septiembre, octubre y noviembre cumplen la regla académica de crecimiento positivo con cancelación inferior a la media mensual.

La ventana es enero-noviembre de 2011. Enero se trata como calentamiento; febrero se excluye del diagnóstico de variaciones porque se compara contra enero. Las metas son supuestos académicos. Se conservan los duplicados de la fuente según el criterio del laboratorio y se explicita su posible impacto; se excluyen clientes sin identificador de las métricas de recurrencia. Las asociaciones no prueban causalidad y los datos históricos no describen la situación actual de la empresa.

Fuente: Chen, D. (2015). [Online Retail — UCI](https://doi.org/10.24432/C5BW33).
