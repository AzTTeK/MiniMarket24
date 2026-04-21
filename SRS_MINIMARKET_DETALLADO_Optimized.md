<!-- Página 1 -->
SRS — Sistema Inteligente de Predicción de Demanda | MiniMarket La 24 S.A.S. | v2.0
ESPECIFICACIÓN DE REQUERIMIENTOS DE SOFTWARE
Sistema Inteligente de Predicción de
Demanda
MiniMarket La 24 S.A.S.
─────────────────────────────────────────
Mateo Reyes T00077079
Elías José Blanco Gil T00078817
Sebastian Valencia T00078248
Montesino
Jose Pereira Acuña T00079768
Fabián Corpas Castro T00064976
─────────────────────────────────────────
Ingeniería de Software • Abril 2025 • Versión 2.0
Universidad — Ingeniería de Software | Abril 2024 Página 1 de 16


<!-- Página 2 -->
SRS — Sistema Inteligente de Predicción de Demanda | MiniMarket La 24 S.A.S. | v2.0
Control de Versiones
Versión Fecha Descripción Autor(es) Estado
1.0 01/04/2025 Borrador inicial del SRS Equipo consultor Aprobado
2.0 04/04/2025 Revisión completa: Equipo consultor Vigente
trazabilidad, RNF
ampliados, riesgos,
arquitectura
Universidad — Ingeniería de Software | Abril 2024 Página 2 de 16

### Tablas detectadas en esta sección:
|  | Versión |  |  | Fecha |  |  | Descripción |  |  | Autor(es) |  |  | Estado |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | 1.0 |  |  | 01/04/2025 |  |  | Borrador inicial del SRS |  |  | Equipo consultor |  |  | Aprobado |  |
| 2.0 |  |  | 04/04/2025 |  |  |  | Revisión completa: |  | Equipo consultor |  |  | Vigente |  |  |
|  |  |  |  |  |  |  | trazabilidad, RNF |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  | ampliados, riesgos, |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  | arquitectura |  |  |  |  |  |  |  |



<!-- Página 3 -->
SRS — Sistema Inteligente de Predicción de Demanda | MiniMarket La 24 S.A.S. | v2.0
1. Introducción
1.1 Propósito del Documento
Este documento constituye la Especificación de Requerimientos de Software (SRS) para el prototipo
funcional del Sistema Inteligente de Predicción de Demanda de MiniMarket La 24 S.A.S. Está elaborado
bajo el estándar IEEE 830 y define de manera completa, consistente y trazable los requisitos funcionales,
no funcionales, restricciones de diseño y criterios de aceptación del sistema. Su audiencia principal son
el equipo de desarrollo, el cliente y el comité evaluador académico.
1.2 Alcance del Sistema
El sistema, denominado internamente DEMAND-24, es un prototipo de predicción de demanda semanal
por producto para el contexto de una cadena de tiendas de barrio. El sistema NO pretende reemplazar
el juicio humano; su propósito es transformar los datos históricos de facturación en proyecciones
accionables que apoyen las decisiones de reposición de inventario. El piloto abarca un subconjunto de
productos estratégicos definidos por la gerencia.
1.3 Definiciones, Siglas y Abreviaturas
Término / Sigla Definición
SRS Software Requirements Specification — Especificación de Requerimientos de
Software.
IA Inteligencia Artificial — conjunto de algoritmos que aprenden patrones a partir
de datos.
RF Requerimiento Funcional — comportamiento observable del sistema.
RNF Requerimiento No Funcional — restricción de calidad, rendimiento o
arquitectura.
MAPE Mean Absolute Percentage Error — métrica de precisión del modelo predictivo.
MAE Mean Absolute Error — error medio absoluto en unidades de producto.
SKU Stock Keeping Unit — identificador único de producto en inventario.
API Application Programming Interface — interfaz de programación entre
componentes.
ETL Extract, Transform, Load — proceso de ingesta y transformación de datos.
DEMAND-24 Nombre interno del sistema a desarrollar.
1.4 Referencias
• IEEE Std 830-1998: Recommended Practice for Software Requirements Specifications.
• Hyndman & Athanasopoulos (2021). Forecasting: Principles and Practice, 3rd ed. OTexts.
• Documentación interna: actas de reunión con MiniMarket La 24 S.A.S., abril 2025.
• Martin Fowler (2002). Patterns of Enterprise Application Architecture. Addison-Wesley.
Universidad — Ingeniería de Software | Abril 2024 Página 3 de 16

### Tablas detectadas en esta sección:
|  | Término / Sigla |  |  | Definición |  |
| --- | --- | --- | --- | --- | --- |
| SRS |  |  |  | Software Requirements Specification — Especificación de Requerimientos de |  |
|  |  |  |  | Software. |  |
| IA |  |  |  | Inteligencia Artificial — conjunto de algoritmos que aprenden patrones a partir |  |
|  |  |  |  | de datos. |  |
|  | RF |  |  | Requerimiento Funcional — comportamiento observable del sistema. |  |
| RNF |  |  |  | Requerimiento No Funcional — restricción de calidad, rendimiento o |  |
|  |  |  |  | arquitectura. |  |
|  | MAPE |  |  | Mean Absolute Percentage Error — métrica de precisión del modelo predictivo. |  |
|  | MAE |  |  | Mean Absolute Error — error medio absoluto en unidades de producto. |  |
|  | SKU |  |  | Stock Keeping Unit — identificador único de producto en inventario. |  |
| API |  |  |  | Application Programming Interface — interfaz de programación entre |  |
|  |  |  |  | componentes. |  |
|  | ETL |  |  | Extract, Transform, Load — proceso de ingesta y transformación de datos. |  |
|  | DEMAND-24 |  |  | Nombre interno del sistema a desarrollar. |  |



<!-- Página 4 -->
SRS — Sistema Inteligente de Predicción de Demanda | MiniMarket La 24 S.A.S. | v2.0
1.5 Visión General del Documento
El documento se organiza en ocho secciones: (1) Introducción, (2) Descripción General, (3)
Requerimientos Funcionales, (4) Requerimientos No Funcionales, (5) Modelado del Sistema, (6)
Arquitectura Propuesta, (7) Análisis de Riesgos y (8) Criterios de Aceptación. Cada requerimiento cuenta
con identificador único, descripción, prioridad y criterio de verificación.
Universidad — Ingeniería de Software | Abril 2024 Página 4 de 16


