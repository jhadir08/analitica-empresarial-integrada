# Semana 12 — Analítica de procesos internos

**Estudiante:** Jhadir Abdel Yupanqui Chahua · C28 6to A-L · TECSUP 2026-II.

[Notebook completo y ejecutado](LAB-D12-AEI-PSAYAN-2026-02_YUPANQUI.ipynb) · [Abrir en Google Colab](https://colab.research.google.com/github/jhadir08/analitica-empresarial-integrada/blob/main/semana12/LAB-D12-AEI-PSAYAN-2026-02_YUPANQUI.ipynb)

El notebook desarrolla el caso de temperatura de una máquina industrial del archivo proporcionado: siete pasos guiados, diez respuestas (1.1–3.3), tres gráficos, sensibilidad de umbrales, contraste con ventanas NAB, reentrenamiento y comparación de variables. Su caso es distinto de MediSur descrito en el foro. No se ha registrado una entrega en Canvas.

## Resultados verificados

- 22.695 filas originales; 12 marcas repetidas, sin huecos de 5 minutos.
- 8.340 lecturas base y 14.112 de seguimiento con variables completas.
- p99: 495 alertas, 17 episodios, 8 días fuera; cubre 1 de 2 ventanas del seguimiento.
- p98/p99/p99,5: 31/17/3 episodios y 15/6/0 excedentes del cupo diario. Estos excedentes no son una cola final con atención posterior.
- Base ampliada: en el periodo común las alertas pasan de 469 a 501; los episodios, de 13 a 16.
- Solo valor: 459 alertas y 4 episodios; cuatro variables: 495 y 17. Ambos cubren una de las dos ventanas.

## Archivos y ejecución

- `datos/`: lecturas, ventanas, descripción primaria, licencia y manifiesto con hashes SHA-256, fijados a un commit de NAB.
- `resultados/`: nueve tablas CSV, tres gráficos PNG y versiones del entorno.
- `requirements.txt`: versiones utilizadas localmente con Python 3.12.10.

Verificación: 12 celdas ejecutadas sin errores el 08/11/2026 23:25 (America/Lima). Para reproducir localmente, instalar `requirements.txt`, abrir este notebook desde `semana12/` y ejecutar todas las celdas. En Colab las fuentes faltantes se descargan desde la misma versión fijada. El enlace de Colab abre GitHub y permite guardar una copia personal en Drive; no representa una copia ya guardada allí.

Codex (OpenAI) apoyó implementación, ejecución, verificación y redacción. Una alerta indica rareza; confirmar una falla requiere investigación y evidencia técnica externa.
