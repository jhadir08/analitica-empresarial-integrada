# PMD2 Suministros Sur

Proyecto Integrador 2 de Analítica Empresarial Integrada · TECSUP 2026-II · Equipo 1 · Caso 4.

## Entrega del checkpoint

- [Notebook ejecutado](Checkpoint_Suministros_Sur_Eq1.ipynb). [Abrir en Colab](https://colab.research.google.com/github/jhadir08/analitica-empresarial-integrada/blob/main/PMD2/Checkpoint_Suministros_Sur_Eq1.ipynb).
- [Gobierno, matriz normativa, plan de integración y pendientes](Gobierno_y_pendientes.md).
- [Evaluación de las 20 preguntas y registro de defectos](salidas/evaluacion_asistente.csv).
- [Resultados y cifras del tablero](salidas/). Los identificadores de las cuentas sólo aparecen en la salida de trabajo local.

El notebook conserva el encabezado suministrado por la docente y usa una revisión fija de los [datos sintéticos oficiales](https://github.com/Rociosayan/pmd2-aei-2026ii/tree/fbdc97049e78850545d7a2bf8c000bb5dadeff3c/casos/caso4_suministros_sur). Para reproducir en Colab, abrir el enlace y ejecutar todas las celdas. El cuaderno descarga los módulos del proyecto si se abre fuera del repositorio. El notebook ejecuta las líneas base y carga la evidencia registrada de GPT-6 Luna. Para repetir la llamada, configure OPENAI_API_KEY en el entorno del proceso y seleccione PMD2_REEVALUAR_LUNA=1. El secreto se gestiona fuera de Git. El servicio público reproduce las 20 respuestas guardadas sin volver a consultar OpenAI.

## Conclusiones para la sustentación

- **Retención.** El modelo logra PR-AUC de 0,408 frente a 0,400 de la regla de recencia. Al umbral 0,20 identifica 39 de los 40 abandonos en prueba y alerta también a 58 de las 70 cuentas que siguieron activas. En validación, todos los umbrales dejan el valor económico en cero. El desempate conserva el mayor recall y el umbral más alto compatible con ese recall. Con efecto supuesto del 4 %, se recomienda cero contactos. Al 9 %, el escenario selecciona 11 cuentas con S/ 52,57 de valor esperado a seis meses. El efecto del contacto sigue siendo un supuesto.
- **Compras y despacho.** El plan estima 2.211 unidades solicitadas. La selección por serie obtuvo WAPE de 29,0 %, frente al 31,9 % del ingenuo anual y al 33,8 % del reciente. Holt-Winters obtuvo 26,4 % agregado en el test. Es un resultado retrospectivo para revisar en el siguiente corte. En capacidad normal, el plan produce S/ 494,53 más de margen operativo y requiere S/ 13.979,22 menos de gasto de compra frente a la política actual ajustada. La carga llega a 7.499,3 de 7.500 kg y constituye el cuello de botella del escenario.
- **Control.** Valle Sagrado presenta tres señales en seguimiento. Ambas bases históricas tienen señales fuera de límites. Logística debe investigar las entregas y validar una base estable antes de automatizar las alertas.
- **Auditoría.** En Valle Sagrado los 14 casos negativos de la prueba fueron marcados como riesgo. La muestra justifica revisar el grupo antes de generalizar la tasa. Ingreso y margen de los últimos 180 días dominan SHAP con signos opuestos. Ambos derivan de la misma actividad comercial. Sus contribuciones describen el comportamiento del modelo y requieren revisar su dependencia.
- **Asistente.** SQL manual y recuperación determinista acertaron 20 de 20 en la batería fija. GPT-6 Luna acertó 20 de 20. La exactitud coincidió con las dos bases y falta medir el beneficio con preguntas nuevas. La batería mide estas políticas y preguntas específicas. Conviene mantener el registro y probar nuevas formulaciones antes de decidir el motor en producción.

## Mejoras basadas en los laboratorios

- **D10 y D11.** El apéndice del Colab compara las alternativas con el mismo conjunto de prueba y muestra la holgura en carga, horas y presupuesto para cada plan operativo. El resultado de prueba se conserva para evaluación.
- **D12 y D13.** El apéndice distingue las señales que requieren revisión humana y añade intervalos de Wilson para interpretar los falsos positivos de grupos pequeños.
- **D14.** La evaluación conserva la misma batería, añade un registro real de modelo, latencia y tokens y mide la abstención en los casos fuera de alcance. Para validar generalización, queda pendiente una batería nueva de paráfrasis y preguntas multitema.

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

La API de Render arranca con `uvicorn backend:app --app-dir PMD2 --host 0.0.0.0 --port $PORT`. Para publicar Netlify se ejecuta `python build_frontend.py DESTINO` y se despliega DESTINO. Con `--render-url URL` se añade el proxy hacia la API. Sin el backend, el sitio muestra la evaluación y el tablero desde las salidas del Colab. El backend ofrece las respuestas evaluadas sin coste adicional de OpenAI. Para habilitar preguntas nuevas se requieren dos variables secretas del servicio, OPENAI_API_KEY para consultar el modelo y PMD2_ACCESS_TOKEN como código de acceso de la demo. El frontend nunca recibe OPENAI_API_KEY.

El equipo debe validar las decisiones, los supuestos y la interpretación académica antes de la sustentación. Se utilizó IA generativa como apoyo de implementación y documentación.