<!-- Página 5 -->
SRS — Sistema Inteligente de Predicción de Demanda | MiniMarket La 24 S.A.S. | v2.0
2. Descripción General del Proyecto
2.1 Perspectiva del Producto
DEMAND-24 es un sistema nuevo, independiente de los sistemas de producción actuales. Se integra de
forma unidireccional con el sistema de facturación existente mediante un módulo ETL que extrae datos
históricos de ventas sin modificar dichos sistemas. El sistema opera como una capa analítica
desacoplada, exponiendo sus resultados a través de una interfaz web accesible desde los equipos de
la tienda.
2.2 Funciones Principales del Producto
Las funciones principales del sistema son las siguientes:
• Ingesta y validación automática de datos históricos de ventas.
• Entrenamiento y versionamiento de modelos de predicción de demanda.
• Generación de predicciones semanales por SKU con intervalos de confianza.
• Generación de alertas automáticas de quiebre de stock proyectado.
• Visualización de tendencias históricas y proyectadas por producto y sucursal.
• Registro de ventas reales para retroalimentación y reentrenamiento del modelo.
2.3 Actores del Sistema
Actor Descripción Interacción Principal
Administrador de Responsable de la gestión operativa de Consulta predicciones, revisa
Tienda cada sucursal. Realiza pedidos alertas, registra ventas reales.
semanales y atiende alertas de inventario.
Gerencia General Supervisa el desempeño estratégico. Visualiza dashboards de
Necesita visualizar tendencias de tendencias y métricas de
demanda a nivel macro sin involucrarse modelo.
en la operación diaria.
Área Financiera Monitorea el impacto económico del Consulta métricas de precisión
sistema: reducción de pérdidas por y reportes de ahorro estimado.
vencimiento y por ruptura de stock.
Sistema de Sistema externo que almacena el historial Origen de datos históricos para
Facturación de ventas. Actor pasivo fuente de datos. el módulo ETL.
Modelo de IA Componente interno que ejecuta el ciclo Es entrenado con datos
entrena-predice-reentrena. históricos y genera
predicciones consumidas por la
capa de presentación.
2.4 Restricciones Generales
• El sistema deberá desarrollarse como piloto de bajo costo con tecnologías de código abierto.
• No se modificará el sistema de facturación existente; la integración es de solo lectura.
Universidad — Ingeniería de Software | Abril 2024 Página 5 de 16

### Tablas detectadas en esta sección:
|  | Actor |  |  | Descripción |  |  | Interacción Principal |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Administrador de Tienda |  |  |  | Responsable de la gestión operativa de |  | Consulta predicciones, revisa alertas, registra ventas reales. |  |  |
|  |  |  |  | cada sucursal. Realiza pedidos |  |  |  |  |
|  |  |  |  | semanales y atiende alertas de inventario. |  |  |  |  |
| Gerencia General |  |  |  | Supervisa el desempeño estratégico. |  | Visualiza dashboards de tendencias y métricas de modelo. |  |  |
|  |  |  |  | Necesita visualizar tendencias de |  |  |  |  |
|  |  |  |  | demanda a nivel macro sin involucrarse |  |  |  |  |
|  |  |  |  | en la operación diaria. |  |  |  |  |
| Área Financiera |  |  |  | Monitorea el impacto económico del |  | Consulta métricas de precisión y reportes de ahorro estimado. |  |  |
|  |  |  |  | sistema: reducción de pérdidas por |  |  |  |  |
|  |  |  |  | vencimiento y por ruptura de stock. |  |  |  |  |
|  | Sistema de |  |  | Sistema externo que almacena el historial |  |  | Origen de datos históricos para |  |
|  | Facturación |  |  | de ventas. Actor pasivo fuente de datos. |  |  | el módulo ETL. |  |
| Modelo de IA |  |  | Componente interno que ejecuta el ciclo entrena-predice-reentrena. |  |  |  | Es entrenado con datos |  |
|  |  |  |  |  |  |  | históricos y genera |  |
|  |  |  |  |  |  |  | predicciones consumidas por la |  |
|  |  |  |  |  |  |  | capa de presentación. |  |


| Administrador de |
| --- |
| Tienda |


| Consulta predicciones, revisa |
| --- |
| alertas, registra ventas reales. |


| Visualiza dashboards de |
| --- |
| tendencias y métricas de |
| modelo. |


| Consulta métricas de precisión |
| --- |
| y reportes de ahorro estimado. |


| Componente interno que ejecuta el ciclo |
| --- |
| entrena-predice-reentrena. |



<!-- Página 6 -->
SRS — Sistema Inteligente de Predicción de Demanda | MiniMarket La 24 S.A.S. | v2.0
• La arquitectura debe ser modular (desacoplada) para permitir extensiones futuras.
• El piloto operará sobre un subconjunto de SKU estratégicos definidos por la gerencia.
• La precisión del modelo estará limitada por la calidad y completitud de los datos históricos.
2.5 Suposiciones y Dependencias
• Los datos de ventas históricos están disponibles en el sistema de facturación con al menos 12
semanas de historia por SKU piloto.
• El área tecnológica del cliente proveerá acceso de lectura a la base de datos de facturación.
• Los administradores de tienda participarán en sesiones de capacitación de máximo dos horas.
• La infraestructura de despliegue será provista por el cliente (servidor local o instancia cloud
básica).
Universidad — Ingeniería de Software | Abril 2024 Página 6 de 16


<!-- Página 7 -->
SRS — Sistema Inteligente de Predicción de Demanda | MiniMarket La 24 S.A.S. | v2.0
3. Requerimientos Funcionales
La siguiente tabla especifica cada requerimiento funcional con su identificador único, prioridad (Alta /
Media / Baja), nombre, descripción detallada y criterio de verificación. La prioridad refleja el impacto en
los objetivos del piloto.
Criterio de
ID Prioridad Nombre Descripción
Verificación
RF- Alta Ingesta de Datos El sistema debe conectarse al Prueba de integración:
01 (ETL) sistema de facturación y extraer ejecutar ETL con datos
registros históricos de ventas de prueba, verificar
(fecha, SKU, cantidad, precio que la tabla de ventas
unitario, sucursal). La extracción se actualice
debe ser incremental: solo carga correctamente sin
datos nuevos desde la última duplicados.
ejecución exitosa.
RF- Alta Validación de Antes de entrenar o predecir, el Prueba unitaria: cargar
02 Datos sistema debe evaluar la calidad dataset con 8 semanas
del dataset: cantidad mínima de de historia; el sistema
registros por SKU (≥ 12 debe rechazar la
semanas), ausencia de valores predicción e indicar el
nulos críticos y coherencia de motivo.
fechas. Ante datos insuficientes
emite mensaje de error
descriptivo.
RF- Alta Generación de El modelo de IA debe generar, Prueba de aceptación:
03 Predicción para cada SKU activo, una el MAPE del modelo
estimación de la demanda para sobre el conjunto de
las próximas 1–4 semanas, validación debe ser ≤
incluyendo límite inferior y 20% en al menos el
superior del intervalo de 70% de los SKU piloto.
confianza al 90%.
RF- Alta Alertas de Si la demanda proyectada para Prueba funcional:
04 Quiebre de la próxima semana supera el insertar un SKU con
Stock stock actual registrado para un stock < demanda
SKU, el sistema genera una proyectada; verificar
alerta visible en el dashboard del que la alerta aparece
Administrador con el mensaje: en menos de 5
'Posible quiebre de stock: [SKU] segundos.
— Demanda proyectada: X uds,
Stock actual: Y uds.'
RF- Media Visualización de El sistema debe mostrar, por Prueba de usabilidad:
05 Tendencias SKU y sucursal, una gráfica de un administrador debe
serie de tiempo con el historial ser capaz de
de ventas de las últimas 12 interpretar la gráfica
semanas y la proyección de las correctamente sin
próximas 4 semanas. Las instrucciones
bandas de confianza deben ser adicionales en < 2
visibles y diferenciadas del valor minutos.
central.
RF- Alta Registro de El Administrador puede registrar Prueba funcional:
06 Venta Real manualmente la venta real de la registrar venta real,
Universidad — Ingeniería de Software | Abril 2024 Página 7 de 16

