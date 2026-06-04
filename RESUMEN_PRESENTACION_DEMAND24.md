# DEMAND-24 — Resumen del Proyecto
## Sistema Inteligente de Predicción de Demanda para MiniMarket La 24 S.A.S.

**Equipo de Desarrollo:**
- Elías José Blanco Gil — T00078817
- Mateo Reyes — T00077079
- Sebastian Valencia Montesino — T00078248
- Jose Pereira Acuña — T00079768
- Fabián Corpas Castro — T00064976

*

---

## ¿Qué es DEMAND-24?

DEMAND-24 es una plataforma web con inteligencia artificial que predice cuántos productos va a vender un minimarket la próxima semana. La idea es sencilla: en lugar de que el dueño de la tienda adivine cuánto pedir de cada producto, el sistema analiza el historial de ventas, aprende patrones y le dice "la semana que viene vas a vender aproximadamente X unidades de tal producto". Con eso, se evitan dos problemas clásicos del comercio: quedarse sin producto (quiebre de stock) o comprar de más y tener dinero parado en estantes.

El sistema no solo predice, sino que también genera alertas automáticas cuando detecta que un producto está en riesgo de agotarse, y presenta toda la información en un panel visual donde el gerente puede tomar decisiones informadas.

---

## ¿Qué problema resuelve?

Un minimarket típico maneja cientos de productos. El encargado de compras suele basarse en su experiencia o en anotaciones a mano para decidir cuánto pedir. Esto genera:

- **Productos agotados** cuando la demanda sube y no se anticipó.
- **Sobrestock** cuando se compra de más por miedo a quedarse sin nada.
- **Pérdida de dinero** en ambos casos: o se pierden ventas, o se inmoviliza capital.

DEMAND-24 ataca estos problemas directamente. El sistema aprende del pasado para anticipar el futuro, y le da al encargado información clara y visual para decidir mejor.

---

## ¿Cómo se construyó? — La historia del desarrollo

### Fase 1: Sentar las bases 
Lo primero fue planificar. Antes de escribir una sola línea de código, nos sentamos a analizar toda la documentación del proyecto: los requerimientos del negocio, la arquitectura propuesta y los mockups del dashboard.

**La decisión más importante de esta fase** fue definir cómo se iba a organizar el código. Decidimos dividir el proyecto en tres módulos completamente separados:

1. **El cerebro de la IA** (Módulo Analítico) — Se encarga exclusivamente de analizar datos y generar predicciones. No sabe nada sobre la base de datos ni sobre la pantalla.
2. **El motor del negocio** (Lógica de Negocio) — Se encarga de guardar datos, gestionar alertas y servir información al dashboard. No sabe cómo funcionan los modelos de IA.
3. **La cara visible** (Visualización) — Es el dashboard web que ve el usuario. Solo muestra datos, no tiene lógica de negocio ni inteligencia artificial adentro.

¿Por qué esta separación tan estricta? Porque si mañana queremos cambiar el modelo de IA, no tenemos que tocar nada del dashboard. Y si queremos rediseñar la interfaz, no tenemos que tocar nada de la IA. Cada pieza es independiente.

También en esta fase elegimos las herramientas de trabajo y creamos la estructura de carpetas del repositorio en GitHub.

---

### Fase 2: Construir la inteligencia artificial 

Esta fue la fase más intensa del proyecto. Aquí construimos todo el motor de predicción desde cero.

**¿De dónde salieron los datos?**

Usamos un dataset público de Kaggle llamado "Store Sales — Time Series Forecasting", que contiene datos reales de ventas diarias de un supermercado ecuatoriano (Corporación Favorita). Tiene miles de registros con múltiples tiendas y familias de productos, lo que lo hacía perfecto para simular el escenario de un minimarket con varias sucursales.

**¿Cómo procesamos los datos?**

Los datos originales son diarios, pero el minimarket hace pedidos semanales. Así que lo primero fue agrupar las ventas por semana (de lunes a domingo). Para eso creamos un componente llamado DataAggregator.

Después, necesitábamos darle "pistas" al modelo de IA para que pudiera aprender mejor. Creamos un componente llamado FeatureBuilder que calcula cosas como:
- ¿En qué mes y semana del año estamos? (porque hay temporadas de mayor venta)
- ¿Cuánto se vendió las últimas 1, 2, 3 y 4 semanas? (para detectar tendencias recientes)
- ¿Cuál es el promedio de ventas del último mes y del último trimestre? (para entender el comportamiento general)

**¿Qué modelo de IA usamos?**

Elegimos **XGBoost**, un algoritmo de Machine Learning que funciona construyendo árboles de decisión de forma secuencial. Es uno de los modelos más usados en competencias de ciencia de datos porque es rápido, preciso y relativamente fácil de configurar. Lo envolvimos en una capa intermedia para que, si algún día queremos cambiar a otro algoritmo, solo tengamos que modificar un archivo en vez de todo el sistema.

