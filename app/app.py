import streamlit as st
import pandas as pd
import numpy as np
import joblib
import seaborn as sns
import matplotlib.pyplot as plt

# ============================================================================
# RECÁLCULO DE VARIABLES DE PRECIO SEGÚN LOS CONTROLES DEL USUARIO
# ============================================================================
def recalcular_variables_precio(df_producto, descuento_pct, escenario_competencia):
    """
    Recalcula precio_venta, Amazon/Decathlon/Deporvillage, precio_competencia,
    descuento_porcentaje y ratio_precio según los controles elegidos.
    NO toca los lags — de eso se encarga la función recursiva, por separado.

    descuento_pct: número entre -50 y 50 (el slider)
    escenario_competencia: 'actual', 'competencia_baja' o 'competencia_alta'
    """
    df = df_producto.copy()

    # Precio de venta a partir del descuento elegido sobre precio_base
    df['precio_venta'] = df['precio_base'] * (1 - descuento_pct / 100)
    # Es matemáticamente equivalente a la fórmula original
    # ((precio_base - precio_venta) / precio_base) * 100, así que lo dejamos directo
    df['descuento_porcentaje'] = descuento_pct

    # Precios de competencia ajustados según el escenario
    ajustes = {'actual': 1.0, 'competencia_baja': 0.95, 'competencia_alta': 1.05}
    ajuste = ajustes[escenario_competencia]
    for col in ['Amazon', 'Decathlon', 'Deporvillage']:
        df[col] = df[col] * ajuste
    df['precio_competencia'] = df[['Amazon', 'Decathlon', 'Deporvillage']].mean(axis=1)

    # ratio_precio depende de los dos anteriores, se recalcula el último
    df['ratio_precio'] = df['precio_venta'] / df['precio_competencia']

    return df


# ============================================================================
# PREDICCIÓN RECURSIVA, DÍA A DÍA, PARA UN ÚNICO PRODUCTO
# ============================================================================
def predecir_recursivo(df_producto, modelo, predictor_vars):
    """
    Predice unidades_vendidas para los 30 días de noviembre de un producto,
    actualizando los lags con cada predicción nueva.

    El día 1 usa los lags que ya vienen calculados desde octubre (datos reales).
    A partir del día 2, lag_1 pasa a ser la predicción del día anterior (no un
    dato real), lag_2 el lag_1 de ayer, etc. — por eso el error tiende a crecer
    a medida que avanza el mes: cada predicción se apoya en la anterior, no en
    datos reales.
    """
    df = df_producto.sort_values('fecha').reset_index(drop=True)
    predicciones = []

    # Historial de los últimos 7 días (reales o predichos), ordenado de más
    # antiguo a más reciente. Se inicializa con los lags YA correctos del día 1
    # (lag_7 = hace 7 días, ..., lag_1 = ayer)
    fila_dia1 = df.iloc[0]
    historial = [fila_dia1[f'lag_{i}_unidades_vendidas'] for i in range(7, 0, -1)]

    for idx in range(len(df)):
        fila_df = df.iloc[[idx]].copy()  # DataFrame de 1 fila, para no perder los dtypes

        if idx > 0:
            # A partir del 2 de noviembre: sustituimos los lags por el historial
            # que hemos ido construyendo con nuestras propias predicciones
            for i in range(1, 8):
                fila_df.loc[fila_df.index[0], f'lag_{i}_unidades_vendidas'] = historial[-i]
            fila_df.loc[fila_df.index[0], 'media_movil_7_unidades_vendidas'] = np.mean(historial)
        # Si idx == 0 (1 de noviembre), no tocamos nada: usamos los lags reales del fichero

        prediccion = modelo.predict(fila_df[predictor_vars])[0]
        prediccion = max(0, prediccion)  # no tiene sentido predecir ventas negativas

        predicciones.append(prediccion)
        historial.append(prediccion)
        historial.pop(0)  # nos quedamos solo con la ventana de los últimos 7 días

    df['unidades_predichas'] = predicciones
    df['ingresos_proyectados'] = df['unidades_predichas'] * df['precio_venta']
    return df

# ============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================================
st.set_page_config(
    page_title="Predicción de Ventas - Noviembre 2025",
    page_icon="🛍️",
    layout="wide"
)

# ============================================================================
# CARGA DE MODELO Y DATOS
# ============================================================================
# @st.cache_resource / @st.cache_data evitan recargar el modelo y el CSV en
# CADA interacción del usuario (Streamlit vuelve a ejecutar todo el script
# de arriba a abajo cada vez que se mueve un slider o se pulsa un botón)
@st.cache_resource
def cargar_modelo():
    try:
        return joblib.load('models/modelo_final.joblib')
    except FileNotFoundError:
        st.error("No se ha encontrado el modelo en 'models/modelo_final.joblib'")
        st.stop()

@st.cache_data
def cargar_datos():
    try:
        df = pd.read_csv('data/processed/df_inferencia_transformado.csv')
        df['fecha'] = pd.to_datetime(df['fecha'])
        return df
    except FileNotFoundError:
        st.error("No se ha encontrado 'data/processed/df_inferencia_transformado.csv'")
        st.stop()

modelo_final = cargar_modelo()
df_transformado = cargar_datos()
predictor_vars = list(modelo_final.feature_names_in_)

# ============================================================================
# SIDEBAR: CONTROLES DE SIMULACIÓN
# ============================================================================
st.sidebar.title("🎛️ Controles de Simulación")

productos = df_transformado[['producto_id', 'nombre']].drop_duplicates().sort_values('nombre')
nombre_producto = st.sidebar.selectbox("Producto", productos['nombre'].tolist())
producto_id_seleccionado = productos.loc[productos['nombre'] == nombre_producto, 'producto_id'].iloc[0]