### Tablas detectadas en esta sección:
| ID |  |  | Prioridad | Nombre |  |  | Descripción |  |  |  | Criterio de |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  |  |  | Verificación |  |
| RF- 01 |  |  | Alta | Ingesta de Datos (ETL) |  |  |  | El sistema debe conectarse al |  | Prueba de integración: ejecutar ETL con datos de prueba, verificar que la tabla de ventas se actualice correctamente sin duplicados. |  |  |
|  |  |  |  |  |  |  |  | sistema de facturación y extraer |  |  |  |  |
|  |  |  |  |  |  |  |  | registros históricos de ventas |  |  |  |  |
|  |  |  |  |  |  |  |  | (fecha, SKU, cantidad, precio |  |  |  |  |
|  |  |  |  |  |  |  |  | unitario, sucursal). La extracción |  |  |  |  |
|  |  |  |  |  |  |  |  | debe ser incremental: solo carga |  |  |  |  |
|  |  |  |  |  |  |  |  | datos nuevos desde la última |  |  |  |  |
|  |  |  |  |  |  |  |  | ejecución exitosa. |  |  |  |  |
| RF- 02 |  |  | Alta | Validación de Datos |  |  |  | Antes de entrenar o predecir, el |  | Prueba unitaria: cargar dataset con 8 semanas de historia; el sistema debe rechazar la predicción e indicar el motivo. |  |  |
|  |  |  |  |  |  |  |  | sistema debe evaluar la calidad |  |  |  |  |
|  |  |  |  |  |  |  |  | del dataset: cantidad mínima de |  |  |  |  |
|  |  |  |  |  |  |  |  | registros por SKU (≥ 12 |  |  |  |  |
|  |  |  |  |  |  |  |  | semanas), ausencia de valores |  |  |  |  |
|  |  |  |  |  |  |  |  | nulos críticos y coherencia de |  |  |  |  |
|  |  |  |  |  |  |  |  | fechas. Ante datos insuficientes |  |  |  |  |
|  |  |  |  |  |  |  |  | emite mensaje de error |  |  |  |  |
|  |  |  |  |  |  |  |  | descriptivo. |  |  |  |  |
| RF- 03 |  |  | Alta | Generación de Predicción |  |  |  | El modelo de IA debe generar, |  | Prueba de aceptación: el MAPE del modelo sobre el conjunto de validación debe ser ≤ 20% en al menos el 70% de los SKU piloto. |  |  |
|  |  |  |  |  |  |  |  | para cada SKU activo, una |  |  |  |  |
|  |  |  |  |  |  |  |  | estimación de la demanda para |  |  |  |  |
|  |  |  |  |  |  |  |  | las próximas 1–4 semanas, |  |  |  |  |
|  |  |  |  |  |  |  |  | incluyendo límite inferior y |  |  |  |  |
|  |  |  |  |  |  |  |  | superior del intervalo de |  |  |  |  |
|  |  |  |  |  |  |  |  | confianza al 90%. |  |  |  |  |
| RF- 04 |  |  | Alta | Alertas de Quiebre de Stock |  |  |  | Si la demanda proyectada para |  | Prueba funcional: insertar un SKU con stock < demanda proyectada; verificar que la alerta aparece en menos de 5 segundos. |  |  |
|  |  |  |  |  |  |  |  | la próxima semana supera el |  |  |  |  |
|  |  |  |  |  |  |  |  | stock actual registrado para un |  |  |  |  |
|  |  |  |  |  |  |  |  | SKU, el sistema genera una |  |  |  |  |
|  |  |  |  |  |  |  |  | alerta visible en el dashboard del |  |  |  |  |
|  |  |  |  |  |  |  |  | Administrador con el mensaje: |  |  |  |  |
|  |  |  |  |  |  |  |  | 'Posible quiebre de stock: [SKU] |  |  |  |  |
|  |  |  |  |  |  |  |  | — Demanda proyectada: X uds, |  |  |  |  |
|  |  |  |  |  |  |  |  | Stock actual: Y uds.' |  |  |  |  |
| RF- 05 |  |  | Media | Visualización de Tendencias |  |  |  | El sistema debe mostrar, por |  | Prueba de usabilidad: un administrador debe ser capaz de interpretar la gráfica correctamente sin instrucciones adicionales en < 2 minutos. |  |  |
|  |  |  |  |  |  |  |  | SKU y sucursal, una gráfica de |  |  |  |  |
|  |  |  |  |  |  |  |  | serie de tiempo con el historial |  |  |  |  |
|  |  |  |  |  |  |  |  | de ventas de las últimas 12 |  |  |  |  |
|  |  |  |  |  |  |  |  | semanas y la proyección de las |  |  |  |  |
|  |  |  |  |  |  |  |  | próximas 4 semanas. Las |  |  |  |  |
|  |  |  |  |  |  |  |  | bandas de confianza deben ser |  |  |  |  |
|  |  |  |  |  |  |  |  | visibles y diferenciadas del valor |  |  |  |  |
|  |  |  |  |  |  |  |  | central. |  |  |  |  |
|  | RF- |  | Alta |  | Registro de |  |  | El Administrador puede registrar |  |  | Prueba funcional: |  |
|  | 06 |  |  |  | Venta Real |  |  | manualmente la venta real de la |  |  | registrar venta real, |  |


| RF- |
| --- |
| 01 |


| Ingesta de Datos |
| --- |
| (ETL) |


| Prueba de integración: |
| --- |
| ejecutar ETL con datos |
| de prueba, verificar |
| que la tabla de ventas |
| se actualice |
| correctamente sin |
| duplicados. |


| RF- |
| --- |
| 02 |


| Validación de |
| --- |
| Datos |


| Prueba unitaria: cargar |
| --- |
| dataset con 8 semanas |
| de historia; el sistema |
| debe rechazar la |
| predicción e indicar el |
| motivo. |


| RF- |
| --- |
| 03 |


| Generación de |
| --- |
| Predicción |


| Prueba de aceptación: |
| --- |
| el MAPE del modelo |
| sobre el conjunto de |
| validación debe ser ≤ |
| 20% en al menos el |
| 70% de los SKU piloto. |


| RF- |
| --- |
| 04 |


| Alertas de |
| --- |
| Quiebre de |
| Stock |


| Prueba funcional: |
| --- |
| insertar un SKU con |
| stock < demanda |
| proyectada; verificar |
| que la alerta aparece |
| en menos de 5 |
| segundos. |


| RF- |
| --- |
| 05 |


| Visualización de |
| --- |
| Tendencias |


