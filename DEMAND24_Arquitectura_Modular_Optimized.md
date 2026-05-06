<!-- Página 1 -->
DEMAND-24
Sistema Inteligente de Predicción de Demanda
MiniMarket La 24 S.A.S.
ARQUITECTURA MODULAR DETALLADA
Documento de Diseño de Software · Versión 1.0
Abril 2025
Proyecto DEMAND-24 — Predicción de Demanda
Cliente MiniMarket La 24 S.A.S.
Equipo Reyes · Blanco · Valencia · Pereira · Corpas
Versión SRS 2.0 (04/04/2025)
Clasificación Confidencial — Solo distribución interna

### Tablas detectadas en esta sección:
| DEMAND-24 Sistema Inteligente de Predicción de Demanda MiniMarket La 24 S.A.S. ARQUITECTURA MODULAR DETALLADA |
| --- |
| Documento de Diseño de Software · Versión 1.0 Abril 2025 Proyecto DEMAND-24 — Predicción de Demanda Cliente MiniMarket La 24 S.A.S. Equipo Reyes · Blanco · Valencia · Pereira · Corpas Versión SRS 2.0 (04/04/2025) Clasificación Confidencial — Solo distribución interna |



<!-- Página 2 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
SECCIÓN
TABLA DE CONTENIDO
1. Visión General del Sistema
1
.
1 Propósito y Alcance
1
.
2 Principios Arquitectónicos
1
.
3 Stack Tecnológico Global
2. Módulo ETL — Ingesta y Validación de Datos
2
.
1 Responsabilidades
2
.
2 Componentes Internos
2
.
3 Flujo de Datos
2
.
4 Tecnologías
3. Módulo de Almacenamiento — Data Store
3
.
1 Estrategia de Persistencia
3
.
2 Esquema de Entidades
3
.
3 Tecnologías
4. Módulo ML Engine — Motor de IA
4
.
1 Pipeline de Machine Learning
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 2


<!-- Página 3 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
4
.
2 Algoritmos y Selección de Modelo
4
.
3 Versionamiento MLflow
4
.
4 Tecnologías Python
5. Módulo Alert Engine — Motor de Alertas
5
.
1 Lógica de Detección
5
.
2 Tipos de Alerta
5
.
3 Tecnologías
6. Módulo REST API — Capa de Servicios
6
.
1 Endpoints Principales
6
.
2 Autenticación y Seguridad
6
.
3 Tecnologías FastAPI
7. Módulo Auth Service — Autenticación
7
.
1 Flujo JWT
7
.
2 Gestión de Roles
7
.
3 Tecnologías
8. Módulo Web Dashboard — Interfaz de Usuario
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 3


<!-- Página 4 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
8
.
1 Vistas por Actor
8
.
2 Componentes UI
8
.
3 Tecnologías Frontend
9. Integración entre Módulos
9
.
1 Diagrama de Dependencias
9
.
2 Contratos de Datos
1
0. Despliegue e Infraestructura
1
0
.
1 Docker y Contenedores
1
0
.
2 Variables de Entorno
1
1. Trazabilidad de Requerimientos
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 4


<!-- Página 5 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
SECCIÓN 1
VISIÓN GENERAL DEL SISTEMA
Este documento define la arquitectura modular completa del sistema DEMAND-24. Cada módulo está descrito
con sus responsabilidades exactas, interfaces, flujos internos y el stack tecnológico que lo implementa. El
diseño sigue el patrón Hexagonal (Ports & Adapters) garantizando desacoplamiento máximo entre capas y
facilitando pruebas, mantenimiento y extensibilidad futura.
1.1 Propósito y Alcance
DEMAND-24 es un sistema analítico desacoplado que transforma datos históricos de facturación en
predicciones de demanda semanales accionables. El piloto opera sobre un subconjunto de SKU estratégicos
con integración de solo lectura al sistema de facturación existente.
IN SCOPE OUT OF SCOPE
Predicción semanal por SKU y sucursal Modificación del sistema de facturación
Alertas de quiebre de stock proyectado Gestión de compras o pedidos a proveedores
Dashboard de tendencias para gerencia Integración con ERP o sistemas de nómina
Reentrenamiento automático del modelo Predicción de precios o elasticidad
Versionamiento de modelos con MLflow Análisis de rentabilidad por categoría
1.2 Principios Arquitectónicos
Separación de Responsabilidades (SRP)
Cada módulo tiene una única razón de cambio. El ML Engine no conoce el sistema de facturación;
solo lee del Data Store. El ETL no conoce el modelo de IA.
Desacoplamiento (Hexagonal Architecture)
El núcleo analítico se comunica con el exterior únicamente mediante puertos (interfaces abstractas).
Los adaptadores concretos (PostgreSQL, Facturación) implementan esos puertos sin contaminar la
lógica de negocio.
Configuración sobre Código
Hiperparámetros, umbrales de confianza, lista de SKU piloto y credenciales se definen en archivos
YAML/ENV, nunca hardcodeados. Agregar un SKU no requiere modificar el código fuente.
Fail-Safe
Ante cualquier error en ETL o predicción, el sistema retorna el último resultado válido y registra el
incidente en el log de auditoría. Nunca muestra un estado inconsistente al usuario.
Versionamiento de Modelos
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 5

### Tablas detectadas en esta sección:
| IN SCOPE | OUT OF SCOPE |
| --- | --- |
| Predicción semanal por SKU y sucursal | Modificación del sistema de facturación |
| Alertas de quiebre de stock proyectado | Gestión de compras o pedidos a proveedores |
| Dashboard de tendencias para gerencia | Integración con ERP o sistemas de nómina |
| Reentrenamiento automático del modelo | Predicción de precios o elasticidad |
| Versionamiento de modelos con MLflow | Análisis de rentabilidad por categoría |


| Separación de Responsabilidades (SRP) |
| --- |
| Cada módulo tiene una única razón de cambio. El ML Engine no conoce el sistema de facturación; solo lee del Data Store. El ETL no conoce el modelo de IA. |


| Desacoplamiento (Hexagonal Architecture) |
| --- |
| El núcleo analítico se comunica con el exterior únicamente mediante puertos (interfaces abstractas). Los adaptadores concretos (PostgreSQL, Facturación) implementan esos puertos sin contaminar la lógica de negocio. |


| Configuración sobre Código |
| --- |
| Hiperparámetros, umbrales de confianza, lista de SKU piloto y credenciales se definen en archivos YAML/ENV, nunca hardcodeados. Agregar un SKU no requiere modificar el código fuente. |


| Fail-Safe |
| --- |
| Ante cualquier error en ETL o predicción, el sistema retorna el último resultado válido y registra el incidente en el log de auditoría. Nunca muestra un estado inconsistente al usuario. |



<!-- Página 6 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
Cada ciclo de entrenamiento genera una versión nueva registrada con sus métricas (MAPE, MAE,
Bias) sin sobrescribir la anterior. Rollback inmediato disponible.
Trazabilidad Total
Toda predicción queda registrada con timestamp, versión de modelo, parámetros de entrada y
resultado. Esta traza es inmutable para ningún actor del sistema.
Seguridad por Defecto
HTTPS/TLS en todas las comunicaciones, contraseñas con bcrypt, tokens JWT con expiración,
autorización basada en roles (RBAC).
1.3 Stack Tecnológico Global
La siguiente tabla resume el stack completo del sistema organizado por capa arquitectónica. Todas las
tecnologías son open-source y compatibles con despliegue en Linux Ubuntu 22.04+ y Docker.
Capa Tecnología Principal Versión Propósito
Recomendada
ETL / Ingesta Python + SQLAlchemy + Pandas 3.11+ / 2.0+ / 2.1+ Extracción incremental, limpieza y
carga de datos
Almacenamiento PostgreSQL 16 16.x Base de datos relacional principal
(schema provisto por cliente)
Machine Learning Python + scikit-learn + 3.11+ / 1.4+ / 0.14+ Entrenamiento, predicción y
statsmodels + MLflow / 2.x versionamiento de modelos
Motor de Alertas Python (microservicio) 3.11+ Comparación predicción vs. stock
y generación de alertas
API REST FastAPI + Uvicorn 0.110+ / 0.27+ Exposición de servicios REST con
documentación automática
Autenticación Python-JOSE + Passlib (bcrypt) latest JWT RS256, hashing seguro de
contraseñas
Frontend React.js + Recharts + Axios 18+ / 2.x / 1.x SPA interactiva con gráficas de
series temporales
Contenedor Docker + Docker Compose 24+ / 2.x Orquestación de servicios y
despliegue reproducible
Logging / Audit Python logging + structlog latest Logs estructurados en JSON para
auditoría y debugging
Testing pytest + pytest-cov + httpx 7+ / 4+ / 0.27+ Pruebas unitarias, de integración y
cobertura >= 70%
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 6

### Tablas detectadas en esta sección:
| Trazabilidad Total |
| --- |
| Toda predicción queda registrada con timestamp, versión de modelo, parámetros de entrada y resultado. Esta traza es inmutable para ningún actor del sistema. |


| Seguridad por Defecto |
| --- |
| HTTPS/TLS en todas las comunicaciones, contraseñas con bcrypt, tokens JWT con expiración, autorización basada en roles (RBAC). |


| Capa | Tecnología Principal | Versión Recomendada | Propósito |
| --- | --- | --- | --- |
| ETL / Ingesta | Python + SQLAlchemy + Pandas | 3.11+ / 2.0+ / 2.1+ | Extracción incremental, limpieza y carga de datos |
| Almacenamiento | PostgreSQL 16 | 16.x | Base de datos relacional principal (schema provisto por cliente) |
| Machine Learning | Python + scikit-learn + statsmodels + MLflow | 3.11+ / 1.4+ / 0.14+ / 2.x | Entrenamiento, predicción y versionamiento de modelos |
| Motor de Alertas | Python (microservicio) | 3.11+ | Comparación predicción vs. stock y generación de alertas |
| API REST | FastAPI + Uvicorn | 0.110+ / 0.27+ | Exposición de servicios REST con documentación automática |
| Autenticación | Python-JOSE + Passlib (bcrypt) | latest | JWT RS256, hashing seguro de contraseñas |
| Frontend | React.js + Recharts + Axios | 18+ / 2.x / 1.x | SPA interactiva con gráficas de series temporales |
| Contenedor | Docker + Docker Compose | 24+ / 2.x | Orquestación de servicios y despliegue reproducible |
| Logging / Audit | Python logging + structlog | latest | Logs estructurados en JSON para auditoría y debugging |
| Testing | pytest + pytest-cov + httpx | 7+ / 4+ / 0.27+ | Pruebas unitarias, de integración y cobertura >= 70% |



