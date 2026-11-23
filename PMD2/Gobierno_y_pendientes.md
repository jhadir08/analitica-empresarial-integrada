# Gobierno y pendientes del checkpoint

Suministros Sur · Equipo 1 · Semana 14

## Contrato y linaje

La revisión de los CSV se fija en el notebook. La carpeta de datos original permanece como fuente de los ocho archivos. El encabezado valida diez controles y materializa una base DuckDB de solo lectura. Cada ejecución vincula esa base a las tablas CSV y al JSON del tablero. El tablero público usa agregados y el corpus de políticas vigentes. Los contactos seudonimizados se producen localmente para revisión comercial.

| Tabla | Grano y validación | Área propietaria y frecuencia propuesta | Uso |
|---|---|---|---|
| clientes | Cuenta única, zona y consentimiento | Comercial, diaria | Elegibilidad, contacto y auditoría |
| actividad | Evento único, cuenta y fecha válidas, soles y unidades | Comercial, diaria | RFM, CLV, historial y retrasos |
| cohortes | Cuenta por corte, etiqueta binaria y seguimiento completo | Analítica, mensual | Entrenamiento, validación, prueba y cartera |
| demanda | Semana, sede, familia, solicitado = atendido + faltante | Logística, semanal | Pronóstico y PuLP |
| recursos | Periodo, recurso y línea, unidades y límites conciliados | Finanzas y Logística, mensual | Topes, costes, peso y márgenes |
| operaciones | Evento operativo único, horas o soles según tipo | Logística y Finanzas, diaria | Anomalías y carta de control |
| politica_actual | Regla versionada por alcance y vigencia | Comercial y Logística, por cambio | Comparación de decisión |
| documentos | Documento y versión, vigencia y responsable | Área emisora, por cambio | Evidencia vigente para el asistente |

Comercial verifica consentimiento y decide cualquier contacto. Logística valida alertas de entrega y capacidad. Finanzas contrasta notas de crédito y aprueba el presupuesto. El responsable de calidad comprueba claves, partidas, unidades y versiones al cargar. El responsable técnico controla la revisión de datos, reproduce el notebook y publica agregados. Los permisos de cuenta son limitados a los responsables operativos. Como propuesta del caso, revisar la necesidad de conservar el detalle a los doce meses y preservar agregados y versiones para trazabilidad. La política definitiva de retención se aprueba con el dueño de datos antes de operar con datos reales.

## Matriz normativa

| Fuente oficial | Aplicabilidad y evidencia propuesta |
|---|---|
| [Ley 29733](https://www.gob.pe/institucion/congreso-de-la-republica/normas-legales/243470-29733) y [DS 016-2024-JUS](https://www.gob.pe/institucion/anpd/normas-legales/6554453-n-016-2024-jus) | El caso es sintético. Si se usan datos de personas identificables, validar finalidad, base de tratamiento, acceso, retención, atención de derechos y respuesta a incidentes. Revisar que la seudonimización no permita una divulgación impropia. |
| [Ley 31814](https://leyes.congreso.gob.pe/Documentos/2021_2026/ADLP/Texto_Consolidado/31814-TXM.pdf) y [DS 115-2025-PCM](https://www.gob.pe/institucion/pcm/normas-legales/7133522-115-2025-) | Aplicar supervisión humana, trazabilidad y evaluación de riesgos. El asistente consulta políticas vigentes y cita documentos. La campaña usa riesgo operativo de abandono. Una aplicación al crédito real exige evaluar el nuevo uso antes de desplegarlo. |
| [Reglamento (UE) 2024/1689, art. 2](https://eur-lex.europa.eu/eli/reg/2024/1689/oj) | El caso descrito opera en Cusco y Valle Sagrado. No se identifica una oferta ni uso de salidas en la UE. Reevaluar el nexo si cambia el alcance. |

## Revisión y tareas para la semana 15

Responsables propuestos para el avance del equipo.

| Responsable | Pendiente verificable |
|---|---|
| Agreda Villacorta, Gyanella | Revisar las exclusiones de elegibilidad y estabilidad del umbral económico. Verificar el escenario sin efecto. |
| Aranda Cuevas, Trilce | Conciliar la demanda y el plan de compra con los recursos. Validar que la regla histórica sea un comparador representativo. |
| Gogin Cisterna, Rodrigo | Revisar las semanas fuera de control con Logística. Estimar una línea base estable antes de automatizar. |
| Mayorca Parra, Sara | Revisar los grupos de muestra pequeña, políticas vigentes y preparación de la matriz normativa. |
| Yupanqui Chahua, Jhadir | Validar la publicación, corregir defectos del asistente con casos de regresión y comprobar las cifras en el producto. |

El despliegue separado usa la API de Render y el frontend de Netlify. El adaptador Streamlit puede importar las mismas salidas y llamar a los mismos componentes de consulta. Antes de la demo, comparar pronóstico, escenarios, control, auditoría y evaluación con el JSON generado por el notebook. Mantener la ficha de defectos junto a las pruebas fijas.