| Prueba de usabilidad: |
| --- |
| un administrador debe |
| ser capaz de |
| interpretar la gráfica |
| correctamente sin |
| instrucciones |
| adicionales en < 2 |
| minutos. |



<!-- Página 8 -->
SRS — Sistema Inteligente de Predicción de Demanda | MiniMarket La 24 S.A.S. | v2.0
semana cerrada para cada SKU. verificar que el MAE de
Este dato se almacena para la predicción
calcular el error del modelo y correspondiente se
disparar el proceso de actualiza en la vista de
reentrenamiento. métricas del modelo.
RF- Media Evaluación y Cada vez que se registren Prueba de regresión:
07 Reentrenamiento ventas reales de al menos 4 tras reentrenamiento,
del Modelo semanas nuevas, el sistema el nuevo modelo no
debe ejecutar un ciclo de debe presentar un
reentrenamiento automático, MAPE mayor en más
versionando el modelo anterior y del 5% al modelo
registrando las métricas de previo sobre el mismo
ambas versiones para conjunto de validación.
comparación.
RF- Baja Ajuste Manual El Administrador puede Prueba funcional:
08 de Predicción sobreescribir la predicción aplicar ajuste manual,
generada por el modelo para verificar que el campo
una semana específica, 'AjusteManual' queda
justificando el ajuste (campo de en true y la cantidad
texto). El ajuste queda ajustada se usa en los
registrado como 'manual' y no cálculos de alerta.
afecta el modelo.
RF- Media Comparación La Gerencia puede visualizar, en Prueba de aceptación:
09 entre Sucursales una vista de resumen, la seleccionar un SKU
(Gerencia) demanda proyectada y el error con datos de al menos
histórico del modelo por sucursal 2 sucursales; la vista
para un SKU dado, permitiendo debe renderizar la
identificar sucursales con comparativa
patrones atípicos. correctamente.
Universidad — Ingeniería de Software | Abril 2024 Página 8 de 16

### Tablas detectadas en esta sección:
|  |  |  |  | semana cerrada para cada SKU. |  |  | verificar que el MAE de |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  | Este dato se almacena para |  |  | la predicción |  |
|  |  |  |  | calcular el error del modelo y |  |  | correspondiente se |  |
|  |  |  |  | disparar el proceso de |  |  | actualiza en la vista de |  |
|  |  |  |  | reentrenamiento. |  |  | métricas del modelo. |  |
| RF- 07 | Media | Evaluación y Reentrenamiento del Modelo |  | Cada vez que se registren |  | Prueba de regresión: tras reentrenamiento, el nuevo modelo no debe presentar un MAPE mayor en más del 5% al modelo previo sobre el mismo conjunto de validación. |  |  |
|  |  |  |  | ventas reales de al menos 4 |  |  |  |  |
|  |  |  |  | semanas nuevas, el sistema |  |  |  |  |
|  |  |  |  | debe ejecutar un ciclo de |  |  |  |  |
|  |  |  |  | reentrenamiento automático, |  |  |  |  |
|  |  |  |  | versionando el modelo anterior y |  |  |  |  |
|  |  |  |  | registrando las métricas de |  |  |  |  |
|  |  |  |  | ambas versiones para |  |  |  |  |
|  |  |  |  | comparación. |  |  |  |  |
| RF- 08 | Baja | Ajuste Manual de Predicción |  | El Administrador puede |  | Prueba funcional: aplicar ajuste manual, verificar que el campo 'AjusteManual' queda en true y la cantidad ajustada se usa en los cálculos de alerta. |  |  |
|  |  |  |  | sobreescribir la predicción |  |  |  |  |
|  |  |  |  | generada por el modelo para |  |  |  |  |
|  |  |  |  | una semana específica, |  |  |  |  |
|  |  |  |  | justificando el ajuste (campo de |  |  |  |  |
|  |  |  |  | texto). El ajuste queda |  |  |  |  |
|  |  |  |  | registrado como 'manual' y no |  |  |  |  |
|  |  |  |  | afecta el modelo. |  |  |  |  |
| RF- 09 | Media | Comparación entre Sucursales (Gerencia) |  | La Gerencia puede visualizar, en |  |  | Prueba de aceptación: |  |
|  |  |  |  | una vista de resumen, la |  |  | seleccionar un SKU |  |
|  |  |  |  | demanda proyectada y el error |  |  | con datos de al menos |  |
|  |  |  |  | histórico del modelo por sucursal |  |  | 2 sucursales; la vista |  |
|  |  |  |  | para un SKU dado, permitiendo |  |  | debe renderizar la |  |
|  |  |  |  | identificar sucursales con |  |  | comparativa |  |
|  |  |  |  | patrones atípicos. |  |  | correctamente. |  |


| RF- |
| --- |
| 07 |


| Evaluación y |
| --- |
| Reentrenamiento |
| del Modelo |


| Prueba de regresión: |
| --- |
| tras reentrenamiento, |
| el nuevo modelo no |
| debe presentar un |
| MAPE mayor en más |
| del 5% al modelo |
| previo sobre el mismo |
| conjunto de validación. |


| RF- |
| --- |
| 08 |


| Ajuste Manual |
| --- |
| de Predicción |


| Prueba funcional: |
| --- |
| aplicar ajuste manual, |
| verificar que el campo |
| 'AjusteManual' queda |
| en true y la cantidad |
| ajustada se usa en los |
| cálculos de alerta. |


| RF- |
| --- |
| 09 |


| Comparación |
| --- |
| entre Sucursales |
| (Gerencia) |



<!-- Página 9 -->
SRS — Sistema Inteligente de Predicción de Demanda | MiniMarket La 24 S.A.S. | v2.0
4. Requerimientos No Funcionales
ID Categoría Especificación
RNF- Rendimiento El sistema debe generar predicciones para todos los SKU activos en un
01 tiempo ≤ 30 segundos bajo carga normal (≤ 10 usuarios concurrentes).
RNF- Disponibilidad El sistema debe estar disponible el 99% del tiempo en horario operativo
02 (lunes a domingo, 6:00–23:00). Las ventanas de mantenimiento
planificado se notificarán con 24 horas de anticipación.
RNF- Usabilidad La interfaz debe ser comprensible para un administrador sin formación
03 técnica. El tiempo de aprendizaje para las funciones principales no debe
superar 2 horas con el manual de usuario incluido.
RNF- Mantenibilidad El código fuente debe seguir principios SOLID, contar con cobertura de
04 pruebas unitarias ≥ 70% y estar documentado con docstrings/JSDoc.
Los modelos entrenados deben ser versionados con MLflow o
equivalente.
RNF- Escalabilidad La arquitectura debe permitir incorporar nuevos SKU o sucursales sin
05 modificar el núcleo del sistema. La adición de un nuevo SKU debe
requerir solo la configuración de datos, no cambios en el código.
RNF- Seguridad El acceso al sistema debe requerir autenticación por usuario/contraseña.
06 Los datos de ventas en tránsito deben ir cifrados (HTTPS/TLS 1.2+). No
se almacenarán contraseñas en texto plano.
RNF- Confiabilidad Cuando el modelo no alcance el umbral de confianza establecido (MAPE
07 del Modelo > 25% en el conjunto de validación), el sistema debe mostrar la etiqueta
'PREDICCIÓN DE BAJA CONFIANZA' junto al resultado.
RNF- Portabilidad El sistema debe ser desplegable en Linux (Ubuntu 22.04+) y en
08 contenedor Docker, sin dependencias de software comercial.
RNF- Trazabilidad Toda predicción generada debe quedar registrada en base de datos con:
09 timestamp, versión del modelo, parámetros de entrada y resultado. Esta
traza no puede ser borrada por ningún actor.
Universidad — Ingeniería de Software | Abril 2024 Página 9 de 16