<!-- Página 7 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
SECCIÓN 2
MÓDULO ETL — INGESTA Y VALIDACIÓN DE DATOS
El módulo ETL (Extract, Transform, Load) es la puerta de entrada al sistema. Es el único componente
autorizado a comunicarse con el sistema de facturación externo, y lo hace en modo solo-lectura. Toda la
información que fluye hacia el ML Engine y el Data Store debe pasar por este módulo, asegurando consistencia
y trazabilidad desde el origen.
2.1 Responsabilidades del Módulo
(cid:127) Conectarse al sistema de facturación mediante credenciales de solo lectura configuradas en variables de
entorno.
(cid:127) Realizar extracción INCREMENTAL: consultar únicamente registros nuevos desde el timestamp de la última
ejecución exitosa (almacenado en la tabla etl_checkpoints del Data Store).
(cid:127) Aplicar transformaciones de limpieza: normalización de fechas, unificación de formatos de SKU, eliminación
de duplicados y corrección de tipos de datos.
(cid:127) Validar los datos antes de cargarlos: detectar nulos en campos críticos (fecha, SKU, cantidad), rangos
inválidos (cantidades negativas), y coherencia referencial.
(cid:127) Cargar los datos validados en la tabla ventas_historicas del Data Store.
(cid:127) Registrar cada ejecución ETL (éxito/fallo, registros procesados, timestamp) en la tabla etl_logs para auditoría.
(cid:127) En caso de error parcial, aplicar rollback transaccional y notificar al log de auditoría sin dejar datos
incompletos.
2.2 Componentes Internos
Componente Clase / Archivo Responsabilidad Específica
FacuracionConnector etl/connectors/facturacion.py Adaptador que implementa el puerto IDataSource.
Encapsula la conexión SQLAlchemy al sistema externo.
Configurable mediante DATABASE_SOURCE_URL en
.env.
IncrementalExtractor etl/extractors/incremental.py Lee el último checkpoint exitoso y construye la query SQL
con filtro temporal. Devuelve un DataFrame Pandas crudo.
DataCleaner etl/transformers/cleaner.py Pipeline de transformaciones: parseo de fechas, cast de
tipos, normalización de SKU codes, deduplicación por
(fecha, SKU, sucursal).
DataValidator etl/validators/quality.py Verifica: nulos en campos críticos, cantidades en rango [0,
MAX_QTY], existencia del SKU en catálogo, coherencia de
fechas. Lanza ETLValidationError con detalle si falla.
DataLoader etl/loaders/postgres_loader.p Carga el DataFrame validado en la tabla ventas_historicas
y usando upsert (INSERT ON CONFLICT DO UPDATE) para
idempotencia.
CheckpointManager etl/checkpoints/manager.py Lee y escribe el timestamp del último ETL exitoso en
etl_checkpoints. Garantiza que un ETL fallido no avance el
checkpoint.
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 7

### Tablas detectadas en esta sección:
| Componente | Clase / Archivo | Responsabilidad Específica |
| --- | --- | --- |
| FacuracionConnector | etl/connectors/facturacion.py | Adaptador que implementa el puerto IDataSource. Encapsula la conexión SQLAlchemy al sistema externo. Configurable mediante DATABASE_SOURCE_URL en .env. |
| IncrementalExtractor | etl/extractors/incremental.py | Lee el último checkpoint exitoso y construye la query SQL con filtro temporal. Devuelve un DataFrame Pandas crudo. |
| DataCleaner | etl/transformers/cleaner.py | Pipeline de transformaciones: parseo de fechas, cast de tipos, normalización de SKU codes, deduplicación por (fecha, SKU, sucursal). |
| DataValidator | etl/validators/quality.py | Verifica: nulos en campos críticos, cantidades en rango [0, MAX_QTY], existencia del SKU en catálogo, coherencia de fechas. Lanza ETLValidationError con detalle si falla. |
| DataLoader | etl/loaders/postgres_loader.p y | Carga el DataFrame validado en la tabla ventas_historicas usando upsert (INSERT ON CONFLICT DO UPDATE) para idempotencia. |
| CheckpointManager | etl/checkpoints/manager.py | Lee y escribe el timestamp del último ETL exitoso en etl_checkpoints. Garantiza que un ETL fallido no avance el checkpoint. |



<!-- Página 8 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
ETLOrchestrator etl/orchestrator.py Coordina el pipeline completo: Extract -> Clean -> Validate
-> Load -> Checkpoint. Maneja excepciones y rollback.
2.3 Flujo de Datos (ETL Pipeline)
PASO 1 · El ETLOrchestrator es invocado por el scheduler (APScheduler) o manualmente
TRIGGER vía endpoint POST /api/v1/etl/run.
PASO 2 · IncrementalExtractor consulta etl_checkpoints, construye query SQL: SELECT *
EXTRACT FROM ventas WHERE fecha > :last_run, ejecuta via FacuracionConnector.
PASO 3 · TR DataCleaner procesa el DataFrame: datetime parsing, SKU normalization, type
ANSFORM casting, drop duplicates.
PASO 4 · DataValidator ejecuta todas las reglas de calidad. Si alguna falla, lanza
VALIDATE ETLValidationError -> el pipeline se detiene y registra el error.
PASO 5 · DataLoader ejecuta el UPSERT transaccional en ventas_historicas. Si la
LOAD transacción falla, rollback total.
PASO 6 · CH CheckpointManager actualiza etl_checkpoints con timestamp actual solo si todos
ECKPOINT los pasos anteriores fueron exitosos.
PASO 7 · ETLOrchestrator registra en etl_logs: {etl_run_id, status, records_extracted,
LOG records_loaded, duration_ms, errors}.
2.4 Tecnologías y Dependencias
(cid:127) Python 3.11+: Lenguaje base. Uso de async/await para operaciones I/O bound.
(cid:127) SQLAlchemy 2.0+: ORM y connection pooling para ambas bases de datos (fuente y destino). Soporte para
múltiples dialectos sin cambiar código.
(cid:127) Pandas 2.1+: Transformaciones vectorizadas en el pipeline de limpieza. Uso de
dtype_backend='numpy_nullable' para manejo correcto de nulos.
(cid:127) APScheduler 3.x: Scheduler embebido para ejecución periódica del ETL (cron: lunes 05:00 AM). Integrado
con FastAPI.
(cid:127) Pydantic 2.x: Validación de schemas de datos de entrada con modelos tipados.
(cid:127) structlog: Logging estructurado en JSON. Cada log incluye: timestamp, correlation_id, module, level,
message, context.
(cid:127) pytest + pytest-cov: Suite de pruebas unitarias con mocking de la conexión a facturación usando
pytest-mock.
Configuración de ejemplo (etl/config.yml):
source_db_url: ${DATABASE_SOURCE_URL} # Inyectado por variable de entorno
target_db_url: ${DATABASE_TARGET_URL}
incremental_field: fecha_venta
min_weeks_per_sku: 12
max_quantity_threshold: 10000
schedule_cron: '0 5 * * 1' # Lunes 5AM
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 8

### Tablas detectadas en esta sección:
| ETLOrchestrator | etl/orchestrator.py | Coordina el pipeline completo: Extract -> Clean -> Validate -> Load -> Checkpoint. Maneja excepciones y rollback. |
| --- | --- | --- |


| PASO 1 · TRIGGER | El ETLOrchestrator es invocado por el scheduler (APScheduler) o manualmente vía endpoint POST /api/v1/etl/run. |
| --- | --- |
| PASO 2 · EXTRACT | IncrementalExtractor consulta etl_checkpoints, construye query SQL: SELECT * FROM ventas WHERE fecha > :last_run, ejecuta via FacuracionConnector. |
| PASO 3 · TR ANSFORM | DataCleaner procesa el DataFrame: datetime parsing, SKU normalization, type casting, drop duplicates. |
| PASO 4 · VALIDATE | DataValidator ejecuta todas las reglas de calidad. Si alguna falla, lanza ETLValidationError -> el pipeline se detiene y registra el error. |
| PASO 5 · LOAD | DataLoader ejecuta el UPSERT transaccional en ventas_historicas. Si la transacción falla, rollback total. |
| PASO 6 · CH ECKPOINT | CheckpointManager actualiza etl_checkpoints con timestamp actual solo si todos los pasos anteriores fueron exitosos. |
| PASO 7 · LOG | ETLOrchestrator registra en etl_logs: {etl_run_id, status, records_extracted, records_loaded, duration_ms, errors}. |



<!-- Página 9 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
SECCIÓN 3
MÓDULO DATA STORE — ALMACENAMIENTO
El Data Store es la capa de persistencia centralizada del sistema. Almacena todos los datos que fluyen entre
módulos: ventas históricas, predicciones, alertas, versiones de modelos, trazas de auditoría y configuración
operativa. Nota: El esquema de base de datos será provisto por el cliente; este módulo define los
contratos de datos (entidades y atributos) que el sistema requiere.
3.1 Estrategia de Persistencia
Se utiliza PostgreSQL 16 como motor principal por su robustez en operaciones transaccionales y soporte nativo
para tipos JSON, arrays y window functions necesarias para consultas de series temporales. Durante el piloto
se puede usar SQLite para entornos de desarrollo local, abstraído mediante el adaptador SQLAlchemy que es
transparente al resto del sistema.
Transacciones Todas las escrituras (ventas, predicciones, alertas) se realizan dentro de
ACID transacciones con rollback automático en caso de error.
Upsert Las cargas ETL usan INSERT ON CONFLICT DO UPDATE para garantizar
Idempotente que re-ejecuciones del ETL no generen duplicados.
Trazas La tabla predicciones_trazas usa permisos de solo-inserción para todos los
Inmutables roles de aplicación. No existe endpoint de DELETE para esta tabla.
Índices de Índices compuestos en (id_producto, id_sucursal, fecha) para las consultas
Rendimiento de series temporales más frecuentes.
Particionamient La tabla ventas_historicas está diseñada para particionamiento por año/mes
o Futuro cuando el volumen lo requiera (RNF-05).
3.2 Entidades y Contratos de Datos
Las siguientes entidades son los contratos que el sistema requiere. El DBA del cliente mapea estas entidades
al esquema físico provisto. Cada entidad incluye sus atributos, tipos y restricciones de integridad.
Tabla: productos (SKU)
Catálogo de productos piloto. Solo los SKUs con activo=TRUE son procesados por el ML Engine.
Campo Tipo / Restricción
id_producto SERIAL PRIMARY KEY
nombre VARCHAR(200) NOT NULL
categoria VARCHAR(100)
unidad_medida VARCHAR(20)
stock_actual INTEGER DEFAULT 0
stock_minimo INTEGER DEFAULT 0
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 9

### Tablas detectadas en esta sección:
| Transacciones ACID | Todas las escrituras (ventas, predicciones, alertas) se realizan dentro de transacciones con rollback automático en caso de error. |
| --- | --- |
| Upsert Idempotente | Las cargas ETL usan INSERT ON CONFLICT DO UPDATE para garantizar que re-ejecuciones del ETL no generen duplicados. |
| Trazas Inmutables | La tabla predicciones_trazas usa permisos de solo-inserción para todos los roles de aplicación. No existe endpoint de DELETE para esta tabla. |
| Índices de Rendimiento | Índices compuestos en (id_producto, id_sucursal, fecha) para las consultas de series temporales más frecuentes. |
| Particionamient o Futuro | La tabla ventas_historicas está diseñada para particionamiento por año/mes cuando el volumen lo requiera (RNF-05). |


