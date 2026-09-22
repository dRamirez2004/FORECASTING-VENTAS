# Forecasting de Ventas — Noviembre 2025

Sistema de predicción de ventas diarias para 24 productos de retail, entrenado con histórico 2021-2024 y aplicado a la predicción de noviembre de 2025. Incluye el pipeline de entrenamiento, la preparación de datos de inferencia y una aplicación Streamlit interactiva para simular distintos escenarios de precio y competencia.

Proyecto desarrollado como parte del curso Data Science For Business (DS4B), con un nivel de rigor superior al planteamiento simplificado del curso: pipeline de scikit-learn real (no encoding manual), validación *walk-forward*, año 2024 reservado como test final nunca visto durante el ajuste, y prevención explícita de fuga de datos en variables de lag.

## Objetivo

Predecir `unidades_vendidas` diarias, por producto, durante noviembre de 2025 — con especial atención al comportamiento alrededor de Black Friday (28 de noviembre) — a partir de variables de calendario, precio, descuento y competencia.

## Estructura del repositorio

```
FORECASTING VENTAS/
├── data/
│   ├── raw/
│   │   ├── entrenamiento/
│   │   │   ├── ventas.csv              # Histórico de ventas 2021-2024
│   │   │   └── competencia.csv         # Precios de competencia 2021-2024
│   │   └── inferencia/
│   │       └── ventas_2025_inferencia.csv   # Real octubre 2025 + planificado noviembre 2025
│   └── processed/
│       ├── df.csv                           # Dataset de entrenamiento, features ya calculadas
│       └── df_inferencia_transformado.csv   # Noviembre 2025, listo para el modelo
├── models/
│   └── modelo_final.joblib             # Pipeline completo: OneHotEncoder + HistGradientBoostingRegressor
├── notebooks/
│   ├── entrenamiento.ipynb             # EDA, feature engineering, entrenamiento y evaluación
│   └── forecasting.ipynb               # Preparación de datos de inferencia (noviembre 2025)
├── app/
│   └── app.py                          # Aplicación Streamlit de simulación
└── README.md
```

## Datos

- **Ventas**: 24 productos, ventana de octubre-noviembre de cada año (2021-2024), ~150 registros por producto.
- **Competencia**: precios diarios de tres competidores (Amazon, Decathlon, Deporvillage) por producto.
- **Inferencia 2025**: mismo esquema, con octubre 2025 ya real (usado para calcular los lags iniciales de noviembre) y noviembre 2025 con `precio_base`, `precio_venta` y precios de competencia ya planificados, pero `unidades_vendidas` desconocida — es la variable a predecir.

## Metodología

### Ingeniería de variables

- **Calendario**: día de la semana, fin de semana, festivos (librería `holidays`, España), Black Friday, Cyber Monday, trimestre, día del año, etc.
- **Precio**: `descuento_porcentaje` (sobre `precio_base`), `ratio_precio` (precio propio frente a la media de competencia).
- **Lags**: `lag_1_unidades_vendidas` … `lag_7_unidades_vendidas` y `media_movil_7_unidades_vendidas`, calculados **por producto** (nunca cruzando de un producto a otro) y con `.shift(1)` antes del `rolling()` para que la media móvil de un día no incluya las ventas de ese mismo día.

### Prevención de fuga de datos

- Los lags se calculan agrupando por `producto_id` antes de desplazar la serie.
- 2024 se reserva íntegro como test final: nunca participa en la búsqueda de hiperparámetros, solo se usa una vez, al final, para evaluar.
- Validación cruzada con `TimeSeriesSplit` (walk-forward) sobre 2021-2023, no K-Fold aleatorio, para respetar el orden temporal.
- El encoding de variables categóricas (`nombre`, `categoria`, `subcategoria`) va dentro de un `Pipeline` de scikit-learn (`ColumnTransformer` + `OneHotEncoder`), no aplicado a mano con `pd.get_dummies()`: así el mismo objeto guardado se encarga de aplicar exactamente el mismo encoding en entrenamiento, validación e inferencia, sin riesgo de que las columnas generadas no coincidan.
- `año` se excluye deliberadamente de las predictoras, para no depender de un valor (2025) nunca visto en entrenamiento.

### Modelo y validación