### Tablas detectadas en esta sección:
|  | ID |  |  | Categoría |  |  | Especificación |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | RNF- |  | Rendimiento |  |  |  | El sistema debe generar predicciones para todos los SKU activos en un |  |
|  | 01 |  |  |  |  |  | tiempo ≤ 30 segundos bajo carga normal (≤ 10 usuarios concurrentes). |  |
| RNF- 02 |  |  | Disponibilidad |  |  |  | El sistema debe estar disponible el 99% del tiempo en horario operativo |  |
|  |  |  |  |  |  |  | (lunes a domingo, 6:00–23:00). Las ventanas de mantenimiento |  |
|  |  |  |  |  |  |  | planificado se notificarán con 24 horas de anticipación. |  |
| RNF- 03 |  |  | Usabilidad |  |  |  | La interfaz debe ser comprensible para un administrador sin formación |  |
|  |  |  |  |  |  |  | técnica. El tiempo de aprendizaje para las funciones principales no debe |  |
|  |  |  |  |  |  |  | superar 2 horas con el manual de usuario incluido. |  |
| RNF- 04 |  |  | Mantenibilidad |  |  |  | El código fuente debe seguir principios SOLID, contar con cobertura de |  |
|  |  |  |  |  |  |  | pruebas unitarias ≥ 70% y estar documentado con docstrings/JSDoc. |  |
|  |  |  |  |  |  |  | Los modelos entrenados deben ser versionados con MLflow o |  |
|  |  |  |  |  |  |  | equivalente. |  |
| RNF- 05 |  |  | Escalabilidad |  |  |  | La arquitectura debe permitir incorporar nuevos SKU o sucursales sin |  |
|  |  |  |  |  |  |  | modificar el núcleo del sistema. La adición de un nuevo SKU debe |  |
|  |  |  |  |  |  |  | requerir solo la configuración de datos, no cambios en el código. |  |
| RNF- 06 |  |  | Seguridad |  |  |  | El acceso al sistema debe requerir autenticación por usuario/contraseña. |  |
|  |  |  |  |  |  |  | Los datos de ventas en tránsito deben ir cifrados (HTTPS/TLS 1.2+). No |  |
|  |  |  |  |  |  |  | se almacenarán contraseñas en texto plano. |  |
| RNF- 07 |  |  | Confiabilidad del Modelo |  |  |  | Cuando el modelo no alcance el umbral de confianza establecido (MAPE |  |
|  |  |  |  |  |  |  | > 25% en el conjunto de validación), el sistema debe mostrar la etiqueta |  |
|  |  |  |  |  |  |  | 'PREDICCIÓN DE BAJA CONFIANZA' junto al resultado. |  |
|  | RNF- |  | Portabilidad |  |  |  | El sistema debe ser desplegable en Linux (Ubuntu 22.04+) y en |  |
|  | 08 |  |  |  |  |  | contenedor Docker, sin dependencias de software comercial. |  |
| RNF- 09 |  |  | Trazabilidad |  |  |  | Toda predicción generada debe quedar registrada en base de datos con: |  |
|  |  |  |  |  |  |  | timestamp, versión del modelo, parámetros de entrada y resultado. Esta |  |
|  |  |  |  |  |  |  | traza no puede ser borrada por ningún actor. |  |


| RNF- |
| --- |
| 02 |


| RNF- |
| --- |
| 03 |


| RNF- |
| --- |
| 04 |


| RNF- |
| --- |
| 05 |


| RNF- |
| --- |
| 06 |


| RNF- |
| --- |
| 07 |


| Confiabilidad |
| --- |
| del Modelo |


| RNF- |
| --- |
| 09 |



<!-- Página 10 -->
SRS — Sistema Inteligente de Predicción de Demanda | MiniMarket La 24 S.A.S. | v2.0
5. Modelado del Sistema
5.1 Casos de Uso Principales
El flujo principal del sistema sigue la secuencia: el Administrador solicita una predicción → el sistema
ejecuta el ETL incremental → valida calidad de datos → entrena o recupera el modelo vigente → genera
predicciones con intervalos de confianza → evalúa si la predicción es confiable → muestra el resultado.
Si la demanda proyectada supera el stock, se genera una alerta. Paralelamente, la Gerencia accede a
vistas de tendencias y comparativas entre sucursales, y el Área Financiera consulta métricas de
precisión del modelo.
5.2 Modelo de Dominio — Entidades Principales
Entidad Atributos Clave Métodos / Responsabilidades
Producto (SKU) IdProducto: int, Nombre: String, obtenerCategoría(), verificarStock(),
Categoría: String, UnidadMedida: calcularBrechaStock()
String, StockActual: int, StockMínimo:
int, Activo: boolean
VentaHistórica IdVenta: int, Fecha: Date, Cantidad: obtenerSemana(), calcularTotal(),
int, PrecioUnitario: double, esDatoVálido()
IdProducto: int, IdSucursal: int
ModeloPredictivo IdModelo: int, Tipo: String (ej. entrenar(), predecir(), reentrenar(),
SARIMA, XGBoost), Versión: String, exportarMétricas()
FechaEntrenamiento: Date,
Parámetros: JSON, Estado: String,
MAPE: double, MAE: double
Predicción IdPredicción: int, IdModelo: int, aplicarAjuste(),
IdProducto: int, IdSucursal: int, compararConVentaReal(),
CantidadEstimada: int, LímiteInferior: calcularError()
int, LímiteSuperior: int,
FechaGeneración: Date,
AjusteManual: boolean,
CantidadAjustada: int
Alerta IdAlerta: int, IdPredicción: int, marcarAtendida(), notificar(),
IdProducto: int, IdSucursal: int, Tipo: generarResumen()
String, Mensaje: String,
FechaGeneración: Date, Atendida:
boolean
Sucursal IdSucursal: int, Nombre: String, obtenerSKUsActivos(),
Dirección: String, Activa: boolean obtenerHistorial()
5.3 Flujo del Proceso Principal
El proceso de predicción sigue estos pasos en secuencia:
• El sistema recibe una solicitud de predicción (manual o automática programada).
• Se ejecuta el ETL incremental: se extraen solo los registros nuevos desde la última ejecución.
Universidad — Ingeniería de Software | Abril 2024 Página 10 de 16