| Campo | Tipo / Restricción |
| --- | --- |
| id_producto | SERIAL PRIMARY KEY |
| nombre | VARCHAR(200) NOT NULL |
| categoria | VARCHAR(100) |
| unidad_medida | VARCHAR(20) |
| stock_actual | INTEGER DEFAULT 0 |
| stock_minimo | INTEGER DEFAULT 0 |



<!-- Página 10 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
activo BOOLEAN DEFAULT TRUE
created_at TIMESTAMPTZ DEFAULT NOW()
Tabla: sucursales
Registro de tiendas de la cadena. El piloto puede operar con una o múltiples sucursales.
Campo Tipo / Restricción
id_sucursal SERIAL PRIMARY KEY
nombre VARCHAR(150) NOT NULL
direccion TEXT
activa BOOLEAN DEFAULT TRUE
Tabla: ventas_historicas
Historial de ventas extraído por el ETL. Índice compuesto en (id_producto, id_sucursal, fecha_venta).
Campo Tipo / Restricción
id_venta BIGSERIAL PRIMARY KEY
fecha_venta DATE NOT NULL
semana_iso INTEGER NOT NULL
anio INTEGER NOT NULL
id_producto INTEGER FK -> productos
id_sucursal INTEGER FK -> sucursales
cantidad INTEGER NOT NULL CHECK(cantidad >= 0)
precio_unitario NUMERIC(10,2)
created_at TIMESTAMPTZ DEFAULT NOW()
Tabla: modelos_predictivos
Registro de cada versión de modelo entrenado con sus métricas. El campo estado puede ser: activo, deprecado,
en_evaluacion.
Campo Tipo / Restricción
id_modelo SERIAL PRIMARY KEY
tipo VARCHAR(50) NOT NULL
version VARCHAR(20) NOT NULL
mlflow_run_id VARCHAR(100)
fecha_entrenamiento TIMESTAMPTZ
parametros JSONB
estado VARCHAR(20) DEFAULT 'activo'
mape NUMERIC(8,4)
mae NUMERIC(8,4)
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 10

### Tablas detectadas en esta sección:
| activo | BOOLEAN DEFAULT TRUE |
| --- | --- |
| created_at | TIMESTAMPTZ DEFAULT NOW() |


| Campo | Tipo / Restricción |
| --- | --- |
| id_sucursal | SERIAL PRIMARY KEY |
| nombre | VARCHAR(150) NOT NULL |
| direccion | TEXT |
| activa | BOOLEAN DEFAULT TRUE |


| Campo | Tipo / Restricción |
| --- | --- |
| id_venta | BIGSERIAL PRIMARY KEY |
| fecha_venta | DATE NOT NULL |
| semana_iso | INTEGER NOT NULL |
| anio | INTEGER NOT NULL |
| id_producto | INTEGER FK -> productos |
| id_sucursal | INTEGER FK -> sucursales |
| cantidad | INTEGER NOT NULL CHECK(cantidad >= 0) |
| precio_unitario | NUMERIC(10,2) |
| created_at | TIMESTAMPTZ DEFAULT NOW() |


| Campo | Tipo / Restricción |
| --- | --- |
| id_modelo | SERIAL PRIMARY KEY |
| tipo | VARCHAR(50) NOT NULL |
| version | VARCHAR(20) NOT NULL |
| mlflow_run_id | VARCHAR(100) |
| fecha_entrenamiento | TIMESTAMPTZ |
| parametros | JSONB |
| estado | VARCHAR(20) DEFAULT 'activo' |
| mape | NUMERIC(8,4) |
| mae | NUMERIC(8,4) |



<!-- Página 11 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
bias NUMERIC(8,4)
Tabla: predicciones
Predicciones generadas con intervalos de confianza. El campo confianza_alta=FALSE cuando MAPE > 25%.
Campo Tipo / Restricción
id_prediccion BIGSERIAL PRIMARY KEY
id_modelo INTEGER FK
id_producto INTEGER FK
id_sucursal INTEGER FK
semana_predicha INTEGER
anio_predicho INTEGER
cantidad_estimada INTEGER
limite_inferior INTEGER
limite_superior INTEGER
confianza_alta BOOLEAN DEFAULT TRUE
ajuste_manual BOOLEAN DEFAULT FALSE
cantidad_ajustada INTEGER
justificacion_ajuste TEXT
timestamp_generacion TIMESTAMPTZ DEFAULT NOW()
Tabla: alertas
Alertas de quiebre de stock proyectado. Solo el Administrador asignado puede marcar una alerta como atendida.
Campo Tipo / Restricción
id_alerta SERIAL PRIMARY KEY
id_prediccion BIGINT FK
id_producto INTEGER FK
id_sucursal INTEGER FK
tipo VARCHAR(50) NOT NULL
mensaje TEXT NOT NULL
fecha_generacion TIMESTAMPTZ DEFAULT NOW()
atendida BOOLEAN DEFAULT FALSE
atendida_por INTEGER FK -> usuarios
atendida_en TIMESTAMPTZ
Tabla: ventas_reales
Ventas reales registradas por el Administrador para calcular error del modelo y disparar reentrenamiento.
Campo Tipo / Restricción
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 11

### Tablas detectadas en esta sección:
| bias | NUMERIC(8,4) |
| --- | --- |


| Campo | Tipo / Restricción |
| --- | --- |
| id_prediccion | BIGSERIAL PRIMARY KEY |
| id_modelo | INTEGER FK |
| id_producto | INTEGER FK |
| id_sucursal | INTEGER FK |
| semana_predicha | INTEGER |
| anio_predicho | INTEGER |
| cantidad_estimada | INTEGER |
| limite_inferior | INTEGER |
| limite_superior | INTEGER |
| confianza_alta | BOOLEAN DEFAULT TRUE |
| ajuste_manual | BOOLEAN DEFAULT FALSE |
| cantidad_ajustada | INTEGER |
| justificacion_ajuste | TEXT |
| timestamp_generacion | TIMESTAMPTZ DEFAULT NOW() |


| Campo | Tipo / Restricción |
| --- | --- |
| id_alerta | SERIAL PRIMARY KEY |
| id_prediccion | BIGINT FK |
| id_producto | INTEGER FK |
| id_sucursal | INTEGER FK |
| tipo | VARCHAR(50) NOT NULL |
| mensaje | TEXT NOT NULL |
| fecha_generacion | TIMESTAMPTZ DEFAULT NOW() |
| atendida | BOOLEAN DEFAULT FALSE |
| atendida_por | INTEGER FK -> usuarios |
| atendida_en | TIMESTAMPTZ |


| Campo | Tipo / Restricción |
| --- | --- |



<!-- Página 12 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
id_venta_real BIGSERIAL PRIMARY KEY
id_prediccion BIGINT FK
id_producto INTEGER FK
id_sucursal INTEGER FK
semana_iso INTEGER
anio INTEGER
cantidad_real INTEGER NOT NULL
registrado_por INTEGER FK -> usuarios
timestamp_registro TIMESTAMPTZ DEFAULT NOW()
Tabla: etl_logs
Registro de cada ejecución ETL para auditoría y debugging operativo.
Campo Tipo / Restricción
id_log BIGSERIAL PRIMARY KEY
etl_run_id UUID NOT NULL
status VARCHAR(20)
records_extracted INTEGER
records_loaded INTEGER
duration_ms INTEGER
error_message TEXT
executed_at TIMESTAMPTZ DEFAULT NOW()
Tabla: predicciones_trazas (inmutable)
Traza inmutable. Permisos: INSERT only para todos los roles de aplicación. Cumple RNF-09.
Campo Tipo / Restricción
id_traza BIGSERIAL PRIMARY KEY
id_prediccion BIGINT FK
version_modelo VARCHAR(20)
parametros_entrada JSONB
resultado JSONB
timestamp TIMESTAMPTZ DEFAULT NOW()
Tabla: usuarios
Usuarios del sistema con roles: administrador_tienda, gerencia, area_financiera, admin_sistema.
Campo Tipo / Restricción
id_usuario SERIAL PRIMARY KEY
email VARCHAR(200) UNIQUE NOT NULL
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 12

### Tablas detectadas en esta sección:
| id_venta_real | BIGSERIAL PRIMARY KEY |
| --- | --- |
| id_prediccion | BIGINT FK |
| id_producto | INTEGER FK |
| id_sucursal | INTEGER FK |
| semana_iso | INTEGER |
| anio | INTEGER |
| cantidad_real | INTEGER NOT NULL |
| registrado_por | INTEGER FK -> usuarios |
| timestamp_registro | TIMESTAMPTZ DEFAULT NOW() |


| Campo | Tipo / Restricción |
| --- | --- |
| id_log | BIGSERIAL PRIMARY KEY |
| etl_run_id | UUID NOT NULL |
| status | VARCHAR(20) |
| records_extracted | INTEGER |
| records_loaded | INTEGER |
| duration_ms | INTEGER |
| error_message | TEXT |
| executed_at | TIMESTAMPTZ DEFAULT NOW() |


| Campo | Tipo / Restricción |
| --- | --- |
| id_traza | BIGSERIAL PRIMARY KEY |
| id_prediccion | BIGINT FK |
| version_modelo | VARCHAR(20) |
| parametros_entrada | JSONB |
| resultado | JSONB |
| timestamp | TIMESTAMPTZ DEFAULT NOW() |


| Campo | Tipo / Restricción |
| --- | --- |
| id_usuario | SERIAL PRIMARY KEY |
| email | VARCHAR(200) UNIQUE NOT NULL |



<!-- Página 13 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
password_hash VARCHAR(255) NOT NULL
rol VARCHAR(30) NOT NULL
id_sucursal INTEGER FK
activo BOOLEAN DEFAULT TRUE
created_at TIMESTAMPTZ DEFAULT NOW()
3.3 Tecnologías
(cid:127) PostgreSQL 16: Motor relacional principal. Soporte JSONB para parámetros de modelo, window functions
para cálculos de series temporales (LAG, LEAD, SUM OVER).
(cid:127) SQLAlchemy 2.0+: ORM con declarative base. Todos los modelos ORM en models/. El repositorio pattern
abstrae todas las queries SQL del código de negocio.
(cid:127) Alembic: Migraciones de esquema versionadas. Toda modificación al schema pasa por una migración con
upgrade/downgrade definidos.
(cid:127) SQLite: Alternativa para entorno de desarrollo local. El switch se hace cambiando
DATABASE_TARGET_URL en .env, sin cambios de código.
(cid:127) psycopg2-binary: Driver PostgreSQL de alto rendimiento con connection pooling vía SQLAlchemy
QueuePool.
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 13

### Tablas detectadas en esta sección:
| password_hash | VARCHAR(255) NOT NULL |
| --- | --- |
| rol | VARCHAR(30) NOT NULL |
| id_sucursal | INTEGER FK |
| activo | BOOLEAN DEFAULT TRUE |
| created_at | TIMESTAMPTZ DEFAULT NOW() |



