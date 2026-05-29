# ============================================================
# sellers_dashboard.py
# Dashboard interactivo de vendedores con Streamlit
# Uso: streamlit run sellers_dashboard.py
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Configuración general de la página ──────────────────────
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# ── Título principal ─────────────────────────────────────────
st.title("📊 Sales Dashboard — Sellers Report")
st.markdown("Upload your `sellers.xlsx` file to explore the data.")

# ── Uploader de archivo ──────────────────────────────────────
# El usuario sube su propio archivo Excel desde la interfaz
uploaded_file = st.file_uploader("Upload sellers.xlsx", type=["xlsx", "csv"])

# Si no se ha subido archivo, detener la ejecución aquí
if uploaded_file is None:
    st.info("👆 Please upload the sellers Excel file to get started.")
    st.stop()

# ── Carga del archivo subido ─────────────────────────────────
# Detecta si es CSV o Excel y lo lee con pandas
if uploaded_file.name.endswith(".csv"):
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_excel(uploaded_file)

# Mostrar mensaje de éxito con número de registros cargados
st.success(f"✅ File loaded: **{len(df)} rows** and **{len(df.columns)} columns**")

# ── Normalización de nombres de columnas ─────────────────────
# Quita espacios extra y convierte a título para uniformidad
df.columns = [col.strip() for col in df.columns]

# Intentar detectar automáticamente las columnas clave
# Se buscan variantes comunes de nombres de columnas
def find_col(df, candidates):
    """Busca la primera columna del DataFrame que coincida con la lista de candidatos."""
    for c in candidates:
        for col in df.columns:
            if c.lower() in col.lower():
                return col
    return None

col_region   = find_col(df, ["Region", "Región", "region"])
col_seller   = find_col(df, ["Seller", "Vendedor", "Sales Rep", "Name"])
col_units    = find_col(df, ["Units Sold", "Units", "Unidades"])
col_total    = find_col(df, ["Total Sales", "Total", "Revenue", "Ventas"])
col_avg      = find_col(df, ["Average Sales", "Average", "Avg", "Promedio"])

# Si no se detectan las columnas necesarias, mostrar error con ayuda
missing = [name for name, col in [
    ("Region", col_region), ("Seller", col_seller),
    ("Units Sold", col_units), ("Total Sales", col_total)
] if col is None]

if missing:
    st.error(f"❌ Could not find these columns: **{', '.join(missing)}**")
    st.write("Columns found in your file:", list(df.columns))
    st.stop()

# ── Separador visual ─────────────────────────────────────────
st.divider()

# ============================================================
# SECCIÓN 1: Tabla con filtro por región
# ============================================================
st.header("🗂️ Data Table")

# Contenedor para el filtro y la tabla
with st.container():

    # Obtener lista única de regiones del archivo
    regions = ["All Regions"] + sorted(df[col_region].dropna().unique().tolist())

    # Selector de región (sidebar + inline)
    selected_region = st.selectbox("Filter by Region", regions)

    # Aplicar filtro: si es "All Regions" no filtra, si no, filtra el DataFrame
    if selected_region == "All Regions":
        df_filtered = df.copy()
    else:
        df_filtered = df[df[col_region] == selected_region]

    # Mostrar conteo de registros filtrados
    st.caption(f"Showing **{len(df_filtered)}** records for: {selected_region}")

    # Mostrar tabla interactiva con los datos filtrados
    st.dataframe(df_filtered, use_container_width=True, height=300)

st.divider()

# ============================================================
# SECCIÓN 2: Gráficas de métricas por región
# ============================================================
st.header("📈 Charts by Region")

# Agrupar datos por región para las gráficas
df_region = df.groupby(col_region).agg(
    Units_Sold   = (col_units, "sum"),
    Total_Sales  = (col_total, "sum"),
).reset_index()

# Agregar columna de promedio de ventas por región
if col_avg:
    df_region["Avg_Sales"] = df.groupby(col_region)[col_avg].mean().values
else:
    # Si no existe columna de promedio, calcularla como Total / Units
    df_region["Avg_Sales"] = df_region["Total_Sales"] / df_region["Units_Sold"]

# Crear tres columnas para mostrar las tres gráficas lado a lado
col1, col2, col3 = st.columns(3)