### Tablas detectadas en esta sección:
|  | Entidad |  |  | Atributos Clave |  |  | Métodos / Responsabilidades |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Producto (SKU) |  |  |  | IdProducto: int, Nombre: String, |  | obtenerCategoría(), verificarStock(), calcularBrechaStock() |  |  |
|  |  |  |  | Categoría: String, UnidadMedida: |  |  |  |  |
|  |  |  |  | String, StockActual: int, StockMínimo: |  |  |  |  |
|  |  |  |  | int, Activo: boolean |  |  |  |  |
| VentaHistórica |  |  |  | IdVenta: int, Fecha: Date, Cantidad: |  | obtenerSemana(), calcularTotal(), esDatoVálido() |  |  |
|  |  |  |  | int, PrecioUnitario: double, |  |  |  |  |
|  |  |  |  | IdProducto: int, IdSucursal: int |  |  |  |  |
| ModeloPredictivo |  |  |  | IdModelo: int, Tipo: String (ej. |  | entrenar(), predecir(), reentrenar(), exportarMétricas() |  |  |
|  |  |  |  | SARIMA, XGBoost), Versión: String, |  |  |  |  |
|  |  |  |  | FechaEntrenamiento: Date, |  |  |  |  |
|  |  |  |  | Parámetros: JSON, Estado: String, |  |  |  |  |
|  |  |  |  | MAPE: double, MAE: double |  |  |  |  |
| Predicción |  |  |  | IdPredicción: int, IdModelo: int, |  | aplicarAjuste(), compararConVentaReal(), calcularError() |  |  |
|  |  |  |  | IdProducto: int, IdSucursal: int, |  |  |  |  |
|  |  |  |  | CantidadEstimada: int, LímiteInferior: |  |  |  |  |
|  |  |  |  | int, LímiteSuperior: int, |  |  |  |  |
|  |  |  |  | FechaGeneración: Date, |  |  |  |  |
|  |  |  |  | AjusteManual: boolean, |  |  |  |  |
|  |  |  |  | CantidadAjustada: int |  |  |  |  |
| Alerta |  |  |  | IdAlerta: int, IdPredicción: int, |  | marcarAtendida(), notificar(), generarResumen() |  |  |
|  |  |  |  | IdProducto: int, IdSucursal: int, Tipo: |  |  |  |  |
|  |  |  |  | String, Mensaje: String, |  |  |  |  |
|  |  |  |  | FechaGeneración: Date, Atendida: |  |  |  |  |
|  |  |  |  | boolean |  |  |  |  |
| Sucursal |  |  |  | IdSucursal: int, Nombre: String, |  |  | obtenerSKUsActivos(), |  |
|  |  |  |  | Dirección: String, Activa: boolean |  |  | obtenerHistorial() |  |


| obtenerCategoría(), verificarStock(), |
| --- |
| calcularBrechaStock() |


| obtenerSemana(), calcularTotal(), |
| --- |
| esDatoVálido() |


| entrenar(), predecir(), reentrenar(), |
| --- |
| exportarMétricas() |


| aplicarAjuste(), |
| --- |
| compararConVentaReal(), |
| calcularError() |


| marcarAtendida(), notificar(), |
| --- |
| generarResumen() |



<!-- Página 11 -->
SRS — Sistema Inteligente de Predicción de Demanda | MiniMarket La 24 S.A.S. | v2.0
• Se valida la calidad de los datos: si hay menos de 12 semanas por SKU, el proceso se detiene
con mensaje de error descriptivo.
• Si existe un modelo vigente entrenado recientemente (< 7 días), se recupera. Si no, se entrena
uno nuevo.
• El modelo genera las predicciones para la próxima semana (y opcionalmente 2–4 semanas).
• Se evalúa la confianza: si MAPE > 25%, se etiqueta como 'baja confianza'.
• Se compara la predicción con el stock actual: si hay déficit proyectado, se genera una alerta.
• Los resultados se persisten en base de datos y se renderizan en la interfaz web.
Universidad — Ingeniería de Software | Abril 2024 Página 11 de 16


<!-- Página 12 -->
SRS — Sistema Inteligente de Predicción de Demanda | MiniMarket La 24 S.A.S. | v2.0
6. Arquitectura Propuesta
6.1 Estilo Arquitectónico
La arquitectura propuesta sigue el patrón Hexagonal (Ports & Adapters) combinado con una separación
en tres capas lógicas: Módulo de Datos (ETL + repositorios), Módulo Analítico (modelo de IA,
entrenamiento, predicción) y Módulo de Presentación (API REST + interfaz web). Este estilo garantiza
que el núcleo analítico sea independiente de la fuente de datos y de la capa de presentación, facilitando
reemplazar cualquier componente sin afectar los demás.
6.2 Componentes del Sistema
RF/RNF
Componente Responsabilidad Tecnología Sugerida
Relacionados
ETL Service Extracción incremental desde Python + SQLAlchemy RF-01, RF-02,
el sistema de facturación, / Pandas RNF-05
limpieza y carga en el data
warehouse.
Data Store Almacenamiento de datos PostgreSQL / SQLite RF-01 – RF-09,
históricos, predicciones, (piloto) RNF-09
alertas y métricas.
ML Engine Entrenamiento, Python + scikit-learn / RF-03, RF-07,
versionamiento y ejecución de statsmodels + MLflow RNF-04, RNF-07
modelos predictivos.
Alert Engine Comparación de predicción Python (microservicio) RF-04, RNF-01
vs. stock, generación y
persistencia de alertas.
REST API Capa de exposición de FastAPI (Python) Todos los RF,
servicios al frontend y RNF-02, RNF-06
sistemas externos.
Web Dashboard Interfaz de usuario para React.js / Vue.js (SPA) RF-04, RF-05, RF-
administradores y gerencia. 08, RF-09, RNF-03
Auth Service Gestión de sesiones, JWT + bcrypt RNF-06
autenticación y autorización
por roles.
6.3 Principios de Diseño Aplicados
• Separación de responsabilidades (SRP): cada componente tiene una única razón de cambio.
• Desacoplamiento: el ML Engine no conoce el sistema de facturación; solo interactúa con el
Data Store.
• Versionamiento de modelos: cada ciclo de entrenamiento genera una nueva versión registrada
con sus métricas, sin sobrescribir la anterior.
• Configuración sobre código: los parámetros del modelo (hiperparámetros, umbrales, SKU
piloto) se definen en archivos de configuración, no en el código fuente.
Universidad — Ingeniería de Software | Abril 2024 Página 12 de 16

