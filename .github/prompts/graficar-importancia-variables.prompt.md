---
description: "Genera una celda de notebook con gráficos de importancia de variables para un modelo de forecasting"
name: "Graficar importancia de variables"
argument-hint: "Indica el notebook o el contexto del modelo si no está seleccionado"
agent: "agent"
---
Crea una única celda de código Python para el notebook de forecasting seleccionado o indicado.

La celda debe:
- Usar el DataFrame `importancias`, que ya contiene las columnas `variable`, `importancia_media` e `importancia_std`.
- Generar un gráfico de barras horizontal que muestre la importancia de cada variable usando `importancia_media`.
- Generar un gráfico de porciones que represente `importancia_std` por variable.
- Ordenar las variables para que el gráfico de barras sea fácil de leer y mostrar etiquetas claras, títulos, ejes y leyendas en español.
- Mantener una figura separada para cada gráfico y aplicar `plt.tight_layout()` antes de mostrarlos.
- Usar únicamente las librerías permitidas por el proyecto: `pandas`, `numpy`, `matplotlib`, `seaborn`, `scikit-learn`, `jupyter` y `streamlit`. No uses Plotly ni otras librerías.
- Reutilizar las variables existentes y no asumir columnas que no estén disponibles. Si hay demasiadas variables para que el gráfico de porciones sea legible, usar las 10 variables con mayor `importancia_std` y agrupar el resto como `Resto`, explicándolo con una breve nota en el código.

Devuelve únicamente el contenido de la celda en formato JSON válido para un archivo `.ipynb`, dentro de un objeto con `cell_type`, `metadata` (incluyendo `language: "python"`) y `source` como una lista de líneas. No incluyas comentarios fuera del JSON ni referencias a IDs de celdas.