<!-- Página 14 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
SECCIÓN 4
MÓDULO ML ENGINE — MOTOR DE INTELIGENCIA ARTIFICIAL
El ML Engine es el núcleo analítico del sistema. Es el componente de mayor valor técnico y está implementado
completamente en Python. Su diseño sigue un pipeline reproducible y versionado que garantiza que cada
predicción sea trazable, auditable y comparable con versiones anteriores del modelo.
4.1 Pipeline de Machine Learning
El ML Engine implementa un pipeline estructurado en cuatro fases: preparación de datos, entrenamiento,
evaluación y predicción. Cada fase es un componente independiente con interfaz definida.
FASE 1 Carga ventas_historicas del Data Store para los SKUs activos. Construye series
DATA PREP temporales semanales (agrupando por semana ISO). Aplica: imputación de semanas
ARATION faltantes con forward-fill, detección y tratamiento de outliers (IQR), creación de
features (lag_1, lag_2, lag_4, rolling_mean_4w, rolling_std_4w, semana_del_año,
es_fin_de_mes). Produce un DataFrame con index=semana_iso y
columnas=features+target.
FASE 2 Walk-Forward Validation: divide los datos en N splits temporales. Para cada split:
TRAINING entrena en las primeras K semanas, evalúa en las siguientes M semanas. Selecciona
el modelo con menor MAPE promedio. Modelos candidatos: SARIMA (baseline
estadístico), XGBoost con features temporales (modelo principal), Ensemble
ponderado por MAPE inverso (modelo avanzado). El modelo ganador se serializa
con joblib y se registra en MLflow.
FASE 3 Calcula métricas sobre el conjunto de validación hold-out: MAPE (error porcentual
EVALUATIO relativo, comparable entre SKUs), MAE (error absoluto en unidades), Bias (sesgo
N sistemático: promedio de errores con signo). Si MAPE > 25%: flag
confianza_alta=False. Si MAPE nuevo_modelo > MAPE_anterior + 5%: alerta de
degradación. Todas las métricas se registran en modelos_predictivos y en MLflow.
FASE 4 Carga el modelo activo desde MLflow (o repositorio local). Genera predicciones para
PREDICTION semanas T+1 a T+4. Calcula intervalos de confianza al 90% usando bootstrap
residuals. Persiste resultados en tabla predicciones con todos los campos
requeridos. Registra traza inmutable en predicciones_trazas. Notifica al Alert Engine
para evaluación de quiebres de stock.
4.2 Algoritmos y Selección de Modelo
Algoritmo Tipo Ventajas Limitaciones Uso
SARIMA Estadístico Captura estacionalidad y Asume linealidad. Requiere Baseline y SKUs
tendencia. No requiere estacionariedad. con pocos datos
features adicionales.
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 14

### Tablas detectadas en esta sección:
| FASE 1 DATA PREP ARATION | Carga ventas_historicas del Data Store para los SKUs activos. Construye series temporales semanales (agrupando por semana ISO). Aplica: imputación de semanas faltantes con forward-fill, detección y tratamiento de outliers (IQR), creación de features (lag_1, lag_2, lag_4, rolling_mean_4w, rolling_std_4w, semana_del_año, es_fin_de_mes). Produce un DataFrame con index=semana_iso y columnas=features+target. |
| --- | --- |


| FASE 2 TRAINING | Walk-Forward Validation: divide los datos en N splits temporales. Para cada split: entrena en las primeras K semanas, evalúa en las siguientes M semanas. Selecciona el modelo con menor MAPE promedio. Modelos candidatos: SARIMA (baseline estadístico), XGBoost con features temporales (modelo principal), Ensemble ponderado por MAPE inverso (modelo avanzado). El modelo ganador se serializa con joblib y se registra en MLflow. |
| --- | --- |


| FASE 3 EVALUATIO N | Calcula métricas sobre el conjunto de validación hold-out: MAPE (error porcentual relativo, comparable entre SKUs), MAE (error absoluto en unidades), Bias (sesgo sistemático: promedio de errores con signo). Si MAPE > 25%: flag confianza_alta=False. Si MAPE nuevo_modelo > MAPE_anterior + 5%: alerta de degradación. Todas las métricas se registran en modelos_predictivos y en MLflow. |
| --- | --- |


| FASE 4 PREDICTION | Carga el modelo activo desde MLflow (o repositorio local). Genera predicciones para semanas T+1 a T+4. Calcula intervalos de confianza al 90% usando bootstrap residuals. Persiste resultados en tabla predicciones con todos los campos requeridos. Registra traza inmutable en predicciones_trazas. Notifica al Alert Engine para evaluación de quiebres de stock. |
| --- | --- |


| Algoritmo | Tipo | Ventajas | Limitaciones | Uso |
| --- | --- | --- | --- | --- |
| SARIMA | Estadístico | Captura estacionalidad y tendencia. No requiere features adicionales. | Asume linealidad. Requiere estacionariedad. | Baseline y SKUs con pocos datos |



<!-- Página 15 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
XGBoost ML Captura relaciones no Requiere más datos. Modelo principal
Supervisado lineales. Maneja features Propenso a overfitting con con >= 24
heterogéneos. pocos SKU. semanas
Prophet Bayesiano Maneja estacionalidad Mayor costo SKUs con patrones
múltiple y días festivos. computacional. Menos estacionales
interpretable. fuertes
Ensemble Meta-modelo Reduce varianza Mayor complejidad de Producción
combinando modelos. Más mantenimiento. avanzada
robusto. (post-piloto)
Criterio de selección automática: El sistema ejecuta los modelos candidatos en paralelo
(concurrent.futures.ProcessPoolExecutor) y selecciona el de menor MAPE promedio en el walk-forward
validation. El proceso es completamente automatizado y reproducible dado el mismo dataset y random seed.
4.3 Versionamiento con MLflow
Tracking MLflow tracking server corriendo como servicio Docker en el puerto 5000. Persiste
URI artefactos en volumen Docker /mlflow-data.
Experimen Un experimento por SKU: Experiment name = 'demand_sku_{id_producto}'. Cada
tos ejecución de entrenamiento = un Run.
Parámetro
s model_type, hyperparams (dict), n_train_weeks, n_val_weeks, feature_list,
Logueados random_seed.
Métricas
Logueadas mape_val, mae_val, bias_val, mape_train, training_duration_sec.
Modelo serializado (model.pkl via joblib), feature_importance.png,
Artefactos walk_forward_results.csv, config.yaml usado.
Model Modelos promovidos a Staging -> Production usando MLflow Model Registry. Solo
Registry el modelo en estado Production es usado por el ML Engine.
Para volver a una versión anterior: mlflow models transition-stage --version N
Rollback --stage Production. Sin reinicio del servicio.
4.4 Tecnologías Python del ML Engine
(cid:127) Python 3.11+: Lenguaje exclusivo del ML Engine. Uso de type hints en todas las funciones para
mantenibilidad.
(cid:127) scikit-learn 1.4+: Pipeline API para encadenar preprocesamiento y modelo. TimeSeriesSplit para
walk-forward validation. Métricas: mean_absolute_percentage_error, mean_absolute_error.
(cid:127) statsmodels 0.14+: Implementación de SARIMA (SARIMAX). Análisis de estacionariedad (ADF test).
Descomposición de series temporales.
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 15

### Tablas detectadas en esta sección:
| XGBoost | ML Supervisado | Captura relaciones no lineales. Maneja features heterogéneos. | Requiere más datos. Propenso a overfitting con pocos SKU. | Modelo principal con >= 24 semanas |
| --- | --- | --- | --- | --- |
| Prophet | Bayesiano | Maneja estacionalidad múltiple y días festivos. | Mayor costo computacional. Menos interpretable. | SKUs con patrones estacionales fuertes |
| Ensemble | Meta-modelo | Reduce varianza combinando modelos. Más robusto. | Mayor complejidad de mantenimiento. | Producción avanzada (post-piloto) |


| Tracking URI | MLflow tracking server corriendo como servicio Docker en el puerto 5000. Persiste artefactos en volumen Docker /mlflow-data. |
| --- | --- |
| Experimen tos | Un experimento por SKU: Experiment name = 'demand_sku_{id_producto}'. Cada ejecución de entrenamiento = un Run. |
| Parámetro s Logueados | model_type, hyperparams (dict), n_train_weeks, n_val_weeks, feature_list, random_seed. |
| Métricas Logueadas | mape_val, mae_val, bias_val, mape_train, training_duration_sec. |
| Artefactos | Modelo serializado (model.pkl via joblib), feature_importance.png, walk_forward_results.csv, config.yaml usado. |
| Model Registry | Modelos promovidos a Staging -> Production usando MLflow Model Registry. Solo el modelo en estado Production es usado por el ML Engine. |
| Rollback | Para volver a una versión anterior: mlflow models transition-stage --version N --stage Production. Sin reinicio del servicio. |



<!-- Página 16 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
(cid:127) XGBoost 2.x: Modelo gradient boosting para features tabulares temporales. Early stopping con eval_set de
validación.
(cid:127) Prophet (Facebook/Meta): Modelo bayesiano para series con estacionalidad múltiple y eventos especiales
(festivos Colombia).
(cid:127) MLflow 2.x: Tracking, Model Registry y serving. Interfaz web en puerto 5000 para visualizar experimentos.
(cid:127) joblib: Serialización de modelos scikit-learn. Paralelización del walk-forward validation con n_jobs=-1.
(cid:127) numpy 1.26+ / pandas 2.1+: Manipulación de arrays y DataFrames. Pandas para construcción de features
temporales.
(cid:127) matplotlib / seaborn: Generación de artefactos visuales de evaluación (feature importance, residual plots)
logueados en MLflow.
(cid:127) pytest + pytest-cov: Suite de pruebas del ML Engine con fixtures de datasets sintéticos. Cobertura >= 70%.
Estructura de directorios del ML Engine:
ml_engine/
nnn data/ # DataPreparer, FeatureEngineer
nnn models/ # SarimaModel, XGBoostModel, ProphetModel, Ensemble
nnn training/ # Trainer, WalkForwardValidator
nnn evaluation/ # MetricsCalculator, ConfidenceEvaluator
nnn prediction/ # Predictor, IntervalCalculator
nnn registry/ # MLflowRegistry, ModelVersionManager
nnn config/ # ml_config.yaml, hyperparams.yaml
nnn tests/ # test_data.py, test_models.py, test_prediction.py
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 16