### Tablas detectadas en esta sección:
| Componente | Responsabilidad |  |  | Tecnología Sugerida |  | RF/RNF |  |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  | Relacionados |  |
| ETL Service |  | Extracción incremental desde |  | Python + SQLAlchemy / Pandas | RF-01, RF-02, RNF-05 |  |  |
|  |  | el sistema de facturación, |  |  |  |  |  |
|  |  | limpieza y carga en el data |  |  |  |  |  |
|  |  | warehouse. |  |  |  |  |  |
| Data Store |  | Almacenamiento de datos |  | PostgreSQL / SQLite (piloto) | RF-01 – RF-09, RNF-09 |  |  |
|  |  | históricos, predicciones, |  |  |  |  |  |
|  |  | alertas y métricas. |  |  |  |  |  |
| ML Engine |  | Entrenamiento, |  | Python + scikit-learn / statsmodels + MLflow | RF-03, RF-07, RNF-04, RNF-07 |  |  |
|  |  | versionamiento y ejecución de |  |  |  |  |  |
|  |  | modelos predictivos. |  |  |  |  |  |
| Alert Engine |  | Comparación de predicción |  | Python (microservicio) | RF-04, RNF-01 |  |  |
|  |  | vs. stock, generación y |  |  |  |  |  |
|  |  | persistencia de alertas. |  |  |  |  |  |
| REST API |  | Capa de exposición de |  | FastAPI (Python) | Todos los RF, RNF-02, RNF-06 |  |  |
|  |  | servicios al frontend y |  |  |  |  |  |
|  |  | sistemas externos. |  |  |  |  |  |
| Web Dashboard |  | Interfaz de usuario para |  | React.js / Vue.js (SPA) |  | RF-04, RF-05, RF- |  |
|  |  | administradores y gerencia. |  |  |  | 08, RF-09, RNF-03 |  |
| Auth Service |  | Gestión de sesiones, |  | JWT + bcrypt | RNF-06 |  |  |
|  |  | autenticación y autorización |  |  |  |  |  |
|  |  | por roles. |  |  |  |  |  |


| Python + SQLAlchemy |
| --- |
| / Pandas |


| RF-01, RF-02, |
| --- |
| RNF-05 |


| PostgreSQL / SQLite |
| --- |
| (piloto) |


| RF-01 – RF-09, |
| --- |
| RNF-09 |


| Python + scikit-learn / |
| --- |
| statsmodels + MLflow |


| RF-03, RF-07, |
| --- |
| RNF-04, RNF-07 |


| Todos los RF, |
| --- |
| RNF-02, RNF-06 |



<!-- Página 13 -->
SRS — Sistema Inteligente de Predicción de Demanda | MiniMarket La 24 S.A.S. | v2.0
• Fail-safe: ante cualquier error en el ETL o el modelo, el sistema muestra el último resultado
válido y registra el incidente en el log de auditoría.
Universidad — Ingeniería de Software | Abril 2024 Página 13 de 16


<!-- Página 14 -->
SRS — Sistema Inteligente de Predicción de Demanda | MiniMarket La 24 S.A.S. | v2.0
7. Análisis de Riesgos
El siguiente registro identifica los riesgos más relevantes del proyecto, su nivel de impacto, descripción
y estrategias de mitigación. Los riesgos se revisarán al final de cada iteración de desarrollo.
Estrategia de
ID Nivel Nombre Descripción Relacionado
Mitigación
R- Alto Datos El sistema de facturación Ejecutar auditoría
01 históricos puede contener de datos en sprint
insuficientes o inconsistencias, SKUs 1. Definir criterio
de mala calidad fusionados o periodos sin mínimo de 12
registros. semanas por
SKU. Implementar
RF-02 con
mensajes claros.
R- Alto Baja adopción Resistencia cultural al Presentar el
02 por parte de los cambio; percepción de sistema como
administradores amenaza a la autonomía. 'herramienta de
apoyo', no de
control. Involucrar
a un
administrador
líder como
champion desde
sprint 2.
R- Medio Overfitting del Con pocos SKU, el Usar validación
03 modelo en modelo puede ajustarse walk-forward
datos de piloto demasiado al histórico y (time-series split).
fallar en nuevos patrones. Implementar
umbral de baja
confianza (RNF-
07).
R- Medio Cambios en el Una actualización del Diseñar el ETL
04 sistema de sistema fuente puede con adaptadores
facturación romper el conector ETL. intercambiables.
Definir contrato de
datos estable
documentado.
R- Bajo Sobreconfianza Gerencia podría tomar Documentar
05 en las decisiones de inversión explícitamente las
predicciones basadas únicamente en limitaciones del
el modelo sin criterio modelo. Los
humano. intervalos de
confianza son
obligatorios en
toda vista (RF-
03).
R- Bajo Deuda técnica Presión de tiempo puede Aplicar revisiones
06 por entrega de llevar a comprometer la de código
piloto calidad del código. semanales.
Mantener
cobertura de
Universidad — Ingeniería de Software | Abril 2024 Página 14 de 16

### Tablas detectadas en esta sección:
| ID | Nivel | Nombre | Descripción |  | Estrategia de |  | Relacionado |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  | Mitigación |  |  |
| R- 01 | Alto | Datos históricos insuficientes o de mala calidad | El sistema de facturación puede contener inconsistencias, SKUs fusionados o periodos sin registros. |  | Ejecutar auditoría |  |  |
|  |  |  |  |  | de datos en sprint |  |  |
|  |  |  |  |  | 1. Definir criterio |  |  |
|  |  |  |  |  | mínimo de 12 |  |  |
|  |  |  |  |  | semanas por |  |  |
|  |  |  |  |  | SKU. Implementar |  |  |
|  |  |  |  |  | RF-02 con |  |  |
|  |  |  |  |  | mensajes claros. |  |  |
| R- 02 | Alto | Baja adopción por parte de los administradores | Resistencia cultural al cambio; percepción de amenaza a la autonomía. |  | Presentar el |  |  |
|  |  |  |  |  | sistema como |  |  |
|  |  |  |  |  | 'herramienta de |  |  |
|  |  |  |  |  | apoyo', no de |  |  |
|  |  |  |  |  | control. Involucrar |  |  |
|  |  |  |  |  | a un |  |  |
|  |  |  |  |  | administrador |  |  |
|  |  |  |  |  | líder como |  |  |
|  |  |  |  |  | champion desde |  |  |
|  |  |  |  |  | sprint 2. |  |  |
| R- 03 | Medio | Overfitting del modelo en datos de piloto | Con pocos SKU, el modelo puede ajustarse demasiado al histórico y fallar en nuevos patrones. |  | Usar validación |  |  |
|  |  |  |  |  | walk-forward |  |  |
|  |  |  |  |  | (time-series split). |  |  |
|  |  |  |  |  | Implementar |  |  |
|  |  |  |  |  | umbral de baja |  |  |
|  |  |  |  |  | confianza (RNF- |  |  |
|  |  |  |  |  | 07). |  |  |
| R- 04 | Medio | Cambios en el sistema de facturación | Una actualización del sistema fuente puede romper el conector ETL. |  | Diseñar el ETL |  |  |
|  |  |  |  |  | con adaptadores |  |  |
|  |  |  |  |  | intercambiables. |  |  |
|  |  |  |  |  | Definir contrato de |  |  |
|  |  |  |  |  | datos estable |  |  |
|  |  |  |  |  | documentado. |  |  |
| R- 05 | Bajo | Sobreconfianza en las predicciones | Gerencia podría tomar decisiones de inversión basadas únicamente en el modelo sin criterio humano. |  | Documentar |  |  |
|  |  |  |  |  | explícitamente las |  |  |
|  |  |  |  |  | limitaciones del |  |  |
|  |  |  |  |  | modelo. Los |  |  |
|  |  |  |  |  | intervalos de |  |  |
|  |  |  |  |  | confianza son |  |  |
|  |  |  |  |  | obligatorios en |  |  |
|  |  |  |  |  | toda vista (RF- |  |  |
|  |  |  |  |  | 03). |  |  |
| R- 06 | Bajo | Deuda técnica por entrega de piloto | Presión de tiempo puede llevar a comprometer la calidad del código. |  | Aplicar revisiones |  |  |
|  |  |  |  |  | de código |  |  |
|  |  |  |  |  | semanales. |  |  |
|  |  |  |  |  | Mantener |  |  |
|  |  |  |  |  | cobertura de |  |  |


