# -*- coding: utf-8 -*-
"""
Genera el PDF resumen de la fase de entrenamiento del proyecto de forecasting.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, ListFlowable, ListItem, KeepTogether
)
from reportlab.pdfbase.pdfmetrics import stringWidth
import os

OUT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "Resumen_Fase_Entrenamiento.pdf",
)

styles = getSampleStyleSheet()

# --- Estilos personalizados ---
styles.add(ParagraphStyle(
    name="TituloPortada", fontName="Helvetica-Bold", fontSize=24,
    leading=30, alignment=TA_CENTER, textColor=colors.HexColor("#1a2b4c"),
    spaceAfter=10
))
styles.add(ParagraphStyle(
    name="SubtituloPortada", fontName="Helvetica", fontSize=13,
    leading=18, alignment=TA_CENTER, textColor=colors.HexColor("#555555"),
    spaceAfter=6
))
styles.add(ParagraphStyle(
    name="H1", fontName="Helvetica-Bold", fontSize=16, leading=20,
    textColor=colors.HexColor("#1a2b4c"), spaceBefore=18, spaceAfter=10,
    borderPadding=(0, 0, 4, 0)
))
styles.add(ParagraphStyle(
    name="H2", fontName="Helvetica-Bold", fontSize=12.5, leading=16,
    textColor=colors.HexColor("#2e4a7a"), spaceBefore=12, spaceAfter=6
))
styles.add(ParagraphStyle(
    name="Cuerpo", fontName="Helvetica", fontSize=9.7, leading=14.2,
    alignment=TA_LEFT, spaceAfter=7
))
styles.add(ParagraphStyle(
    name="CuerpoNegrita", parent=styles["Cuerpo"], fontName="Helvetica-Bold"
))
styles.add(ParagraphStyle(
    name="Concepto", parent=styles["Cuerpo"], backColor=colors.HexColor("#eef2f8"),
    borderColor=colors.HexColor("#c3d2e8"), borderWidth=0.6, borderPadding=8,
    spaceBefore=4, spaceAfter=10, leftIndent=2
))
styles.add(ParagraphStyle(
    name="Codigo", fontName="Courier", fontSize=7.6, leading=10.2,
    backColor=colors.HexColor("#f4f4f4"), borderColor=colors.HexColor("#dddddd"),
    borderWidth=0.5, borderPadding=6, spaceBefore=4, spaceAfter=10,
    textColor=colors.HexColor("#222222")
))
styles.add(ParagraphStyle(
    name="Etiqueta", fontName="Helvetica-Bold", fontSize=8.5,
    textColor=colors.white, backColor=colors.HexColor("#c0392b"),
    borderPadding=4, spaceAfter=4
))
styles.add(ParagraphStyle(
    name="EtiquetaOK", parent=styles["Etiqueta"], backColor=colors.HexColor("#1e824c")
))
styles.add(ParagraphStyle(
    name="Pie", fontName="Helvetica-Oblique", fontSize=8, textColor=colors.grey
))

def code_block(text):
    """Convierte un bloque de código en un Paragraph con saltos de línea preservados."""
    escaped = (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    escaped = escaped.replace("\n", "<br/>").replace(" ", "&nbsp;")
    return Paragraph(escaped, styles["Codigo"])

def concepto(texto):
    return Paragraph("<b>💡 Concepto:</b> " + texto, styles["Concepto"])

def parrafo(texto):
    return Paragraph(texto, styles["Cuerpo"])

def h1(texto):
    return Paragraph(texto, styles["H1"])

def h2(texto):
    return Paragraph(texto, styles["H2"])

def bullet_list(items):
    return ListFlowable(
        [ListItem(Paragraph(it, styles["Cuerpo"]), leftIndent=6) for it in items],
        bulletType="bullet", start="•", leftIndent=14
    )

def tabla_metricas(headers, rows, col_widths=None):
    data = [headers] + rows
    t = Table(data, colWidths=col_widths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a2b4c")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f5fa")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t

story = []

# ============================================================
# PORTADA
# ============================================================
story.append(Spacer(1, 4.5 * cm))
story.append(Paragraph("Proyecto de Forecasting de Ventas", styles["TituloPortada"]))
story.append(Paragraph("Resumen de la fase de entrenamiento (entrenamiento.ipynb)", styles["SubtituloPortada"]))
story.append(Spacer(1, 0.6 * cm))
story.append(HRFlowable(width="60%", thickness=1.2, color=colors.HexColor("#1a2b4c"), hAlign="CENTER"))
story.append(Spacer(1, 0.8 * cm))
story.append(Paragraph("Preparado para: Diego Ramírez Cruz", styles["SubtituloPortada"]))
story.append(Paragraph("Curso de iniciación a Machine Learning aplicado — revisión y mejora del proyecto", styles["SubtituloPortada"]))
story.append(Spacer(1, 3 * cm))
story.append(Paragraph(
    "Este documento recoge, de forma explicada, todas las decisiones tomadas en la fase de "
    "entrenamiento del modelo: tanto lo desarrollado originalmente en el curso como las mejoras, "
    "correcciones de errores y ajustes de rigor aplicados durante la revisión conjunta.",
    styles["SubtituloPortada"]
))
story.append(PageBreak())

# ============================================================
# 0. CONTEXTO Y OBJETIVO
# ============================================================
story.append(h1("0. Contexto y objetivo del proyecto"))
story.append(parrafo(
    "El objetivo del proyecto es predecir las ventas futuras (<b>unidades_vendidas</b>) de un catálogo "
    "de productos de retail a partir de datos históricos de ventas (2021-2024) y de precios de la "
    "competencia (Amazon, Decathlon, Deporvillage). El resultado de esta fase será un modelo de Machine "
    "Learning entrenado, evaluado y validado con rigor, listo para generar predicciones sobre datos "
    "nuevos (noviembre 2025) en la fase de inferencia (<i>forecasting.ipynb</i>)."
))
story.append(parrafo(
    "Se ha optado por un <b>único modelo global</b> (todos los productos a la vez, con la identidad del "
    "producto como variable más) en vez de un modelo independiente por producto o por tipo de día. "
    "Con un dataset de este tamaño (unos pocos miles de filas), un modelo global permite compartir el "
    "aprendizaje entre productos y periodos, mientras que modelos segmentados se quedarían con muy "
    "pocos datos cada uno y tenderían a sobreajustar."
))

# ============================================================
# 1. PREPARACIÓN Y CALIDAD DE DATOS
# ============================================================
story.append(h1("1. Preparación y calidad de datos (fase previa al chat)"))
story.append(parrafo(
    "Antes de esta revisión ya se habían completado los siguientes pasos: carga de los datos de ventas "
    "y de precios de competencia desde CSV, un informe de calidad de datos (valores nulos, tipos, "
    "rangos), conversión de la columna <b>fecha</b> a formato datetime, y la unión (<i>merge</i>) de "
    "ambos datasets por fecha y producto mediante un <b>inner join</b>."
))
story.append(parrafo(
    "También se realizó un análisis exploratorio (EDA) completo: evolución temporal de ventas por año "
    "con foco en el pico de Black Friday, ventas por día de la semana, por categoría, por subcategoría, "
    "top 15 productos más vendidos, y comparación de la densidad de precios propios frente a los de "
    "la competencia."
))
story.append(concepto(
    "Un <b>inner join</b> conserva solo las filas cuya clave (fecha + producto) existe en ambos "
    "datasets. Es la opción correcta aquí: si un día no hay precio de competencia registrado para un "
    "producto, no tiene sentido mantener esa fila a medias, ya que faltaría información necesaria para "
    "las variables de precio relativo que se calculan más adelante."
))

# ============================================================
# 2. VARIABLES TEMPORALES Y DE CALENDARIO
# ============================================================
story.append(h1("2. Variables temporales y de calendario (fase previa al chat)"))
story.append(parrafo(
    "A partir de la columna <b>fecha</b> se generaron variables de calendario: <b>año</b>, <b>mes</b>, "
    "<b>día_mes</b>, <b>día_semana</b> (texto), <b>día_semana_num</b> (0-6), <b>trimestre</b>, "
    "<b>día_año</b> y <b>días_hasta_fin_año</b>. Además, banderas booleanas: <b>es_fin_semana</b>, "
    "<b>es_lunes</b>, <b>es_viernes</b>, <b>es_sabado</b>, <b>es_domingo</b>, <b>es_festivo</b>, "
    "<b>es_black_friday</b> y <b>es_cyber_monday</b>."
))
story.append(concepto(
    "Los modelos de árboles (como el que se usa aquí) no entienden fechas de forma nativa: no saben que "
    "el 25 de diciembre es Navidad ni que noviembre suele tener más ventas por el Black Friday. "
    "Descomponer la fecha en variables numéricas y booleanas explícitas es lo que le da al modelo la "
    "capacidad de aprender esos patrones estacionales mediante splits sobre esas columnas."
))

# ============================================================
# 3. VARIABLES PORCENTUALES Y DE PRECIO
# ============================================================
story.append(h1("3. Variables de descuento y precio de competencia"))
story.append(Paragraph("Revisado y corregido durante este chat", styles["EtiquetaOK"]))

story.append(h2("3.1 descuento_porcentaje"))
story.append(parrafo(
    "Variable que mide la diferencia porcentual entre el precio base y el precio de venta real."
))
story.append(code_block(
    "df['descuento_porcentaje'] = (\n"
    "    (df['precio_base'] - df['precio_venta']) / df['precio_base']\n"
    ") * 100"
))
story.append(Paragraph("Problema detectado y corregido", styles["Etiqueta"]))
story.append(parrafo(
    "La fórmula original tenía el signo invertido: <b>(precio_venta - precio_base) / precio_base</b>. "
    "Con esa versión, un descuento real (precio_venta &lt; precio_base) daba un valor <b>negativo</b>, "
    "lo cual es contraintuitivo para una variable llamada 'descuento'. Además, esto provocó que el "
    "análisis automático de correlación del propio notebook etiquetara como 'inesperada' una "
    "correlación que en realidad era totalmente lógica (a mayor descuento real, más ventas). Se "
    "invirtió el signo para que un valor positivo signifique 'hay descuento real', coherente con el "
    "nombre de la variable."
))
story.append(parrafo(
    "También se añadió una comprobación de seguridad antes del cálculo, para detectar si algún "
    "<b>precio_base</b> fuera 0 y evitar una división por cero silenciosa (<i>n_ceros = "
    "df['precio_base'].eq(0).sum()</i>). Resultado tras el fix: media 1.13%, mediana 0.43%, "
    "rango de -3% a 15% de descuento."
))

story.append(h2("3.2 precio_competencia y ratio_precio"))
story.append(code_block(
    "df['precio_competencia'] = df[['Amazon', 'Decathlon', 'Deporvillage']].mean(axis=1)\n"
    "df['ratio_precio'] = df['precio_venta'] / df['precio_competencia']"
))
story.append(parrafo(
    "<b>ratio_precio</b> normaliza el precio propio frente al precio medio del mercado: valores por "
    "encima de 1 indican que se vende más caro que la competencia, y por debajo de 1, más barato. Es "
    "una variable más informativa para el modelo que el precio absoluto, ya que generaliza mejor entre "
    "productos de gamas de precio muy distintas."
))
story.append(Paragraph("Decisión de rigor aplicada: multicolinealidad", styles["Etiqueta"]))
story.append(parrafo(
    "Tras calcular <b>descuento_porcentaje</b>, <b>precio_competencia</b> y <b>ratio_precio</b>, se "
    "eliminaron del dataframe las columnas <b>Amazon</b>, <b>Decathlon</b>, <b>Deporvillage</b>, "
    "<b>precio_venta</b> y <b>precio_competencia</b>. Se mantienen únicamente <b>precio_base</b>, "
    "<b>descuento_porcentaje</b> y <b>ratio_precio</b> como variables de precio."
))
story.append(concepto(
    "La <b>multicolinealidad determinística</b> ocurre cuando una variable es una combinación exacta "
    "de otras que también están en el dataset (por ejemplo, precio_venta, precio_base y "
    "descuento_porcentaje: con dos de ellas se deduce la tercera). En un modelo de árboles esto no "
    "rompe el entrenamiento, pero sí diluye la importancia entre columnas redundantes y complica la "
    "interpretación posterior (por ejemplo, el análisis de importancia de variables). Por eso se "
    "eliminan las columnas 'origen' una vez calculadas las variables derivadas, quedándose solo con la "
    "combinación mínima de variables no redundantes."
))

# ============================================================
# 4. ENCODING
# ============================================================
story.append(h1("4. Encoding de variables categóricas"))
story.append(Paragraph("Revisado y corregido durante este chat", styles["EtiquetaOK"]))
story.append(parrafo(
    "Se crean copias con sufijo <b>_h</b> de las variables categóricas relevantes, para poder aplicar "
    "one-hot encoding sobre las copias sin perder las columnas originales legibles (útiles para "
    "análisis y gráficos posteriores)."
))
story.append(code_block(
    "df['nombre_h'] = df['nombre']\n"
    "df['categoria_h'] = df['categoria']\n"
    "df['subcategoria_h'] = df['subcategoria']\n\n"
    "df = pd.get_dummies(\n"
    "    df, columns=['nombre_h', 'categoria_h', 'subcategoria_h'],\n"
    "    drop_first=False\n"
    ")"
))
story.append(Paragraph("Dos variables descartadas del encoding", styles["Etiqueta"]))
story.append(bullet_list([
    "<b>dia_semana_h</b>: se detectó que era información totalmente redundante — el día de la semana "
    "ya está capturado por <b>día_semana_num</b> (ordinal) y por las banderas "
    "<b>es_lunes/es_viernes/es_sabado/es_domingo/es_fin_semana</b>. Codificarlo una tercera vez solo "
    "añadía ruido y colinealidad.",
    "<b>nombre_festivo_h</b>: la columna original solo tenía 96 valores no nulos de 3.384 filas "
    "(festivos concretos, cada uno con apenas un puñado de apariciones en 4 años). Un one-hot sobre "
    "eso genera muchas columnas casi vacías, con muy poca capacidad de aprendizaje individual, y esa "
    "señal ya está mejor representada por <b>es_festivo</b>, <b>es_black_friday</b> y "
    "<b>es_cyber_monday</b>."
]))
story.append(concepto(
    "El <b>one-hot encoding</b> convierte una variable categórica de texto en varias columnas "
    "binarias (0/1), una por cada categoría posible, porque los modelos de Machine Learning necesitan "
    "números, no texto. El parámetro <b>drop_first=False</b> mantiene todas las categorías: en una "
    "regresión lineal esto causaría un problema de colinealidad perfecta (la 'trampa de la variable "
    "dummy'), pero en modelos de árboles como el usado aquí no es un problema, y conservarlas todas "
    "facilita la interpretación posterior por categoría."
))

# ============================================================
# 5. LAGS Y MEDIA MOVIL — EL BUG CRÍTICO
# ============================================================
story.append(h1("5. Variables de lags y media móvil — fuga de información detectada y corregida"))
story.append(Paragraph("Hallazgo crítico de este chat", styles["Etiqueta"]))
story.append(parrafo(
    "Esta fue la corrección más importante de toda la revisión: el código original generaba variables "
    "de lag (ventas de días anteriores) y media móvil con dos errores que provocaban <b>fuga de "
    "información (data leakage)</b>, inflando artificialmente el rendimiento del modelo."
))

story.append(h2("5.1 Código original (con los dos bugs)"))
story.append(code_block(
    "df = df.sort_values(['año', 'fecha', 'producto_id']).reset_index(drop=True)\n\n"
    "for año in sorted(df['año'].unique()):\n"
    "    mask_año = df['año'] == año\n"
    "    for lag in range(1, 8):\n"
    "        df.loc[mask_año, f'lag_{lag}_unidades_vendidas'] = \\\n"
    "            df.loc[mask_año, 'unidades_vendidas'].shift(lag)\n"
    "    df.loc[mask_año, 'media_movil_7_unidades_vendidas'] = \\\n"
    "        df.loc[mask_año, 'unidades_vendidas']\\\n"
    "          .rolling(window=7, min_periods=1).mean()"
))
story.append(bullet_list([
    "<b>Bug 1 — mezcla de productos:</b> el orden usado (año, fecha, producto_id) coloca todos los "
    "productos de un mismo día seguidos. Un <b>shift(1)</b> sobre esos datos no coge 'lo que vendió "
    "este producto ayer', sino 'lo que vendió el producto anterior en la lista, ese mismo día'. Los "
    "supuestos lags no eran lags temporales reales del mismo producto.",
    "<b>Bug 2 — la media móvil se mira a sí misma:</b> faltaba un <b>shift(1)</b> antes del "
    "<b>rolling()</b>. Sin él, la ventana de 7 días incluye el valor de la propia fila que se está "
    "prediciendo. En la primera fila de cada segmento (con min_periods=1), la media móvil era "
    "literalmente idéntica al valor real de ventas de ese día — el predictor contenía la respuesta.",
]))
story.append(concepto(
    "El <b>data leakage</b> (fuga de información) ocurre cuando una variable predictora contiene, "
    "directa o indirectamente, información que en un escenario real de predicción no estaría "
    "disponible en el momento de predecir — en este caso, el propio valor que se quiere predecir, o el "
    "de otro producto del mismo día que tampoco se conocería de antemano. Es uno de los errores más "
    "peligrosos en forecasting porque no rompe el código ni da errores: al contrario, hace que las "
    "métricas de validación parezcan mucho mejores de lo que el modelo realmente sería en producción. "
    "La señal de alarma que lo delató aquí fue un R² sospechosamente alto (0,93) para un problema de "
    "demanda retail."
))

story.append(h2("5.2 Código corregido"))
story.append(code_block(
    "df = df.sort_values(['producto_id', 'fecha']).reset_index(drop=True)\n\n"
    "for lag in range(1, 8):\n"
    "    df[f'lag_{lag}_unidades_vendidas'] = (\n"
    "        df.groupby('producto_id')['unidades_vendidas'].shift(lag)\n"
    "    )\n\n"
    "df['media_movil_7_unidades_vendidas'] = (\n"
    "    df.groupby('producto_id')['unidades_vendidas']\n"
    "      .transform(lambda s: s.shift(1).rolling(window=7, min_periods=1).mean())\n"
    ")\n\n"
    "df = df.dropna(subset=[f'lag_{i}_unidades_vendidas' for i in range(1, 8)]\n"
    "                + ['media_movil_7_unidades_vendidas'])"
))
story.append(parrafo(
    "El <b>groupby('producto_id')</b> garantiza que cada shift y cada media móvil se calculan dentro "
    "de la serie temporal de un único producto. Como efecto secundario positivo, al no reiniciar los "
    "lags en cada cambio de año (el código original sí lo hacía), se recuperan registros de 2022-2024 "
    "que antes se perdían de forma innecesaria."
))
story.append(parrafo(
    "<b>Impacto real del fix</b> — comparación de las métricas del modelo final antes y después de "
    "corregir el leakage:"
))
story.append(tabla_metricas(
    ["Métrica", "Con leakage (antes)", "Sin leakage (después, real)"],
    [
        ["MAE", "0.759", "1.002"],
        ["RMSE", "1.659", "1.935"],
        ["MAPE", "16.60%", "20.97%"],
        ["R²", "0.9296", "0.9040"],
    ],
    col_widths=[5.5*cm, 5*cm, 6*cm]
))
story.append(Spacer(1, 6))
story.append(parrafo(
    "El empeoramiento es real pero moderado, no catastrófico — señal de que el modelo seguía "
    "aprendiendo patrones genuinos (precio, estacionalidad, tendencia por producto) además de la fuga, "
    "y no dependía enteramente de ella."
))

# ============================================================
# 6. FASE DE MACHINE LEARNING
# ============================================================
story.append(PageBreak())
story.append(h1("6. Entrenamiento del modelo"))

story.append(h2("6.1 División train / validation"))
story.append(code_block(
    "train_df = df[df['año'].isin([2021, 2022, 2023])].copy()\n"
    "validation_df = df[df['año'] == 2024].copy()"
))
story.append(concepto(
    "En series temporales <b>no se puede dividir aleatoriamente</b> entre entrenamiento y validación: "
    "si se mezclan fechas de 2024 en el entrenamiento y de 2021 en la validación, el modelo estaría "
    "aprendiendo con información del futuro respecto a lo que se le pide predecir. Por eso se divide "
    "por corte cronológico estricto: todo 2024 queda después de todo el periodo de entrenamiento, tal "
    "y como ocurrirá en producción."
))

story.append(h2("6.2 Selección de variables predictoras — bug corregido"))
story.append(parrafo(
    "El filtro automático original (<i>dtype != 'object'</i>) no excluía las columnas de texto en el "
    "entorno de pandas usado, porque su dtype real es <b>'str'</b>, no <b>'object'</b>. Esto provocó "
    "un error de entrenamiento al intentar usar <b>producto_id</b> como número. Se sustituyó por una "
    "lista explícita de exclusión, más robusta y auditable:"
))
story.append(code_block(
    "cols_excluir = ['fecha', 'ingresos', 'unidades_vendidas',\n"
    "                'producto_id', 'nombre', 'categoria', 'subcategoria',\n"
    "                'día_semana', 'nombre_festivo', 'año']\n\n"
    "predictor_vars = [col for col in train_df.columns if col not in cols_excluir]"
))
story.append(parrafo(
    "<b>ingresos</b> se excluye porque se calcula a partir de la propia variable objetivo "
    "(unidades_vendidas × precio), así que incluirla sería fuga de información directa. <b>año</b> se "
    "excluyó tras el análisis de importancia de variables: un árbol de decisión no puede extrapolar "
    "más allá del rango de valores vistos en entrenamiento (2021-2023), así que en noviembre 2025 "
    "trataría 'año' como si fuera 2023, perdiendo cualquier tendencia real entre años."
))

story.append(h2("6.3 El modelo: HistGradientBoostingRegressor"))
story.append(concepto(
    "Es un modelo de <b>gradient boosting</b>: construye muchos árboles de decisión pequeños de forma "
    "secuencial, donde cada árbol nuevo se centra en corregir los errores que cometieron los árboles "
    "anteriores. Es una de las familias de modelos más efectivas para datos tabulares de tamaño "
    "pequeño-mediano como este: captura relaciones no lineales e interacciones entre variables de "
    "forma automática, no requiere escalar los datos (a diferencia de una regresión lineal), y tolera "
    "razonablemente bien la colinealidad entre variables."
))

story.append(h2("6.4 Walk-forward validation con TimeSeriesSplit"))
story.append(parrafo(
    "En vez de evaluar el modelo con un único corte fijo, se usa <b>TimeSeriesSplit(n_splits=5)</b> "
    "sobre <b>train_df</b> (2021-2023), que genera varias particiones respetando siempre el orden "
    "cronológico: en cada partición, el entrenamiento crece y la validación son siempre las filas "
    "cronológicamente posteriores."
))
story.append(concepto(
    "La <b>validación walk-forward</b> (o de ventana expansiva) da una estimación mucho más fiable del "
    "rendimiento real que un único split, porque promedia el error a lo largo de varios periodos en "
    "vez de depender de que el periodo de validación elegido haya sido, por azar, 'fácil' o 'difícil'. "
    "Es el estándar recomendado en forecasting profesional frente a una sola partición fija."
))

story.append(h2("6.5 Búsqueda automática de hiperparámetros: RandomizedSearchCV"))
story.append(code_block(
    "param_dist = {\n"
    "    'learning_rate': uniform(0.01, 0.19),\n"
    "    'max_iter': randint(150, 600),\n"
    "    'max_leaf_nodes': randint(15, 63),\n"
    "    'max_depth': randint(3, 12),\n"
    "    'min_samples_leaf': randint(10, 50),\n"
    "    'l2_regularization': uniform(0, 3),\n"
    "}\n\n"
    "search = RandomizedSearchCV(\n"
    "    estimator=base_model, param_distributions=param_dist,\n"
    "    n_iter=40, scoring='neg_mean_absolute_error',\n"
    "    cv=TimeSeriesSplit(n_splits=5), random_state=42, n_jobs=-1\n"
    ")\n"
    "search.fit(X_train, y_train)"
))
story.append(concepto(
    "En vez de fijar los hiperparámetros a mano por prueba y error, <b>RandomizedSearchCV</b> prueba "
    "automáticamente muchas combinaciones aleatorias dentro de los rangos definidos y se queda con la "
    "que mejor puntúa. El detalle importante aquí es que se usa el mismo esquema walk-forward "
    "(<b>TimeSeriesSplit</b>) también como validación interna de la búsqueda — si se usara una "
    "validación cruzada aleatoria normal, se estaría filtrando información temporal también durante el "
    "ajuste de hiperparámetros, no solo en la evaluación final. El año 2024 (validation_df) no "
    "participa en ningún momento de esta búsqueda: se reserva exclusivamente para la evaluación final, "
    "una sola vez."
))
story.append(parrafo("<b>Mejores hiperparámetros encontrados:</b>"))
story.append(tabla_metricas(
    ["Hiperparámetro", "Valor"],
    [
        ["learning_rate", "0.191"],
        ["max_iter", "338"],
        ["max_depth", "10"],
        ["max_leaf_nodes", "35"],
        ["min_samples_leaf", "48"],
        ["l2_regularization", "1.124"],
        ["MAE promedio en CV (walk-forward)", "1.463 unidades"],
    ],
    col_widths=[8*cm, 8.5*cm]
))

# ============================================================
# 7. RESULTADOS Y BASELINES
# ============================================================
story.append(PageBreak())
story.append(h1("7. Resultados finales y comparación con baselines"))
story.append(concepto(
    "Un resultado de error (MAE = 1 unidad, por ejemplo) no significa nada por sí solo: hay que "
    "compararlo contra un <b>baseline</b> — una estrategia de predicción trivial — para saber si el "
    "modelo realmente aporta valor. Se usaron dos: el <b>naive de la media</b> (predecir siempre la "
    "media histórica de ventas) y el <b>naive estacional</b> (predecir 'lo mismo que se vendió hace 7 "
    "días', usando la propia variable lag_7), este último mucho más exigente."
))
story.append(tabla_metricas(
    ["Métrica", "Modelo final", "Naive estacional (lag_7)", "Naive media"],
    [
        ["MAE", "1.002", "3.011", "3.420"],
        ["RMSE", "1.935", "7.458", "—"],
        ["MAPE", "20.97%", "—", "—"],
        ["R²", "0.9040", "-0.4250", "—"],
    ],
    col_widths=[4*cm, 4*cm, 5*cm, 3.5*cm]
))
story.append(Spacer(1, 8))
story.append(parrafo(
    "El modelo reduce el error frente al baseline más exigente (naive estacional) en aproximadamente "
    "un <b>67%</b> (MAE de 3.01 a 1.00), y pasa de un R² negativo (el naive estacional ni siquiera "
    "supera a predecir la media constante) a un R² de 0.904. Es una mejora clara e inequívoca."
))
story.append(h2("Qué mide cada métrica"))
story.append(bullet_list([
    "<b>MAE (Mean Absolute Error):</b> error medio en las mismas unidades que la variable objetivo "
    "(unidades vendidas) — el más fácil de comunicar al negocio.",
    "<b>RMSE (Root Mean Squared Error):</b> como el MAE, pero penaliza más los errores grandes. Es "
    "mayor que el MAE porque hay algunos errores puntuales más grandes (probablemente en picos de "
    "demanda como Black Friday, difíciles de acertar al 100%).",
    "<b>MAPE (Mean Absolute Percentage Error):</b> error medio en porcentaje. Es la métrica que mejor "
    "entiende un negocio ('nos equivocamos un 21% de media'), pero es más sensible en productos con "
    "ventas bajas, donde un pequeño error absoluto se traduce en un gran error relativo.",
    "<b>R² (coeficiente de determinación):</b> proporción de la variabilidad de las ventas que el "
    "modelo logra explicar. Un valor de 0.90 significa que el modelo captura el 90% de esa "
    "variabilidad.",
]))

# ============================================================
# 8. IMPORTANCIA DE VARIABLES
# ============================================================
story.append(h1("8. Importancia de variables (permutation importance)"))
story.append(concepto(
    "La <b>importancia por permutación</b> mide cuánto empeora el error del modelo cuando se baraja "
    "aleatoriamente (se destruye la relación con el objetivo) una columna a la vez, evaluado siempre "
    "sobre datos que el modelo no ha visto en entrenamiento (validation_df, 2024). Es más fiable que "
    "la importancia nativa de los árboles (feature_importances_), que está sesgada a favor de "
    "variables con muchos valores distintos y mide utilidad durante el propio entrenamiento, no "
    "capacidad real de generalizar."
))
story.append(code_block(
    "result = permutation_importance(\n"
    "    modelo_final, X_val, y_val,\n"
    "    n_repeats=20, random_state=42,\n"
    "    scoring='neg_mean_absolute_error', n_jobs=-1\n"
    ")"
))
story.append(parrafo(
    "Las columnas del one-hot encoding (nombre_h_*, categoria_h_*, subcategoria_h_*) se agruparon por "
    "variable original, ya que su importancia individual queda repartida entre decenas de columnas."
))
story.append(tabla_metricas(
    ["Variable / grupo", "Importancia media"],
    [
        ["lag_1_unidades_vendidas", "0.870"],
        ["descuento_porcentaje", "0.598"],
        ["lag_7_unidades_vendidas", "0.554"],
        ["ratio_precio", "0.223"],
        ["día_año", "0.162"],
        ["es_black_friday", "0.156"],
        ["media_movil_7_unidades_vendidas", "0.148"],
        ["mes", "0.077"],
        ["nombre_h (agrupado)", "0.054"],
        ["categoria_h (agrupado)", "0.042"],
    ],
    col_widths=[9*cm, 7.5*cm]
))
story.append(Spacer(1, 8))
story.append(h2("Lectura de negocio"))
story.append(bullet_list([
    "La <b>inercia reciente</b> domina claramente (lag_1 y lag_7): lo que se vendió ayer y hace una "
    "semana es, con diferencia, la mejor señal de lo que se venderá hoy.",
    "El <b>precio propio</b> (descuento_porcentaje) y el <b>precio relativo a la competencia</b> "
    "(ratio_precio) son drivers reales confirmados con un método riguroso, no solo por correlación "
    "simple.",
    "La <b>estacionalidad</b> (día_año, mes) y los <b>eventos comerciales</b> (es_black_friday) "
    "también son relevantes.",
    "La <b>identidad del producto o categoría</b> (nombre_h, categoria_h) aporta relativamente poco "
    "una vez que el modelo ya conoce los lags de ese mismo producto — su efecto ya queda capturado "
    "indirectamente a través del historial reciente de ventas.",
]))
story.append(concepto(
    "Limitación importante del método: si una variable apenas varía dentro del conjunto de validación "
    "(por ejemplo, es_cyber_monday, con muy pocos días positivos al año), barajarla apenas cambia el "
    "error y su importancia sale artificialmente baja o nula, sin que eso signifique que el modelo no "
    "la use en absoluto."
))

# ============================================================
# 9. CONCLUSIONES
# ============================================================
story.append(h1("9. Conclusiones y estado final del proyecto"))
story.append(parrafo(
    "La fase de entrenamiento queda cerrada con un modelo riguroso y defendible: sin fuga de "
    "información, con una selección de variables libre de colinealidad determinística innecesaria, "
    "validado con un esquema walk-forward y con hiperparámetros ajustados automáticamente. El modelo "
    "final reduce el error un ~67% frente al mejor baseline disponible y su comportamiento (según el "
    "análisis de importancia) es coherente con el sentido común del negocio: inercia de demanda, "
    "precio y estacionalidad como principales impulsores."
))
story.append(h2("Principales mejoras aplicadas respecto al proyecto de curso original"))
story.append(bullet_list([
    "Corrección del signo de descuento_porcentaje para que sea interpretable.",
    "Eliminación de colinealidad determinística en variables de precio (precio_venta, precio_competencia).",
    "Eliminación de codificaciones redundantes en el encoding (día de la semana, festivos dispersos).",
    "Corrección de un bug crítico de data leakage en los lags y la media móvil.",
    "Sustitución de un filtro de selección de variables poco fiable por una exclusión explícita.",
    "Paso de un único split a validación walk-forward con TimeSeriesSplit.",
    "Búsqueda automática de hiperparámetros con RandomizedSearchCV, respetando el orden temporal.",
    "Eliminación de 'año' como predictora por su incapacidad de extrapolación en modelos de árboles.",
    "Incorporación de un baseline naive estacional, más exigente que el naive de la media.",
    "Análisis de importancia de variables por permutación para validar la coherencia del modelo.",
])) 
story.append(Spacer(1, 10))
story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#cccccc")))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "Próximo paso: fase de inferencia sobre datos nuevos (forecasting.ipynb), aplicando exactamente "
    "el mismo pipeline de transformación de variables validado en este documento.",
    styles["Pie"]
))

doc = SimpleDocTemplate(
    OUT_PATH, pagesize=A4,
    topMargin=2.2*cm, bottomMargin=2*cm, leftMargin=2*cm, rightMargin=2*cm,
    title="Resumen Fase de Entrenamiento - Proyecto Forecasting",
    author="Claude"
)
doc.build(story)
print("PDF generado en", OUT_PATH)