<!-- Página 17 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
SECCIÓN 5
MÓDULO ALERT ENGINE — MOTOR DE ALERTAS
El Alert Engine es un microservicio Python independiente que se activa cada vez que el ML Engine genera
nuevas predicciones. Compara la demanda proyectada con el stock actual registrado en el Data Store y genera
alertas persistentes cuando detecta riesgo de quiebre de stock o sobrestock crítico.
5.1 Lógica de Detección
El ML Engine publica un evento interno (llamada directa o mensaje en cola) al Alert
1. Trigger Engine con los IDs de las predicciones recién generadas.
2. Carga El Alert Engine consulta: predicciones (cantidad_estimada, limite_superior,
de Datos id_producto, id_sucursal) y productos (stock_actual, stock_minimo).
3. Evalua Para cada SKU/sucursal: si cantidad_estimada > stock_actual => QUIEBRE
ción de PROYECTADO. Si limite_superior > stock_actual (usando peor caso) => RIESGO
Quiebre ALTO.
4. Evalua
ción de S
obrestoc Si stock_actual > (cantidad_estimada * 3) para productos perecederos =>
k SOBRESTOCK CRITICO (pérdida por vencimiento).
5. Genera
ción de Crea registro en tabla alertas con mensaje formateado, tipo, y referencias a
Alerta prediccion, producto, sucursal.
6. Notific
ación Publica la alerta vía WebSocket al dashboard del Administrador correspondiente
Real-time (filtrado por id_sucursal del usuario).
7. Dedupl No genera alertas duplicadas: verifica si ya existe una alerta activa (atendida=False)
icación del mismo tipo para el mismo SKU/sucursal/semana.
5.2 Tipos de Alerta y Mensajes
Tipo Condición Mensaje Generado Prioridad
QUIEBRE_PROYECT cantidad_estimada > 'Posible quiebre de stock: [SKU] — ALTA
ADO stock_actual Demanda proyectada: X uds, Stock
actual: Y uds.'
RIESGO_QUIEBRE limite_superior > 'Riesgo de quiebre (peor caso): MEDIA
stock_actual [SKU] — Limite superior demanda: X
uds, Stock: Y uds.'
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 17

### Tablas detectadas en esta sección:
| 1. Trigger | El ML Engine publica un evento interno (llamada directa o mensaje en cola) al Alert Engine con los IDs de las predicciones recién generadas. |
| --- | --- |
| 2. Carga de Datos | El Alert Engine consulta: predicciones (cantidad_estimada, limite_superior, id_producto, id_sucursal) y productos (stock_actual, stock_minimo). |
| 3. Evalua ción de Quiebre | Para cada SKU/sucursal: si cantidad_estimada > stock_actual => QUIEBRE PROYECTADO. Si limite_superior > stock_actual (usando peor caso) => RIESGO ALTO. |
| 4. Evalua ción de S obrestoc k | Si stock_actual > (cantidad_estimada * 3) para productos perecederos => SOBRESTOCK CRITICO (pérdida por vencimiento). |
| 5. Genera ción de Alerta | Crea registro en tabla alertas con mensaje formateado, tipo, y referencias a prediccion, producto, sucursal. |
| 6. Notific ación Real-time | Publica la alerta vía WebSocket al dashboard del Administrador correspondiente (filtrado por id_sucursal del usuario). |
| 7. Dedupl icación | No genera alertas duplicadas: verifica si ya existe una alerta activa (atendida=False) del mismo tipo para el mismo SKU/sucursal/semana. |


| Tipo | Condición | Mensaje Generado | Prioridad |
| --- | --- | --- | --- |
| QUIEBRE_PROYECT ADO | cantidad_estimada > stock_actual | 'Posible quiebre de stock: [SKU] — Demanda proyectada: X uds, Stock actual: Y uds.' | ALTA |
| RIESGO_QUIEBRE | limite_superior > stock_actual | 'Riesgo de quiebre (peor caso): [SKU] — Limite superior demanda: X uds, Stock: Y uds.' | MEDIA |



<!-- Página 18 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
SOBRESTOCK_CRIT stock > 'Sobrestock crítico: [SKU] — Stock: MEDIA
ICO demanda_estimada * 3 X uds, Demanda estimada: Y uds.
Riesgo vencimiento.'
BAJA_CONFIANZA MAPE > 25% 'PREDICCIÓN DE BAJA CONFIANZA para INFO
[SKU]. MAPE actual: X%. Usar con
precaución.'
5.3 Tecnologías
(cid:127) Python 3.11+: Microservicio independiente. Puede ejecutarse como worker separado o importado como
módulo por la REST API.
(cid:127) SQLAlchemy 2.0+: Acceso al Data Store para leer predicciones, stock y escribir alertas. Transacciones con
rollback.
(cid:127) WebSockets (FastAPI/Starlette): Canal de notificación en tiempo real hacia el dashboard. Conexiones
filtradas por rol y sucursal del usuario autenticado.
(cid:127) APScheduler: Evaluación periódica de alertas (cada hora en horario operativo) independiente del ciclo de
predicción.
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 18

### Tablas detectadas en esta sección:
| SOBRESTOCK_CRIT ICO | stock > demanda_estimada * 3 | 'Sobrestock crítico: [SKU] — Stock: X uds, Demanda estimada: Y uds. Riesgo vencimiento.' | MEDIA |
| --- | --- | --- | --- |
| BAJA_CONFIANZA | MAPE > 25% | 'PREDICCIÓN DE BAJA CONFIANZA para [SKU]. MAPE actual: X%. Usar con precaución.' | INFO |



<!-- Página 19 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
SECCIÓN 6
MÓDULO REST API — CAPA DE SERVICIOS
La REST API es la interfaz entre el frontend, los clientes externos y los módulos internos del sistema.
Implementada con FastAPI, expone endpoints RESTful documentados automáticamente con
OpenAPI/Swagger. Es el único punto de entrada externo al sistema (excepto WebSockets).
6.1 Endpoints Principales
Autenticación (/api/v1/auth)
Métod Rol
Ruta Descripción
o Requerido
Autentica usuario con email/password. Retorna
POST /login Público
access_token (JWT, 8h) y refresh_token (24h).
Autenticad
POST /refresh Renueva el access_token usando un refresh_token válido.
o
Autenticad
POST /logout Invalida el refresh_token del usuario.
o
ETL (/api/v1/etl)
Métod Rol
Ruta Descripción
o Requerido
Admin
POST /run Dispara manualmente una ejecución ETL incremental.
Sistema
Retorna el estado de la última ejecución ETL (status, Admin
GET /status
records, timestamp). Sistema
Lista los últimos N registros de etl_logs con filtros Admin
GET /logs
opcionales. Sistema
Predicciones (/api/v1/predictions)
Métod Rol
Ruta Descripción
o Requerido
Admin
POST /generate Dispara el ciclo de predicción para todos los SKUs activos.
Sistema
/{sku_id}/{sucursal_ Retorna predicciones T+1 a T+4 para un SKU/sucursal con
GET Todos
id} intervalos de confianza.
Gerencia,
GET /summary Resumen de predicciones por sucursal (vista gerencia).
Financiero
/{prediction_id}/adj Aplica ajuste manual con justificación. Solo modifica Administra
PATCH
ust cantidad_ajustada, no el modelo. dor
Alertas (/api/v1/alerts)
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 19

### Tablas detectadas en esta sección:
| Métod o | Ruta | Descripción | Rol Requerido |
| --- | --- | --- | --- |
| POST | /login | Autentica usuario con email/password. Retorna access_token (JWT, 8h) y refresh_token (24h). | Público |
| POST | /refresh | Renueva el access_token usando un refresh_token válido. | Autenticad o |
| POST | /logout | Invalida el refresh_token del usuario. | Autenticad o |


| Métod o | Ruta | Descripción | Rol Requerido |
| --- | --- | --- | --- |
| POST | /run | Dispara manualmente una ejecución ETL incremental. | Admin Sistema |
| GET | /status | Retorna el estado de la última ejecución ETL (status, records, timestamp). | Admin Sistema |
| GET | /logs | Lista los últimos N registros de etl_logs con filtros opcionales. | Admin Sistema |


| Métod o | Ruta | Descripción | Rol Requerido |
| --- | --- | --- | --- |
| POST | /generate | Dispara el ciclo de predicción para todos los SKUs activos. | Admin Sistema |
| GET | /{sku_id}/{sucursal_ id} | Retorna predicciones T+1 a T+4 para un SKU/sucursal con intervalos de confianza. | Todos |
| GET | /summary | Resumen de predicciones por sucursal (vista gerencia). | Gerencia, Financiero |
| PATCH | /{prediction_id}/adj ust | Aplica ajuste manual con justificación. Solo modifica cantidad_ajustada, no el modelo. | Administra dor |



<!-- Página 20 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
Métod Rol
Ruta Descripción
o Requerido
Lista alertas activas (atendida=False) para la sucursal del Administra
GET /active
usuario autenticado. dor
Lista todas las alertas con filtros (tipo, fecha, sucursal, Gerencia,
GET /
atendida). Financiero
Marca una alerta como atendida. Registra usuario y Administra
PATCH /{alert_id}/attend
timestamp. dor
Métricas (/api/v1/metrics)
Métod Rol
Ruta Descripción
o Requerido
Retorna MAPE, MAE, Bias del modelo activo y el anterior
GET /model Todos
para comparación.
Gerencia,
GET /model/history Historial de métricas de todos los modelos versionados.
Financiero
Estimación de ahorro por reducción de quiebres y
GET /savings Financiero
sobrestock.
Ventas Reales (/api/v1/sales)
Métod Rol
Ruta Descripción
o Requerido
Registra la venta real de la semana cerrada para un Administra
POST /actual
SKU/sucursal. dor
/{sku_id}/{sucursal_
GET Historial de ventas reales registradas manualmente. Todos
id}
WebSocket (/ws)
Métod Rol
Ruta Descripción
o Requerido
Canal en tiempo real para recibir alertas nuevas. El token Administra
WS /alerts/{token}
JWT identifica el usuario y filtra por sucursal. dor
6.2 Autenticación y Seguridad
Todo el tráfico entre cliente y servidor va cifrado. En producción, Nginx actúa
HTTPS/TLS como reverse proxy con certificado SSL. En desarrollo, Uvicorn con certificado
1.2+ auto-firmado.
Tokens firmados con clave privada RSA 2048 bits. El payload incluye: sub
(user_id), role, sucursal_id, exp (expiración). Verificación con clave pública en
JWT RS256 cada request.
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 20

### Tablas detectadas en esta sección:
| Métod o | Ruta | Descripción | Rol Requerido |
| --- | --- | --- | --- |
| GET | /active | Lista alertas activas (atendida=False) para la sucursal del usuario autenticado. | Administra dor |
| GET | / | Lista todas las alertas con filtros (tipo, fecha, sucursal, atendida). | Gerencia, Financiero |
| PATCH | /{alert_id}/attend | Marca una alerta como atendida. Registra usuario y timestamp. | Administra dor |


| Métod o | Ruta | Descripción | Rol Requerido |
| --- | --- | --- | --- |
| GET | /model | Retorna MAPE, MAE, Bias del modelo activo y el anterior para comparación. | Todos |
| GET | /model/history | Historial de métricas de todos los modelos versionados. | Gerencia, Financiero |
| GET | /savings | Estimación de ahorro por reducción de quiebres y sobrestock. | Financiero |