| R- |
| --- |
| 01 |


| Datos |
| --- |
| históricos |
| insuficientes o |
| de mala calidad |


| El sistema de facturación |
| --- |
| puede contener |
| inconsistencias, SKUs |
| fusionados o periodos sin |
| registros. |


| R- |
| --- |
| 02 |


| Baja adopción |
| --- |
| por parte de los |
| administradores |


| Resistencia cultural al |
| --- |
| cambio; percepción de |
| amenaza a la autonomía. |


| R- |
| --- |
| 03 |


| Overfitting del |
| --- |
| modelo en |
| datos de piloto |


| Con pocos SKU, el |
| --- |
| modelo puede ajustarse |
| demasiado al histórico y |
| fallar en nuevos patrones. |


| R- |
| --- |
| 04 |


| Cambios en el |
| --- |
| sistema de |
| facturación |


| Una actualización del |
| --- |
| sistema fuente puede |
| romper el conector ETL. |


| R- |
| --- |
| 05 |


| Sobreconfianza |
| --- |
| en las |
| predicciones |


| Gerencia podría tomar |
| --- |
| decisiones de inversión |
| basadas únicamente en |
| el modelo sin criterio |
| humano. |


| R- |
| --- |
| 06 |


| Deuda técnica |
| --- |
| por entrega de |
| piloto |


| Presión de tiempo puede |
| --- |
| llevar a comprometer la |
| calidad del código. |



<!-- Página 15 -->
SRS — Sistema Inteligente de Predicción de Demanda | MiniMarket La 24 S.A.S. | v2.0
pruebas ≥ 70%
(RNF-04) desde
el inicio.
Universidad — Ingeniería de Software | Abril 2024 Página 15 de 16

### Tablas detectadas en esta sección:
|  |  |  |  |  | pruebas ≥ 70% |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  | (RNF-04) desde |  |  |
|  |  |  |  |  | el inicio. |  |  |



<!-- Página 16 -->
SRS — Sistema Inteligente de Predicción de Demanda | MiniMarket La 24 S.A.S. | v2.0
8. Criterios de Aceptación del Piloto
El piloto se considerará exitoso si se cumplen los siguientes criterios al finalizar el periodo de evaluación
(4 semanas de operación real):
ID Criterio Métrica de Medición Umbral de Éxito
CA-01 Precisión del modelo de predicción MAPE sobre conjunto ≤ 20% en al menos el
de validación hold-out 70% de los SKU piloto
CA-02 Reducción de quiebres de stock Comparativa de Reducción ≥ 15%
incidentes de quiebre respecto a la línea
semana a semana base pre-piloto
CA-03 Reducción de sobrestock en Unidades de producto Reducción ≥ 10%
perecederos vencido o en respecto a la línea
promoción urgente base pre-piloto
CA-04 Adopción por administradores % de semanas en que ≥ 80% de las semanas
el administrador del piloto
consulta la predicción
CA-05 Disponibilidad del sistema % de tiempo operativo ≥ 99% conforme a
en horario definido RNF-02
CA-06 Tiempo de generación de Segundos desde la ≤ 30 segundos
predicciones solicitud hasta la conforme a RNF-01
visualización del
resultado
8.1 Estrategia de Validación
La validación del modelo se realizará mediante validación cruzada temporal (walk-forward validation):
se entrenará el modelo con los primeros N períodos y se evaluará sobre los M períodos siguientes,
avanzando semana a semana. Este enfoque replica fielmente el escenario de uso real y evita el data
leakage propio de la validación cruzada estándar en series de tiempo.
Las métricas principales serán MAPE (para evaluar el error relativo, comparables entre SKU de distinto
volumen) y MAE (para entender el error absoluto en unidades). Adicionalmente, se registrará el Bias
(sesgo sistemático) para detectar si el modelo tiende a sobreestimar o subestimar de forma consistente.
Universidad — Ingeniería de Software | Abril 2024 Página 16 de 16

### Tablas detectadas en esta sección:
|  | ID |  |  | Criterio |  |  | Métrica de Medición |  |  | Umbral de Éxito |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CA-01 |  |  | Precisión del modelo de predicción |  |  |  | MAPE sobre conjunto |  |  | ≤ 20% en al menos el |  |
|  |  |  |  |  |  |  | de validación hold-out |  |  | 70% de los SKU piloto |  |
| CA-02 |  |  | Reducción de quiebres de stock |  |  |  | Comparativa de |  |  | Reducción ≥ 15% |  |
|  |  |  |  |  |  |  | incidentes de quiebre |  |  | respecto a la línea |  |
|  |  |  |  |  |  |  | semana a semana |  |  | base pre-piloto |  |
| CA-03 |  |  | Reducción de sobrestock en perecederos |  |  |  | Unidades de producto |  |  | Reducción ≥ 10% |  |
|  |  |  |  |  |  |  | vencido o en |  |  | respecto a la línea |  |
|  |  |  |  |  |  |  | promoción urgente |  |  | base pre-piloto |  |
| CA-04 |  |  | Adopción por administradores |  |  |  | % de semanas en que |  | ≥ 80% de las semanas del piloto |  |  |
|  |  |  |  |  |  |  | el administrador |  |  |  |  |
|  |  |  |  |  |  |  | consulta la predicción |  |  |  |  |
| CA-05 |  |  | Disponibilidad del sistema |  |  |  | % de tiempo operativo |  |  | ≥ 99% conforme a |  |
|  |  |  |  |  |  |  | en horario definido |  |  | RNF-02 |  |
| CA-06 |  |  | Tiempo de generación de predicciones |  |  |  | Segundos desde la |  | ≤ 30 segundos conforme a RNF-01 |  |  |
|  |  |  |  |  |  |  | solicitud hasta la |  |  |  |  |
|  |  |  |  |  |  |  | visualización del |  |  |  |  |
|  |  |  |  |  |  |  | resultado |  |  |  |  |


| Reducción de sobrestock en |
| --- |
| perecederos |


| ≥ 80% de las semanas |
| --- |
| del piloto |


| Tiempo de generación de |
| --- |
| predicciones |


| ≤ 30 segundos |
| --- |
| conforme a RNF-01 |