**¿Cómo nos aseguramos de que las predicciones fueran confiables?**

Este fue un punto crítico. En datos de series de tiempo (ventas a lo largo del tiempo), no se puede mezclar el pasado con el futuro durante el entrenamiento. Si el modelo "ve" datos del futuro mientras aprende, las métricas salen artificialmente buenas pero en la realidad fallaría.

Para evitar esto usamos una técnica llamada **Walk-Forward Validation**: el modelo entrena con las primeras semanas, predice la siguiente, luego avanza una semana, entrena de nuevo con más datos, predice la siguiente, y así sucesivamente. Es como simular que el modelo está operando en producción y tiene que predecir cada semana sin conocer el futuro.

---

### Fase 3: Conectar con la base de datos 

Con la IA funcionando, el siguiente paso fue darle memoria al sistema. Las predicciones no pueden quedarse solo en la computadora del desarrollador; necesitan guardarse en una base de datos accesible.

**¿Qué base de datos usamos?**

Elegimos **Supabase**, que es básicamente PostgreSQL (una base de datos relacional muy robusta) pero gestionada en la nube. Supabase nos dio además autenticación de usuarios "gratis" (login, registro, manejo de sesiones), lo que nos ahorró construir eso desde cero.

**¿Qué guardamos?**

Creamos 5 tablas principales:
- **sku**: Los productos del minimarket (nombre, familia, tienda, si está activo o no)
- **prediction**: Cada predicción generada (producto, semana, valor predicho, intervalos de confianza, porcentaje de error)
- **model_version**: Un registro de cada vez que se entrena el modelo (fecha, parámetros usados, si cumplió el criterio de aceptación)
- **evaluation_fold**: Los resultados detallados de la validación del modelo por cada período
- **alert**: Las alertas automáticas de quiebre de stock

**¿Cómo conectamos la IA con la base de datos?**

Usamos **SQLAlchemy**, que es una herramienta de Python que nos permite trabajar con la base de datos usando clases y objetos en vez de escribir consultas SQL a mano. Encima de eso, implementamos un patrón llamado **Repository**: cada tabla tiene su propio "administrador" que se encarga de crear, leer, actualizar y borrar registros. Así, si mañana cambiamos de base de datos, solo modificamos los repositorios sin tocar el resto del sistema.

También usamos **Pydantic** para definir contratos de datos: antes de que cualquier información entre o salga de la base de datos, se valida automáticamente que tenga el formato correcto.

En esta fase se escribieron 53 tests adicionales que verifican que la capa de datos funcione bien, usando una base de datos temporal en memoria (SQLite) para que los tests sean rápidos y no dependan de internet.

---

### Fase 4: Construir la API 

Hasta este punto teníamos la IA funcionando y los datos guardándose. Pero el dashboard web no puede hablar directamente con Python ni con la base de datos. Necesitábamos un intermediario: una API REST.

**¿Qué es una API REST?**

Es como un mesero en un restaurante. El dashboard (el cliente) le pide información al mesero (la API), el mesero va a la cocina (la IA y la base de datos), trae los datos, y se los entrega al cliente en un formato que entienda (JSON). El cliente nunca entra a la cocina.

**¿Con qué la construimos?**

Usamos **FastAPI**, un framework de Python diseñado específicamente para construir APIs modernas. Es rápido, genera documentación automática (puedes probar todos los endpoints desde el navegador), y se integra perfectamente con Pydantic para validar los datos.


---

### Fase 5: Construir el dashboard 

Con toda la lógica funcionando detrás, llegó el momento de construir lo que el usuario realmente ve y toca.

**¿Con qué lo construimos?**

Usamos **React** (versión 19), que es una librería de JavaScript para construir interfaces de usuario basadas en componentes reutilizables. Para que el desarrollo fuera rápido, usamos **Vite** como herramienta de compilación, que actualiza los cambios en el navegador casi al instante mientras desarrollamos.

**¿Cómo se ve?**

El dashboard tiene un diseño oscuro (Dark Mode) con una estética moderna. No es solo funcional, sino que buscamos que se sintiera profesional y agradable a la vista. Para eso usamos:

- **Framer Motion** para animaciones suaves: las tarjetas aparecen con transiciones, los paneles se abren con fluidez.
- **Recharts** para los gráficos: se pueden ver las ventas históricas junto con la predicción futura, incluyendo una banda sombreada que representa el intervalo de confianza (el rango dentro del cual esperamos que caiga la demanda real).
- **Lucide** para los íconos, que le dan un aspecto limpio y moderno a la navegación.

**¿Qué secciones tiene?**