| Métod o | Ruta | Descripción | Rol Requerido |
| --- | --- | --- | --- |
| POST | /actual | Registra la venta real de la semana cerrada para un SKU/sucursal. | Administra dor |
| GET | /{sku_id}/{sucursal_ id} | Historial de ventas reales registradas manualmente. | Todos |


| Métod o | Ruta | Descripción | Rol Requerido |
| --- | --- | --- | --- |
| WS | /alerts/{token} | Canal en tiempo real para recibir alertas nuevas. El token JWT identifica el usuario y filtra por sucursal. | Administra dor |


| HTTPS/TLS 1.2+ | Todo el tráfico entre cliente y servidor va cifrado. En producción, Nginx actúa como reverse proxy con certificado SSL. En desarrollo, Uvicorn con certificado auto-firmado. |
| --- | --- |
| JWT RS256 | Tokens firmados con clave privada RSA 2048 bits. El payload incluye: sub (user_id), role, sucursal_id, exp (expiración). Verificación con clave pública en cada request. |



<!-- Página 21 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
Refresh
Token Cada uso del refresh_token genera uno nuevo e invalida el anterior.
Rotation Almacenados con hash bcrypt en base de datos. TTL: 24 horas.
RBAC
(Role-Based Dependency injection de FastAPI verifica el rol en cada endpoint. Roles:
Access admin_sistema (full), administrador_tienda (su sucursal), gerencia (lectura
Control) global), area_financiera (métricas).
Rate slowapi (basado en limits) para prevenir abuso: 100 req/min por IP para
Limiting endpoints públicos, 1000 req/min para autenticados.
Configurado explícitamente con lista blanca de origins permitidos. No se usa
CORS wildcard (*) en producción.
Validación Todos los schemas de request/response definidos con Pydantic 2.x. Validación
de Entrada automática con mensajes de error descriptivos.
6.3 Tecnologías FastAPI
(cid:127) FastAPI 0.110+: Framework asíncrono de alto rendimiento. Documentación automática OpenAPI en /docs
(Swagger UI) y /redoc. Soporte nativo para async/await y dependency injection.
(cid:127) Uvicorn: ASGI server. En producción: 4 workers con --workers 4. Detrás de Nginx como reverse proxy.
(cid:127) Pydantic 2.x: Validación de schemas con model_config = ConfigDict(from_attributes=True) para serializar
modelos ORM directamente.
(cid:127) python-JOSE: Librería para creación y verificación de JWT con RS256. Manejo de expiración y claims
personalizados.
(cid:127) slowapi: Rate limiting por IP y por usuario autenticado. Configuración via decoradores.
(cid:127) Starlette WebSockets: Integrado en FastAPI para el canal de alertas en tiempo real. ConnectionManager
mantiene el registro de conexiones activas por usuario.
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 21

### Tablas detectadas en esta sección:
| Refresh Token Rotation | Cada uso del refresh_token genera uno nuevo e invalida el anterior. Almacenados con hash bcrypt en base de datos. TTL: 24 horas. |
| --- | --- |
| RBAC (Role-Based Access Control) | Dependency injection de FastAPI verifica el rol en cada endpoint. Roles: admin_sistema (full), administrador_tienda (su sucursal), gerencia (lectura global), area_financiera (métricas). |
| Rate Limiting | slowapi (basado en limits) para prevenir abuso: 100 req/min por IP para endpoints públicos, 1000 req/min para autenticados. |
| CORS | Configurado explícitamente con lista blanca de origins permitidos. No se usa wildcard (*) en producción. |
| Validación de Entrada | Todos los schemas de request/response definidos con Pydantic 2.x. Validación automática con mensajes de error descriptivos. |



<!-- Página 22 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
SECCIÓN 7
MÓDULO AUTH SERVICE — AUTENTICACIÓN Y AUTORIZACIÓN
El Auth Service gestiona la identidad de todos los actores del sistema. Está implementado como un conjunto de
componentes Python integrados en la REST API (no como un servicio separado en el piloto, para mantener la
simplicidad). Se diseña con interfaces para poder extraerlo como microservicio independiente en el futuro.
7.1 Flujo de Autenticación JWT
1.
Login El usuario envía {email, password} al endpoint POST /api/v1/auth/login.
2. Veri
ficació AuthService consulta la tabla usuarios por email. Verifica la contraseña con
n passlib.verify(password, password_hash) usando bcrypt.
3. Gen
eració
n de T Si las credenciales son válidas: genera access_token (JWT RS256, exp: 8h) y
okens refresh_token (JWT RS256, exp: 24h con JTI único).
4. Alm
acena
mient
o Refr El refresh_token JTI se almacena hasheado en la tabla refresh_tokens con el user_id y
esh timestamp de expiración.
5. Req
uest A
utenti El cliente incluye el access_token en el header: Authorization: Bearer . FastAPI lo valida
cado via Dependency (get_current_user).
6. Ren
ovació Cuando el access_token expira, el cliente usa el refresh_token en POST /auth/refresh
n para obtener un nuevo par de tokens (rotation).
7. Log El JTI del refresh_token se agrega a la tabla token_blacklist. El access_token expira
out naturalmente (no hay revocación inmediata del access_token).
7.2 Gestión de Roles (RBAC)
Rol Actor Permisos Restricción
admin_sistema DevOps / IT Acceso total: ETL, modelos, usuarios, Solo desde
configuración. red interna
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 22

### Tablas detectadas en esta sección:
| 1. Login | El usuario envía {email, password} al endpoint POST /api/v1/auth/login. |
| --- | --- |
| 2. Veri ficació n | AuthService consulta la tabla usuarios por email. Verifica la contraseña con passlib.verify(password, password_hash) usando bcrypt. |
| 3. Gen eració n de T okens | Si las credenciales son válidas: genera access_token (JWT RS256, exp: 8h) y refresh_token (JWT RS256, exp: 24h con JTI único). |
| 4. Alm acena mient o Refr esh | El refresh_token JTI se almacena hasheado en la tabla refresh_tokens con el user_id y timestamp de expiración. |
| 5. Req uest A utenti cado | El cliente incluye el access_token en el header: Authorization: Bearer . FastAPI lo valida via Dependency (get_current_user). |
| 6. Ren ovació n | Cuando el access_token expira, el cliente usa el refresh_token en POST /auth/refresh para obtener un nuevo par de tokens (rotation). |
| 7. Log out | El JTI del refresh_token se agrega a la tabla token_blacklist. El access_token expira naturalmente (no hay revocación inmediata del access_token). |


| Rol | Actor | Permisos | Restricción |
| --- | --- | --- | --- |
| admin_sistema | DevOps / IT | Acceso total: ETL, modelos, usuarios, configuración. | Solo desde red interna |



<!-- Página 23 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
administrador_tienda Administrador de Ver predicciones, alertas, registrar ventas reales, Filtrado por
Tienda ajuste manual. Solo su sucursal. id_sucursal
gerencia Gerencia General Lectura de dashboards, tendencias, comparativa Sin escritura
entre sucursales. Solo lectura.
area_financiera Área Financiera Lectura de métricas de precisión, reportes de Sin escritura
ahorro estimado.
7.3 Tecnologías
(cid:127) python-JOSE 3.x: Creación y verificación de JWTs con algoritmo RS256 (asimétrico). Las claves RSA se
generan una vez y se montan como secretos Docker.
(cid:127) Passlib + bcrypt: Hashing de contraseñas con bcrypt (cost factor 12). Nunca se almacena la contraseña en
texto plano. La verificación usa passlib.context.verify() que es resistente a timing attacks.
(cid:127) FastAPI Dependency Injection: La función get_current_user() es un dependency inyectado en cada
endpoint protegido. Verifica firma, expiración y blacklist del JWT en cada request.
(cid:127) Middleware de Logging: Cada request autenticado registra: user_id, rol, endpoint, método, ip_origen,
timestamp, status_code en el log de auditoría.
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 23

### Tablas detectadas en esta sección:
| administrador_tienda | Administrador de Tienda | Ver predicciones, alertas, registrar ventas reales, ajuste manual. Solo su sucursal. | Filtrado por id_sucursal |
| --- | --- | --- | --- |
| gerencia | Gerencia General | Lectura de dashboards, tendencias, comparativa entre sucursales. Solo lectura. | Sin escritura |
| area_financiera | Área Financiera | Lectura de métricas de precisión, reportes de ahorro estimado. | Sin escritura |



<!-- Página 24 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
SECCIÓN 8
MÓDULO WEB DASHBOARD — INTERFAZ DE USUARIO
El Web Dashboard es una Single Page Application (SPA) en React.js que provee a cada actor una interfaz
visual adaptada a sus necesidades. Prioriza la usabilidad para usuarios sin formación técnica (RNF-03): tiempo
de aprendizaje <= 2 horas para las funciones principales.
8.1 Vistas por Actor
Actor: Administrador de Tienda
Panel de alertas activas con badges de prioridad. Predicciones de la semana
Dashboard próxima para cada SKU de su sucursal. Semáforo visual (verde/amarillo/rojo)
Principal según nivel de stock vs demanda proyectada.
Gráfica de serie temporal (Recharts LineChart): historial 12 semanas +
Vista de proyección 4 semanas + bandas de confianza (área sombreada). Etiqueta
Predicción por 'BAJA CONFIANZA' cuando MAPE > 25%. Botón de ajuste manual con campo
SKU de justificación.
Registro de Formulario simple para registrar la cantidad vendida de la semana cerrada por
Venta Real SKU. Validación de campo requerido y rango numérico.
Historial de Tabla de alertas históricas con filtros por tipo, fecha, SKU. Botón 'Marcar como
Alertas atendida' por alerta.
Actor: Gerencia General
Métricas clave en cards: promedio MAPE actual, % alertas atendidas, SKUs
Dashboard con predicción confiable. Gráfica de tendencia de demanda agregada por
Ejecutivo categoría.
Comparativa Para un SKU seleccionado: gráfica multi-línea con la demanda proyectada de
entre cada sucursal. Tabla de error histórico por sucursal para identificar patrones
Sucursales atípicos.
Actor: Área Financiera
Métricas de Panel con MAPE, MAE y Bias del modelo activo vs anterior. Gráfica de
Modelo evolución del MAPE a lo largo del tiempo (por versión de modelo).
Tabla con estimación de reducción de quiebres (% semana a semana) y
Reporte de reducción de sobrestock en perecederos. Basado en comparativa predicción vs
Impacto venta real.
8.2 Componentes React Principales
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 24

### Tablas detectadas en esta sección:
| Dashboard Principal | Panel de alertas activas con badges de prioridad. Predicciones de la semana próxima para cada SKU de su sucursal. Semáforo visual (verde/amarillo/rojo) según nivel de stock vs demanda proyectada. |
| --- | --- |


| Vista de Predicción por SKU | Gráfica de serie temporal (Recharts LineChart): historial 12 semanas + proyección 4 semanas + bandas de confianza (área sombreada). Etiqueta 'BAJA CONFIANZA' cuando MAPE > 25%. Botón de ajuste manual con campo de justificación. |
| --- | --- |