- **Modelo**: `HistGradientBoostingRegressor` (scikit-learn), dentro de un `Pipeline` junto al `ColumnTransformer`.
- **Búsqueda de hiperparámetros**: `RandomizedSearchCV` con `TimeSeriesSplit(n_splits=5)`, optimizando MAE, sobre 2021-2023.
- **Evaluación final**: una única vez, sobre 2024 (nunca visto).
- **Baseline de referencia**: modelo naive estacional (predicción = valor de hace 7 días).

**Métricas del modelo final (validación 2024):**

| Métrica | Modelo final | Baseline naive estacional |
|---|---|---|
| MAE | 0.976 | 3.0113 |
| RMSE | 2.031 | 55.6261 |
| MAPE | 20.08% | 7.4583 |
| R² | 0.8943 | -0.4250 |

> Los valores exactos están impresos al final de `entrenamiento.ipynb`; quedan pendientes de rellenar aquí con los de tu última ejecución.

## Cómo ejecutar el proyecto

### Requisitos

- Python 3.11
- Un entorno para los notebooks (conda) y otro para la app (`.venv`) — **importante**: mantenerlos sincronizados en las mismas versiones de librerías (especialmente `scikit-learn`, ya que el modelo se deserializa con `joblib` y necesita las mismas clases disponibles en ambos entornos). Generar un `requirements.txt` desde el entorno de conda (`pip freeze > requirements.txt`) e instalarlo igual en el `.venv` evita desajustes.
- Librerías principales: `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `seaborn`, `holidays`, `joblib`, `streamlit`.

### 1. Entrenamiento

Ejecutar `notebooks/entrenamiento.ipynb` de principio a fin. Genera `models/modelo_final.joblib` (el Pipeline completo, listo para usar) y `data/processed/df.csv`.

### 2. Preparación de datos de inferencia

Ejecutar `notebooks/forecasting.ipynb` de principio a fin. Aplica la misma ingeniería de variables que el entrenamiento sobre los datos de octubre-noviembre 2025 y genera `data/processed/df_inferencia_transformado.csv`, filtrado a solo noviembre.

Solo el **1 de noviembre** tiene lags completamente reales (calculados con datos reales de octubre); el resto del mes tiene los lags anulados a propósito, porque se completan de forma recursiva en la app.

### 3. Aplicación Streamlit

Desde la **raíz del proyecto** (no desde dentro de `app/`), con el entorno `.venv` activado:

```bash
streamlit run app/app.py
```

Las rutas del script (`data/...`, `models/...`) son relativas al directorio desde el que se lanza el comando, no a la ubicación de `app.py`.

## La app: cómo funciona

**Controles (sidebar):**
- Selector de producto.
- Ajuste de precio (-50% a +50% sobre `precio_base`; positivo = descuento, negativo = subida de precio).
- Escenario de competencia (actual, competencia -5%, competencia +5%).

**Predicción recursiva:** el modelo predice noviembre día a día. El 1 de noviembre usa lags reales de octubre. A partir del 2, `lag_1` pasa a ser la predicción del día anterior (no un dato real), y así sucesivamente — por lo que el error esperado crece a medida que avanza el mes, ya que cada predicción se apoya en la anterior en lugar de en datos observados.

**Zona principal:** KPIs (unidades e ingresos totales, precio medio, descuento medio), gráfico de evolución diaria con Black Friday marcado, tabla detallada día a día, y comparativa de los 3 escenarios de competencia manteniendo el ajuste de precio elegido.

## Limitaciones y próximos pasos

- **Predicción puntual, sin intervalos de incertidumbre**: el sistema da un único número por día, sin rango. Dado que el error se acumula a lo largo de la metodología recursiva, sería más honesto comunicar un intervalo que crece con el horizonte, especialmente de cara a decisiones de stock. _(Próxima mejora planificada.)_
- **Validación limitada a un producto concreto** durante el desarrollo de la app: con ~150 registros históricos por producto repartidos en 4 años, es esperable que el modelo se comporte mejor en unos productos que en otros; falta una revisión sistemática por producto.
- **Los precios de noviembre 2025 son planificados, no observados**: `precio_venta` y los precios de competencia para noviembre proceden de un escenario base asumido en los datos de entrada, no de hechos ya ocurridos, a diferencia de octubre.
- **Entornos de conda y `.venv` sin `requirements.txt` compartido**, con el riesgo de desincronización ya visto una vez durante el desarrollo.

## Autor

Diego Ramírez Cruz