- **Tarjetas de KPIs**: Muestran de un vistazo cuántos productos hay activos, cuál es la precisión general del modelo y cuántas alertas hay.
- **Gráfico de demanda**: Un gráfico interactivo donde se puede ver la demanda histórica vs. la predicción, con intervalos de confianza.
- **Centro de riesgos**: Un panel que lista las alertas de productos en riesgo de quiebre de stock.
- **Tabla de predicciones**: Un listado detallado producto por producto con sus predicciones, errores y nivel de confianza.
- **Barra lateral**: Navegación entre las diferentes secciones del dashboard.

**¿Cómo se conecta con el backend?**

Usamos **Axios** (una librería de JavaScript para hacer peticiones HTTP) para comunicarnos con la API de FastAPI. Para la autenticación de usuarios, nos conectamos directamente con **Supabase Auth** desde el frontend, lo que nos dio login, registro y manejo de sesiones sin tener que construirlo nosotros.

---

## Calidad del código

No nos conformamos con que el código "funcionara". Implementamos varias prácticas para garantizar su calidad:

**Tests automatizados:**
Se escribieron más de 80 tests que verifican que cada pieza del sistema funcione correctamente. Cada test se puede ejecutar con un solo comando y en segundos sabemos si algo se rompió. Los tests cubren desde las operaciones más básicas de la base de datos hasta el flujo completo de predicción.

**Integración continua (CI/CD):**
Configuramos **GitHub Actions** para que cada vez que alguien sube código al repositorio, automáticamente se ejecuten todos los tests y se analice la calidad del código. Si algo falla, el equipo se entera inmediatamente.

**Análisis estático con SonarCloud:**
Integramos **SonarCloud**, una herramienta que revisa el código buscando errores potenciales, código duplicado, vulnerabilidades de seguridad y malas prácticas. El proyecto pasa el "Quality Gate" de SonarCloud, que exige al menos un 80% de cobertura de tests en código nuevo.



---

## Resumen de herramientas utilizadas

### Para la inteligencia artificial
- **XGBoost**: El modelo de Machine Learning que genera las predicciones de demanda.
- **scikit-learn**: Nos proporcionó herramientas de validación (TimeSeriesSplit) para evaluar el modelo sin hacer trampa con datos futuros.
- **pandas**: La herramienta principal para manipular y transformar los datos tabulares (agrupar ventas por semana, calcular promedios, etc.).
- **NumPy**: Para cálculos matemáticos rápidos sobre grandes volúmenes de datos.

### Para el backend
- **FastAPI**: El framework con el que construimos la API REST. Nos dio documentación automática y validación de datos.
- **SQLAlchemy**: Nos permitió trabajar con la base de datos usando clases de Python en vez de SQL crudo.
- **Pydantic**: Valida que los datos que entran y salen del sistema tengan el formato correcto.
- **python-dotenv**: Lee la configuración desde un archivo .env para no tener contraseñas ni parámetros escritos directamente en el código.

### Para el frontend
- **React**: La librería para construir la interfaz de usuario por componentes.
- **Vite**: La herramienta de compilación que hace que el desarrollo sea ultrarrápido.
- **Recharts**: La librería de gráficos que usamos para visualizar la demanda.
- **Framer Motion**: Para las animaciones y transiciones del dashboard.
- **Axios**: Para comunicar el frontend con la API del backend.

### Para la base de datos
- **Supabase (PostgreSQL)**: Base de datos relacional en la nube donde guardamos productos, predicciones, métricas y alertas.
- **Supabase Auth**: Sistema de autenticación para login y registro de usuarios.

### Calidad del codigo
- **GitHub Actions**: Ejecuta tests automáticamente en cada push al repositorio.
- **SonarCloud**: Analiza la calidad del código y detecta problemas potenciales.
- **Git/GitHub**: Control de versiones y colaboración del equipo.

---

## Lo que aprendimos

1. **Documentar todo desde el día uno** nos salvó muchas horas. Cada sesión de trabajo quedó registrada en una bitácora, y cuando retomábamos el proyecto días después, sabíamos exactamente dónde habíamos quedado.
2. **Los tests son nuestra red de seguridad.** Con 80+ tests pasando, podíamos hacer cambios con confianza de que no estábamos rompiendo nada.
3. **La separación en módulos realmente funciona.** Cuando construimos el dashboard, no tuvimos que tocar una sola línea de la IA. Y cuando ajustamos la base de datos, el frontend no se enteró.
4. **Configurar todo desde un archivo externo** hizo que el despliegue a la nube fuera mucho más fácil: solo cambiamos las variables de entorno y todo funcionó.
5. **La validación temporal es esencial** cuando trabajas con datos de series de tiempo. Sin ella, las métricas mienten.


