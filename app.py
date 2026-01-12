import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text

# Configuración de página y estilos
st.set_page_config(page_title="BankGuard Monitor V2", page_icon="🛡️", layout="wide")

# Inyectamos CSS personalizado (esto da estilos avanzados)
st.markdown("""
    <style>
    .titulo-sombra {
        font-size: 3em;
        color: #FFFFFF;
        text-shadow: 2px 2px 4px #000000;
        font-weight: bold;
        text-align: center;
    }
    .stMetricLabel {font-size: 1.1em; font-weight: bold;}
    </style>
    """, unsafe_allow_html=True)

# Conexión a la base de datos
SERVER = 'LOCALHOST'
DATABASE = 'BankGuard'
CONNECTION_STRING = F"mssql+pyodbc://{SERVER}/{DATABASE}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"

@st.cache_resource
def getEngine():
    return create_engine(CONNECTION_STRING)

engine = getEngine()

# Título
c_logo, c_title = st.columns([1, 6])
with c_logo:
    st.markdown("# 🦈🛡️")
with c_title:
    st.title("BankGuard Security Center")
    st.markdown("Monitoreo de fraudes transaccionales en tiempo real")

st.divider()

# Sidebar
st.sidebar.header("Filtros de Seguridad")
tipo_filtro = st.sidebar.multiselect("Tipo de Operación", ["COMPRA", "TRANSFERENCIA", "RETIRO", "PAGO_SERVICIO"])

# Botón para refrescar
if st.sidebar.button("Actualizar Datos"):
    st.cache_data.clear()

# Lógica de datos
def cargar_datos():
    with engine.connect() as conn:
        # Transacciones Generales
        dataframe_transaccion = pd.read_sql(text("SELECT TOP 500 * FROM Transacciones ORDER BY fecha_hora DESC"), conn)
        
        # Razones de auditoría de fraudes
        try:
            dataframe_audit = pd.read_sql(text("SELECT TOP 100 * FROM Auditoria_Fraude ORDER BY fecha_auditoria DESC"), conn)
        except:
            dataframe_audit = pd.DataFrame() # Si no existe la tabla, DataFrame vacío
            
    return dataframe_transaccion, dataframe_audit

df, df_audit = cargar_datos()

# Aplicar filtros
if tipo_filtro:
    df = df[df['tipo_operacion'].isin(tipo_filtro)]

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Transacciones Totales", len(df))
col2.metric("Fraudes Detectados", len(df[df['estado'] == 'RECHAZADA']))
col3.metric("Monto Bloqueado", f"${df[df['estado'] == 'RECHAZADA']['monto'].sum():,.0f}")

# Calcular % de Fraude
tasa_fraude = (len(df[df['estado'] == 'RECHAZADA']) / len(df) * 100) if len(df) > 0 else 0
col4.metric("Tasa de Riesgo", f"{tasa_fraude:.1f}%")

st.divider()

# Sección 1: Análisis de Fraudes
if not df_audit.empty:
    st.subheader("Análisis de Amenazas Detectadas")
    c_audit1, c_audit2 = st.columns((2, 1))
    
    with c_audit1:
        # Tabla de Auditoría
        st.dataframe(
            df_audit[['transaccion_id', 'regla_activada', 'detalle', 'fecha_auditoria']],
            width = 'stretch',
            hide_index = True
        )
        
    with c_audit2:
        # Gráfico: Monto VS Velocidad
        fig_audit = px.bar(
            df_audit, 
            x = 'regla_activada', 
            title = "Amenazas por Tipo",
            color = 'regla_activada',
            color_discrete_map = {"MONTO_ALTO": "#FF4B4B", "VELOCIDAD_ALTA": "#FFA500"}
        )
        st.plotly_chart(fig_audit, width = 'stretch')
else:
    st.info("No hay registros en la auditoría de fraudes aún.")

# Sección 2: Transacciones en tiempo real
st.subheader("Transacciones en Tiempo Real")

if not df.empty:
    # Gráfico Scatter (Monto vs Tiempo)
    fig = px.scatter(
        df, 
        x = "transaccion_id", 
        y = "monto", 
        color = "estado",
        size = "monto",
        color_discrete_map = {"APROBADA": "#00CC96", "RECHAZADA": "#EF553B", "PENDIENTE": "#636EFA"},
        title = "Dispersión de Transacciones (Monto vs ID)"
    )
    st.plotly_chart(fig, width = 'stretch')

    # Últimas transacciones
    st.dataframe(df.head(10), width = 'stretch', hide_index = True)
else:
    st.warning("Esperando datos")