# ── Gráfica 1: Unidades vendidas por región ──────────────────
with col1:
    fig_units = px.bar(
        df_region,
        x=col_region,
        y="Units_Sold",
        title="Units Sold by Region",
        color=col_region,
        color_discrete_sequence=px.colors.qualitative.Set2,
        labels={"Units_Sold": "Units Sold", col_region: "Region"}
    )
    fig_units.update_layout(showlegend=False, height=380)
    st.plotly_chart(fig_units, use_container_width=True)

# ── Gráfica 2: Ventas totales por región ─────────────────────
with col2:
    fig_total = px.bar(
        df_region,
        x=col_region,
        y="Total_Sales",
        title="Total Sales by Region",
        color=col_region,
        color_discrete_sequence=px.colors.qualitative.Pastel,
        labels={"Total_Sales": "Total Sales ($)", col_region: "Region"}
    )
    fig_total.update_layout(showlegend=False, height=380)
    st.plotly_chart(fig_total, use_container_width=True)

# ── Gráfica 3: Promedio de ventas por región ─────────────────
with col3:
    fig_avg = px.bar(
        df_region,
        x=col_region,
        y="Avg_Sales",
        title="Average Sales by Region",
        color=col_region,
        color_discrete_sequence=px.colors.qualitative.Bold,
        labels={"Avg_Sales": "Avg Sales ($)", col_region: "Region"}
    )
    fig_avg.update_layout(showlegend=False, height=380)
    st.plotly_chart(fig_avg, use_container_width=True)

st.divider()

# ============================================================
# SECCIÓN 3: Vista detallada por vendedor
# ============================================================
st.header("👤 Seller Detail")

with st.container():

    # Lista de vendedores disponibles en el archivo
    sellers = sorted(df[col_seller].dropna().unique().tolist())

    # Selector de vendedor individual
    selected_seller = st.selectbox("Select a Seller", sellers)

    # Filtrar datos del vendedor seleccionado
    df_seller = df[df[col_seller] == selected_seller]

    # ── Métricas clave del vendedor ──────────────────────────
    # Mostrar KPIs en tarjetas usando st.metric
    m1, m2, m3 = st.columns(3)

    total_units = int(df_seller[col_units].sum())
    total_sales = df_seller[col_total].sum()
    avg_sales   = df_seller[col_avg].mean() if col_avg else (total_sales / total_units if total_units else 0)

    m1.metric("Total Units Sold", f"{total_units:,}")
    m2.metric("Total Sales",      f"${total_sales:,.2f}")
    m3.metric("Avg Sales / Transaction", f"${avg_sales:,.2f}")

    # ── Tabla del vendedor ───────────────────────────────────
    st.subheader(f"All transactions for: {selected_seller}")
    st.dataframe(df_seller, use_container_width=True, height=250)

    # ── Gráfica de barras: evolución del vendedor ────────────
    # Si existe columna de mes/fecha, muestra evolución temporal
    col_month = find_col(df, ["Month", "Date", "Fecha", "Mes", "Period"])

    if col_month and col_month in df_seller.columns:
        # Agrupar por mes para ver tendencia
        df_trend = df_seller.groupby(col_month).agg(
            Total=(col_total, "sum")
        ).reset_index()

        fig_seller = px.line(
            df_trend,
            x=col_month,
            y="Total",
            title=f"Sales Over Time — {selected_seller}",
            markers=True,
            labels={"Total": "Total Sales ($)", col_month: "Month"}
        )
        fig_seller.update_traces(line_color="#4f8ef7", line_width=2.5)
        st.plotly_chart(fig_seller, use_container_width=True)
    else:
        # Si no hay columna de fecha, mostrar gráfica de pie por región/producto
        col_group = find_col(df, ["Product", "Producto", "Category"])
        if col_group:
            df_pie = df_seller.groupby(col_group)[col_total].sum().reset_index()
            fig_pie = px.pie(
                df_pie,
                names=col_group,
                values=col_total,
                title=f"Sales by {col_group} — {selected_seller}"
            )
            st.plotly_chart(fig_pie, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────
st.divider()
st.caption("Sales Dashboard · Built with Streamlit & Plotly")
