# PMD2 Suministros Sur

Proyecto Integrador 2 de Analítica Empresarial Integrada · TECSUP 2026-II · Equipo 1 · Caso 4.

## Entrega del checkpoint

- [Notebook ejecutado](Checkpoint_Suministros_Sur_Eq1.ipynb). [Abrir en Colab](https://colab.research.google.com/github/jhadir08/analitica-empresarial-integrada/blob/main/PMD2/Checkpoint_Suministros_Sur_Eq1.ipynb).
- [Gobierno, matriz normativa, plan de integración y pendientes](Gobierno_y_pendientes.md).
- [Evaluación de las 20 preguntas y registro de defectos](salidas/evaluacion_asistente.csv).
- [Resultados y cifras del tablero](salidas/). Los identificadores de las cuentas sólo aparecen en la salida de trabajo local.

El notebook conserva el encabezado suministrado por la docente y usa una revisión fija de los [datos sintéticos oficiales](https://github.com/Rociosayan/pmd2-aei-2026ii/tree/fbdc97049e78850545d7a2bf8c000bb5dadeff3c/casos/caso4_suministros_sur). Para reproducir en Colab, abrir el enlace y ejecutar todas las celdas. El cuaderno descarga los módulos del proyecto si se abre fuera del repositorio. El notebook vuelve a ejecutar la línea base y carga el registro guardado de Qwen. Para repetir esa inferencia con pesos locales, configure PMD2_MODELO_LOCAL como Qwen/Qwen2.5-0.5B-Instruct antes de ejecutar. La primera carga descarga los pesos. El asistente público usa recuperación determinista de extractos de las políticas vigentes.

## Resultados del checkpoint

- **Predicción.** PR-AUC de 0,408 frente a 0,400 con la regla de recencia. El umbral elegido es 0,20 y la tasa de falsos positivos en prueba es 82,9 %. El pronóstico seleccionado por serie obtuvo un WAPE de 29,0 %, frente al 31,9 % del ingenuo anual y 33,8 % del ingenuo reciente.
- **Decisión central.** Con un efecto supuesto de 4 %, ningún contacto presenta valor esperado positivo bajo los costes definidos. La propuesta pronostica 2.211 unidades solicitadas y alcanza S/ 32.652,42 de margen operativo con S/ 50.844,65 de compras. La política actual ajustada obtiene S/ 32.157,89 con S/ 64.823,87 en compras.
- **Vigilancia.** Los límites de control son preliminares en ambas zonas. Se registran tres señales de seguimiento en Valle Sagrado. El equipo debe investigar cada señal antes de activar alertas automáticas.
- **Asistente.** La recuperación determinista acertó 20 de 20 casos. Qwen acertó 18 de 20. El registro identifica dos casos de evidencia incompleta y ninguna respuesta sin sustento según el criterio fijado.

## Guías de los laboratorios

| Semana | Referencia | Adaptación |
|---|---|---|
| 9 | [D9](../semana09) | RFM, CLV y riesgo de churn operativo con cortes definidos por el caso |
| 10 | [D10](../semana10) | Backtesting temporal, ingenuos y Holt-Winters por zona y familia |
| 11 | [D11](../semana11) | Compras y contactos enteros con PuLP, sensibilidad y política actual reconstruida |
| 12 | [D12](../semana12) | Isolation Forest, base histórica separada y carta de medias con tamaño variable |
| 13 | [D13](../semana13) | Auditoría por subgrupos, SHAP, contrato y linaje |
| 14 | [D14](../semana14) | Evaluación fija, abstención, trazabilidad y comparación de motores |

[Materiales de las semanas 9 a 14 en Canvas](https://tecsup.instructure.com/courses/73300/modules). Los laboratorios se consultaron como referencia metodológica. Todos los resultados de la entrega corresponden al caso Suministros Sur.

## Producto

FastAPI sirve el JSON generado en el Colab y el asistente de políticas. La interfaz HTML, CSS y JavaScript consulta la API. Desde la carpeta PMD2, instalar `pip install -r requirements-api.txt` y ejecutar `uvicorn backend:app`. Abrir http://127.0.0.1:8000. La comprobación de estado está en `/api/health`.

La API de Render arranca con `uvicorn backend:app --app-dir PMD2 --host 0.0.0.0 --port $PORT`. Para publicar Netlify se ejecuta `python build_frontend.py DESTINO` y se despliega DESTINO. Con `--render-url URL` se añade el proxy hacia la API. Sin el backend, el sitio muestra la evaluación y el tablero desde las salidas del Colab. Los cambios de resultados se publican regenerando el notebook y su JSON, sin reentrenar ni cargar un LLM en cada petición.

El equipo debe validar las decisiones, los supuestos y la interpretación académica antes de la sustentación. Se utilizó IA generativa como apoyo de implementación y documentación.