descuento_pct = st.sidebar.slider(
    "Ajuste de precio (%)", min_value=-50, max_value=50, value=0, step=5,
    help="Positivo = descuento (precio más bajo). Negativo = subida de precio."
)

escenario_label = st.sidebar.radio(
    "Escenario de competencia",
    options=["Actual (0%)", "Competencia -5%", "Competencia +5%"]
)
mapa_escenario = {
    "Actual (0%)": "actual",
    "Competencia -5%": "competencia_baja",
    "Competencia +5%": "competencia_alta"
}
escenario_competencia = mapa_escenario[escenario_label]

simular = st.sidebar.button("🚀 Simular Ventas", use_container_width=True)

# ============================================================================
# EJECUTAR SIMULACIÓN AL PULSAR EL BOTÓN
# ============================================================================
if simular:
    with st.spinner("Calculando predicciones día a día..."):
        df_producto = df_transformado[df_transformado['producto_id'] == producto_id_seleccionado].copy()
        df_producto = recalcular_variables_precio(df_producto, descuento_pct, escenario_competencia)
        resultado = predecir_recursivo(df_producto, modelo_final, predictor_vars)

    # Se guarda en session_state para que no desaparezca si luego el usuario
    # toca otro control sin volver a pulsar "Simular Ventas"
    st.session_state['resultado'] = resultado
    st.session_state['nombre_producto'] = nombre_producto
    st.session_state['descuento_pct'] = descuento_pct
    st.session_state['escenario_label'] = escenario_label

# ============================================================================
# ZONA PRINCIPAL
# ============================================================================
if 'resultado' not in st.session_state:
    st.info("👈 Elige un producto y pulsa **Simular Ventas** en el panel lateral para empezar.")
    st.stop()

resultado = st.session_state['resultado']

# --- Header ---
st.title("🛍️ Simulación de Ventas — Noviembre 2025")
st.subheader(f"Producto: {st.session_state['nombre_producto']}")
st.caption(f"Descuento aplicado: {st.session_state['descuento_pct']}% · "
           f"Escenario de competencia: {st.session_state['escenario_label']}")

st.divider()

# --- KPIs ---
unidades_totales = resultado['unidades_predichas'].sum()
ingresos_totales = resultado['ingresos_proyectados'].sum()
precio_promedio = resultado['precio_venta'].mean()
descuento_promedio = resultado['descuento_porcentaje'].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("📦 Unidades totales proyectadas", f"{unidades_totales:,.0f}")
col2.metric("💰 Ingresos proyectados", f"{ingresos_totales:,.2f} €")
col3.metric("🏷️ Precio medio de venta", f"{precio_promedio:,.2f} €")
col4.metric("🔖 Descuento medio", f"{descuento_promedio:.1f} %")

st.divider()

# --- Gráfico de predicción diaria ---
st.subheader("📈 Evolución de unidades vendidas durante el mes")

fig, ax = plt.subplots(figsize=(12, 5))
sns.lineplot(data=resultado, x='fecha', y='unidades_predichas',
             marker='o', linewidth=2.5, color='#667eea', ax=ax)

fila_bf = resultado[resultado['es_black_friday']]
if not fila_bf.empty:
    fecha_bf = fila_bf['fecha'].iloc[0]
    unidades_bf = fila_bf['unidades_predichas'].iloc[0]

    ax.axvline(x=fecha_bf, color='#e74c3c', linestyle='--', linewidth=2, alpha=0.6)
    ax.scatter([fecha_bf], [unidades_bf], color='#e74c3c', s=120, zorder=5,
               edgecolor='white', linewidth=1.5)
    ax.annotate('Black Friday', xy=(fecha_bf, unidades_bf),
                xytext=(10, 15), textcoords='offset points',
                fontsize=10, fontweight='bold', color='#e74c3c',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                          edgecolor='#e74c3c', alpha=0.9))

ax.set_xlabel("Fecha")
ax.set_ylabel("Unidades vendidas")
fig.autofmt_xdate(rotation=45)
sns.despine()
st.pyplot(fig)

st.divider()

# --- Tabla detallada ---
st.subheader("📋 Detalle diario")

tabla = resultado[['fecha', 'día_semana', 'precio_venta', 'precio_competencia',
                    'descuento_porcentaje', 'unidades_predichas',
                    'ingresos_proyectados', 'es_black_friday']].copy()

dias_es = {'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
           'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'}
tabla['día_semana'] = tabla['día_semana'].replace(dias_es)
tabla['fecha'] = tabla['fecha'].dt.strftime('%Y-%m-%d')
tabla['unidades_predichas'] = tabla['unidades_predichas'].round(0).astype(int)
for col in ['precio_venta', 'precio_competencia', 'descuento_porcentaje', 'ingresos_proyectados']:
    tabla[col] = tabla[col].round(2)

tabla['📌'] = tabla['es_black_friday'].apply(lambda x: '🔥' if x else '')
tabla = tabla.drop(columns='es_black_friday').rename(columns={
    'fecha': 'Fecha', 'día_semana': 'Día', 'precio_venta': 'Precio venta (€)',
    'precio_competencia': 'Precio competencia (€)', 'descuento_porcentaje': 'Descuento (%)',
    'unidades_predichas': 'Unidades', 'ingresos_proyectados': 'Ingresos (€)'
})

st.dataframe(
    tabla[['📌', 'Fecha', 'Día', 'Precio venta (€)', 'Precio competencia (€)',
           'Descuento (%)', 'Unidades', 'Ingresos (€)']],
    use_container_width=True, hide_index=True
)