| Registro de Venta Real | Formulario simple para registrar la cantidad vendida de la semana cerrada por SKU. Validación de campo requerido y rango numérico. |
| --- | --- |


| Historial de Alertas | Tabla de alertas históricas con filtros por tipo, fecha, SKU. Botón 'Marcar como atendida' por alerta. |
| --- | --- |


| Dashboard Ejecutivo | Métricas clave en cards: promedio MAPE actual, % alertas atendidas, SKUs con predicción confiable. Gráfica de tendencia de demanda agregada por categoría. |
| --- | --- |


| Comparativa entre Sucursales | Para un SKU seleccionado: gráfica multi-línea con la demanda proyectada de cada sucursal. Tabla de error histórico por sucursal para identificar patrones atípicos. |
| --- | --- |


| Métricas de Modelo | Panel con MAPE, MAE y Bias del modelo activo vs anterior. Gráfica de evolución del MAPE a lo largo del tiempo (por versión de modelo). |
| --- | --- |


| Reporte de Impacto | Tabla con estimación de reducción de quiebres (% semana a semana) y reducción de sobrestock en perecederos. Basado en comparativa predicción vs venta real. |
| --- | --- |



<!-- Página 25 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
Componente Archivo Descripción
AlertBadge components/AlertBadge.jsx Badge con color e ícono por tipo de alerta. Se actualiza via
WebSocket sin recargar la página.
DemandChart components/DemandChart.js Gráfica Recharts con historial + proyección + bandas de
x confianza. Tooltips con valores exactos.
StockSemaphore components/StockSemaphor Indicador visual verde/amarillo/rojo según ratio
e.jsx stock_actual/demanda_estimada.
PredictionCard components/PredictionCard.js Tarjeta por SKU con demanda T+1, intervalo de confianza,
x badge de confianza del modelo.
ManualAdjustModal components/ManualAdjustMo Modal con input numérico + textarea de justificación para
dal.jsx ajuste manual de predicción.
SucursalComparison components/SucursalCompar Gráfica multi-línea Recharts para comparativa entre
ison.jsx sucursales. Solo visible para gerencia.
MetricsPanel components/MetricsPanel.jsx Panel de métricas MAPE/MAE/Bias con comparativa entre
versiones de modelo. Con sparklines.
8.3 Tecnologías Frontend
(cid:127) React.js 18+: SPA con React Router para navegación sin recarga. Context API para estado global de usuario
autenticado y alertas activas.
(cid:127) Recharts 2.x: Librería de gráficas basada en D3.js. Usada para DemandChart (LineChart + AreaChart para
bandas de confianza) y MetricsPanel (BarChart + LineChart).
(cid:127) Axios 1.x: Cliente HTTP con interceptors para inyectar automáticamente el Bearer token en cada request y
manejar renovación de tokens expirados.
(cid:127) TanStack Query (React Query) 5.x: Caché de datos del servidor, revalidación automática y estados de
loading/error para todas las llamadas a la API.
(cid:127) WebSocket nativo (browser API): Conexión al canal /ws/alerts/{token} para recibir alertas en tiempo real sin
polling.
(cid:127) Tailwind CSS 3.x: Utility-first CSS. Paleta de colores consistente con el diseño del sistema. Responsive para
tablets (resolución mínima 768px).
(cid:127) Vite 5.x: Build tool con HMR (Hot Module Replacement) para desarrollo. Build optimizado con code splitting
para producción.
(cid:127) Vitest + React Testing Library: Pruebas de componentes con mocks de la API. Cobertura de componentes
críticos (DemandChart, AlertBadge, ManualAdjustModal).
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 25

### Tablas detectadas en esta sección:
| Componente | Archivo | Descripción |
| --- | --- | --- |
| AlertBadge | components/AlertBadge.jsx | Badge con color e ícono por tipo de alerta. Se actualiza via WebSocket sin recargar la página. |
| DemandChart | components/DemandChart.js x | Gráfica Recharts con historial + proyección + bandas de confianza. Tooltips con valores exactos. |
| StockSemaphore | components/StockSemaphor e.jsx | Indicador visual verde/amarillo/rojo según ratio stock_actual/demanda_estimada. |
| PredictionCard | components/PredictionCard.js x | Tarjeta por SKU con demanda T+1, intervalo de confianza, badge de confianza del modelo. |
| ManualAdjustModal | components/ManualAdjustMo dal.jsx | Modal con input numérico + textarea de justificación para ajuste manual de predicción. |
| SucursalComparison | components/SucursalCompar ison.jsx | Gráfica multi-línea Recharts para comparativa entre sucursales. Solo visible para gerencia. |
| MetricsPanel | components/MetricsPanel.jsx | Panel de métricas MAPE/MAE/Bias con comparativa entre versiones de modelo. Con sparklines. |



<!-- Página 26 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
SECCIÓN 9
INTEGRACIÓN ENTRE MÓDULOS
Esta sección describe cómo los módulos se comunican entre sí, sus interfaces contractuales y las reglas de
integración que garantizan el desacoplamiento definido en los principios arquitectónicos.
9.1 Mapa de Dependencias
El flujo de dependencias es estrictamente unidireccional de izquierda a derecha en el diagrama conceptual.
Ningún módulo interno conoce los detalles de implementación de otro módulo; solo conoce su interfaz (puerto).
Módulo Origen Módulo Destino Tipo de Comunicación Contrato / Interfaz
Sistema ETL Service SQL Read-Only Tabla ventas con campos: fecha, sku,
Facturación (SQLAlchemy) cantidad, precio, sucursal
ETL Service Data Store SQL Write (SQLAlchemy Interfaz IDataRepository.save_sales(df:
Upsert) DataFrame) -> int
REST API ETL Service Llamada directa Python ETLOrchestrator.run() -> ETLResult
(mismo proceso)
REST API ML Engine Llamada directa Python MLEngine.predict(sku_ids, sucursal_id) ->
List[Prediction]
ML Engine Data Store SQL Read/Write IModelRepository, IPredictionRepository,
(SQLAlchemy) ISalesRepository
ML Engine Alert Engine Llamada directa Python AlertEngine.evaluate(prediction_ids:
(post-predicción) List[int]) -> List[Alert]
Alert Engine Data Store SQL Write (SQLAlchemy) IAlertRepository.save(alert: Alert) -> int
Alert Engine Web Dashboard WebSocket (Starlette) JSON: {type, alert_id, sku_id, message,
priority, timestamp}
Web Dashboard REST API HTTP/HTTPS (Axios) OpenAPI Spec en /docs. Bearer JWT en
todos los requests.
Auth Service Data Store SQL Read/Write IUserRepository, ITokenRepository
(SQLAlchemy)
ML Engine MLflow HTTP (MLflow Python mlflow.log_params(),
client) mlflow.log_metrics(),
mlflow.sklearn.log_model()
9.2 Contratos de Datos (Data Transfer Objects)
Los DTOs son schemas Pydantic que definen el contrato exacto de datos entre módulos. Su uso garantiza que
un cambio en la implementación interna de un módulo no rompa otros módulos mientras el DTO no cambie.
PredictionResponse (API -> Frontend)
id_prediccion: int id_producto: int nombre_producto: str id_sucursal: int semana_predicha: int
anio_predicho: int cantidad_estimada: int limite_inferior: int limite_superior: int
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 26

### Tablas detectadas en esta sección:
| Módulo Origen | Módulo Destino | Tipo de Comunicación | Contrato / Interfaz |
| --- | --- | --- | --- |
| Sistema Facturación | ETL Service | SQL Read-Only (SQLAlchemy) | Tabla ventas con campos: fecha, sku, cantidad, precio, sucursal |
| ETL Service | Data Store | SQL Write (SQLAlchemy Upsert) | Interfaz IDataRepository.save_sales(df: DataFrame) -> int |
| REST API | ETL Service | Llamada directa Python (mismo proceso) | ETLOrchestrator.run() -> ETLResult |
| REST API | ML Engine | Llamada directa Python | MLEngine.predict(sku_ids, sucursal_id) -> List[Prediction] |
| ML Engine | Data Store | SQL Read/Write (SQLAlchemy) | IModelRepository, IPredictionRepository, ISalesRepository |
| ML Engine | Alert Engine | Llamada directa Python (post-predicción) | AlertEngine.evaluate(prediction_ids: List[int]) -> List[Alert] |
| Alert Engine | Data Store | SQL Write (SQLAlchemy) | IAlertRepository.save(alert: Alert) -> int |
| Alert Engine | Web Dashboard | WebSocket (Starlette) | JSON: {type, alert_id, sku_id, message, priority, timestamp} |
| Web Dashboard | REST API | HTTP/HTTPS (Axios) | OpenAPI Spec en /docs. Bearer JWT en todos los requests. |
| Auth Service | Data Store | SQL Read/Write (SQLAlchemy) | IUserRepository, ITokenRepository |
| ML Engine | MLflow | HTTP (MLflow Python client) | mlflow.log_params(), mlflow.log_metrics(), mlflow.sklearn.log_model() |



<!-- Página 27 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
confianza_alta: bool ajuste_manual: bool cantidad_ajustada: Optional[int]
timestamp_generacion: datetime
AlertResponse (API -> Frontend)
id_alerta: int tipo: str mensaje: str id_producto: int nombre_producto: str id_sucursal: int
fecha_generacion: datetime atendida: bool
ModelMetricsResponse (API -> Frontend)
id_modelo: int tipo: str version: str mape: float mae: float bias: float fecha_entrenamiento:
datetime estado: str es_modelo_activo: bool
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 27


<!-- Página 28 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
SECCIÓN 10
DESPLIEGUE E INFRAESTRUCTURA
El sistema se despliega mediante Docker Compose, orquestando todos los servicios en contenedores
independientes sobre el servidor provisto por el cliente (Linux Ubuntu 22.04+ o instancia cloud básica). Todo el
sistema es desplegable con un único comando: docker-compose up -d.
10.1 Servicios Docker
Servicio Rol Imagen Base Puerto Descripción
nginx Reverse Proxy nginx:alpine 80, 443 Punto de entrada único. Termina
SSL/TLS. Sirve el build estático del
frontend. Proxea /api/ hacia el
backend.
backend FastAPI + Uvicorn python:3.11-slim 8000 Contiene: REST API, Auth Service,
(custom) (interno) ETL Service, Alert Engine. 4 workers
Uvicorn.
ml_engi ML Engine Worker python:3.11-slim — Proceso Python dedicado al ciclo de
ne (custom) entrenamiento y predicción. Comparte
volumen /data con backend.
mlflow MLflow Server python:3.11-slim 5000 Tracking server de MLflow. Persiste
(custom) (interno) experimentos y modelos en
/mlflow-data.
db PostgreSQL postgres:16-alpi 5432 Base de datos principal. Datos
ne (interno) persistidos en volumen Docker
/pgdata.
fronten React Build node:18-alpine — Stage de build. El artefacto estático
d (build stage) es copiado al contenedor Nginx.
10.2 Variables de Entorno (.env)
Todas las configuraciones sensibles y variables de entorno se definen en un archivo .env que NUNCA se
versiona en el repositorio (incluido en .gitignore). El archivo .env.example documenta todas las variables
requeridas:
# Base de datos destino (provisto por cliente)
DATABASE_TARGET_URL=postgresql://user:pass@db:5432/demand24
# Base de datos fuente (facturación, solo lectura)
DATABASE_SOURCE_URL=postgresql://ro_user:pass@host:5432/facturacion
# JWT (generar con: openssl genrsa -out private.pem 2048)
JWT_PRIVATE_KEY_PATH=/run/secrets/jwt_private.pem
JWT_PUBLIC_KEY_PATH=/run/secrets/jwt_public.pem
JWT_ACCESS_TOKEN_EXPIRE_HOURS=8
JWT_REFRESH_TOKEN_EXPIRE_HOURS=24
# MLflow
MLFLOW_TRACKING_URI=http://mlflow:5000
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 28

### Tablas detectadas en esta sección:
| Servicio | Rol | Imagen Base | Puerto | Descripción |
| --- | --- | --- | --- | --- |
| nginx | Reverse Proxy | nginx:alpine | 80, 443 | Punto de entrada único. Termina SSL/TLS. Sirve el build estático del frontend. Proxea /api/ hacia el backend. |
| backend | FastAPI + Uvicorn | python:3.11-slim (custom) | 8000 (interno) | Contiene: REST API, Auth Service, ETL Service, Alert Engine. 4 workers Uvicorn. |
| ml_engi ne | ML Engine Worker | python:3.11-slim (custom) | — | Proceso Python dedicado al ciclo de entrenamiento y predicción. Comparte volumen /data con backend. |
| mlflow | MLflow Server | python:3.11-slim (custom) | 5000 (interno) | Tracking server de MLflow. Persiste experimentos y modelos en /mlflow-data. |
| db | PostgreSQL | postgres:16-alpi ne | 5432 (interno) | Base de datos principal. Datos persistidos en volumen Docker /pgdata. |
| fronten d | React Build | node:18-alpine (build stage) | — | Stage de build. El artefacto estático es copiado al contenedor Nginx. |



<!-- Página 29 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
# Configuración del piloto
PILOT_SKU_IDS=101,102,103,104,105 # IDs definidos por gerencia
MIN_WEEKS_HISTORY=12
MAPE_LOW_CONFIDENCE_THRESHOLD=25.0
ETL_SCHEDULE_CRON='0 5 * * 1' # Lunes 5AM
10.3 Estructura del Repositorio
demand-24/
nnn backend/
n nnn api/ # FastAPI routers por dominio
n nnn auth/ # Auth Service (JWT, bcrypt, RBAC)
n nnn etl/ # ETL pipeline (connectors, transformers, loaders)
n nnn ml_engine/ # Pipeline ML (data, models, training, prediction)
n nnn alert_engine/ # Motor de alertas
n nnn models/ # SQLAlchemy ORM models
n nnn schemas/ # Pydantic DTOs (request/response)
n nnn repositories/ # Repository pattern (DB abstraction)
n nnn config/ # Settings, constants, YAML configs
n nnn tests/ # pytest: unit + integration tests
nnn frontend/
n nnn src/
n n nnn components/ # React components reutilizables
n n nnn pages/ # Vistas por actor (Admin, Gerencia, Financiero)
n n nnn hooks/ # Custom hooks (useAlerts, usePredictions)
n n nnn services/ # Axios API clients por módulo
n n nnn context/ # AuthContext, AlertContext
n nnn tests/ # Vitest + RTL
nnn nginx/
n nnn nginx.conf # Config reverse proxy + SSL
nnn mlflow/
n nnn Dockerfile
nnn docker-compose.yml # Orquestación completa
nnn .env.example # Template de variables de entorno
nnn .gitignore # Incluye .env, *.pem, mlflow-data/
nnn README.md # Instrucciones de despliegue
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 29


<!-- Página 30 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
SECCIÓN 11
TRAZABILIDAD DE REQUERIMIENTOS
Esta matriz de trazabilidad vincula cada requerimiento funcional y no funcional del SRS con el módulo
arquitectónico que lo implementa y la tecnología específica responsable de su cumplimiento.
Trazabilidad Requerimientos Funcionales (RF)
ID Nombre Módulo Implementador Tecnología Clave Prioridad
RF0 Ingesta de Datos (ETL) ETL Service SQLAlchemy + Pandas + ALTA
1 APScheduler
RF0 Validación de Datos ETL Service Pydantic + Python custom rules ALTA
2 (DataValidator)
RF0 Generación de Predicción ML Engine (Predictor) scikit-learn + XGBoost + ALTA
3 statsmodels + MLflow
RF0 Alertas de Quiebre de Alert Engine + WebSocket Python + Starlette WebSockets ALTA
4 Stock
RF0 Visualización de Web Dashboard React.js + Recharts MEDIA
5 Tendencias (DemandChart)
RF0 Registro de Venta Real REST API + Data Store FastAPI endpoint + PostgreSQL ALTA
6
RF0 Reentrenamiento del ML Engine (Trainer) scikit-learn + MLflow Model Registry MEDIA
7 Modelo
RF0 Ajuste Manual de REST API + Web FastAPI PATCH endpoint + React BAJA
8 Predicción Dashboard Modal
RF0 Comparación entre Web Dashboard React.js + Recharts + FastAPI MEDIA
9 Sucursales (SucursalComparison)
Trazabilidad Requerimientos No Funcionales (RNF)
ID Categoría Módulo Implementador Mecanismo de Cumplimiento
RNF01 Rendimiento (<=30s) ML Engine + REST API Modelos pre-cargados en memoria. Uvicorn async.
Cache de predicciones recientes.
RNF02 Disponibilidad (99%) Docker + Nginx Restart policy: always en Docker Compose. Health
checks en Nginx. Alertas de downtime.
RNF03 Usabilidad (2h Web Dashboard Diseño con semáforos visuales, tooltips
aprendizaje) contextuales, mensajes de error descriptivos.
RNF04 Mantenibilidad Todos los módulos Repository pattern. Interfaces abstractas. pytest-cov
(SOLID, 70%) enforce 70%. Docstrings obligatorios.
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 30

### Tablas detectadas en esta sección:
| ID | Nombre | Módulo Implementador | Tecnología Clave | Prioridad |
| --- | --- | --- | --- | --- |
| RF0 1 | Ingesta de Datos (ETL) | ETL Service | SQLAlchemy + Pandas + APScheduler | ALTA |
| RF0 2 | Validación de Datos | ETL Service (DataValidator) | Pydantic + Python custom rules | ALTA |
| RF0 3 | Generación de Predicción | ML Engine (Predictor) | scikit-learn + XGBoost + statsmodels + MLflow | ALTA |
| RF0 4 | Alertas de Quiebre de Stock | Alert Engine + WebSocket | Python + Starlette WebSockets | ALTA |
| RF0 5 | Visualización de Tendencias | Web Dashboard (DemandChart) | React.js + Recharts | MEDIA |
| RF0 6 | Registro de Venta Real | REST API + Data Store | FastAPI endpoint + PostgreSQL | ALTA |
| RF0 7 | Reentrenamiento del Modelo | ML Engine (Trainer) | scikit-learn + MLflow Model Registry | MEDIA |
| RF0 8 | Ajuste Manual de Predicción | REST API + Web Dashboard | FastAPI PATCH endpoint + React Modal | BAJA |
| RF0 9 | Comparación entre Sucursales | Web Dashboard (SucursalComparison) | React.js + Recharts + FastAPI | MEDIA |


| ID | Categoría | Módulo Implementador | Mecanismo de Cumplimiento |
| --- | --- | --- | --- |
| RNF01 | Rendimiento (<=30s) | ML Engine + REST API | Modelos pre-cargados en memoria. Uvicorn async. Cache de predicciones recientes. |
| RNF02 | Disponibilidad (99%) | Docker + Nginx | Restart policy: always en Docker Compose. Health checks en Nginx. Alertas de downtime. |
| RNF03 | Usabilidad (2h aprendizaje) | Web Dashboard | Diseño con semáforos visuales, tooltips contextuales, mensajes de error descriptivos. |
| RNF04 | Mantenibilidad (SOLID, 70%) | Todos los módulos | Repository pattern. Interfaces abstractas. pytest-cov enforce 70%. Docstrings obligatorios. |



<!-- Página 31 -->
DEMAND-24 · Arquitectura Modular Detallada MiniMarket La 24 S.A.S. · Confidencial
RNF05 Escalabilidad (nuevos ETL + ML Engine + Data Configuracion YAML para lista de SKUs. Sin
SKU) Store cambios de código para agregar productos.
RNF06 Seguridad (HTTPS, Auth Service + Nginx + TLS en Nginx. JWT RS256. bcrypt contraseñas.
JWT) REST API RBAC en cada endpoint.
RNF07 Confiabilidad Modelo ML Engine + Web Flag confianza_alta=False cuando MAPE>25%.
Dashboard Badge visible en UI y alerta BAJA_CONFIANZA.
RNF08 Portabilidad (Docker, Docker Compose docker-compose up -d despliega todo. Sin
Linux) dependencias de software comercial.
RNF09 Trazabilidad (audit Data Store Tabla inmutable con permisos INSERT-only.
trail) (predicciones_trazas) Registro automático en cada predicción.
Nota del Arquitecto: Este documento define la arquitectura de referencia del sistema DEMAND-24.
La base de datos fisica (esquema SQL, indices, migraciones Alembic) sera integrada en una revision
subsecuente una vez el cliente provea acceso al sistema de facturacion existente. Todos los modulos
estan disenados para operar con el schema provisto sin modificaciones en la logica de negocio.
Documento generado: Abril 2025 | Versión: 1.0 | Estado: Vigente
MiniMarket La 24 S.A.S. — Ingeniería de Software — Universidad
Documento de Arquitectura de Software · v1.0 · Abril 2025 Página 31

### Tablas detectadas en esta sección:
| RNF05 | Escalabilidad (nuevos SKU) | ETL + ML Engine + Data Store | Configuracion YAML para lista de SKUs. Sin cambios de código para agregar productos. |
| --- | --- | --- | --- |
| RNF06 | Seguridad (HTTPS, JWT) | Auth Service + Nginx + REST API | TLS en Nginx. JWT RS256. bcrypt contraseñas. RBAC en cada endpoint. |
| RNF07 | Confiabilidad Modelo | ML Engine + Web Dashboard | Flag confianza_alta=False cuando MAPE>25%. Badge visible en UI y alerta BAJA_CONFIANZA. |
| RNF08 | Portabilidad (Docker, Linux) | Docker Compose | docker-compose up -d despliega todo. Sin dependencias de software comercial. |
| RNF09 | Trazabilidad (audit trail) | Data Store (predicciones_trazas) | Tabla inmutable con permisos INSERT-only. Registro automático en cada predicción. |


