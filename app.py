import streamlit as st
import pandas as pd
import pyodbc
import plotly.express as px

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
CONN_STRING = (
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=LOCALHOST;"
    r"DATABASE=BankGuard;"
    r"Trusted_Connection=yes;"
)

# Usamos @st.cache_data para que no recargue la base de datos a cada click si los datos no cambiaron
@st.cache_data 
def cargar_datos():
    conn = pyodbc.connect(CONN_STRING)
    query = "SELECT * FROM Transacciones"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Inicio de la app
try:
    # Cargamos los datos crudos
    df_raw = cargar_datos()

    # Barra lateral (sidebar) - Panel de control
    with st.sidebar:
        st.header("🛠️ Panel de Control")
        st.markdown("---")
        st.write("Usa estos filtros para segmentar la información del dashboard.")

        # Filtro 1 - Despegable múltiple por tipo de operación
        # Obtenemos los tipos únicos de la DB
        tipos_disponibles = df_raw['tipo_operacion'].unique()
        # Creamos el widget de selección múltiple
        tipos_seleccionados = st.multiselect(
            "Filtrar por Tipo de Operación:",
            options = tipos_disponibles,
            default = tipos_disponibles, # Por defecto marcan todos
            help = "Seleccioná uno o más tipos para ver en los gráficos."
        )

        # Filtro 2 - Checkbox simple
        mostrar_solo_fraudes = st.checkbox("🚨 Ver SOLO Fraudes confirmados")
        
        st.markdown("---")
        st.info("ℹ️ Dashboard conectado a SQL Server local.")

    # Lógica de filtrado
    # Creamos una copia para no modificar los datos originales
    df_filtrado = df_raw.copy()

    # 1. Aplicamos Filtro de Tipo (Si el usuario desmarcó algo)
    if tipos_seleccionados:
        df_filtrado = df_filtrado[df_filtrado['tipo_operacion'].isin(tipos_seleccionados)]

    # 2. Aplicamos Filtro de Solo Fraudes (Si marcó el checkbox)
    if mostrar_solo_fraudes:
        df_filtrado = df_filtrado[df_filtrado['estado'] == 'RECHAZADA']

    # Título con sombra usando el CSS que definimos arriba
    st.markdown('<p class="titulo-sombra">🛡️ BankGuard: Monitor de Fraude V2</p>', unsafe_allow_html=True)
    st.markdown("---")

    # Usamos los datos filtrados para todo lo demás
    
    # Cálculos de KPIs en base a lo filtrado
    transacciones_totales = len(df_filtrado)
    fraudes = df_filtrado[df_filtrado['estado'] == 'RECHAZADA']
    aprobadas = df_filtrado[df_filtrado['estado'] == 'APROBADA']
    
    porcentaje_fraude = (len(fraudes) / transacciones_totales) * 100 if transacciones_totales > 0 else 0

    # Fila 1 - Métricas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Transacciones Visibles", transacciones_totales, help="Total según filtros aplicados")
    col2.metric("✅ Aprobadas", len(aprobadas))
    col3.metric("🚨 Fraudes Detectados", len(fraudes), delta_color="inverse")

    # Usamos un color condicional para la tasa
    col4.metric("Tasa de Fraude (Filtrada)", f"{porcentaje_fraude:.2f}%", 
                delta=f"{porcentaje_fraude:.1f}%" if porcentaje_fraude > 5 else None,
                delta_color="inverse")
    st.markdown("---")

    # Fila 2 - Gráficos
    if transacciones_totales > 0:
        c1, c2 = st.columns((2, 1))

        with c1:
            st.subheader(f"Tendencia ({', '.join(tipos_seleccionados) if tipos_seleccionados else 'Todo'})")
            fig_scatter = px.scatter(
                df_filtrado, # Usamos el DF filtrado
                x="transaccion_id", y="monto", color="estado", size="monto",
                color_discrete_map={"APROBADA": "green", "RECHAZADA": "red", "PENDIENTE": "gray"},
                hover_data=['tipo_operacion', 'ip_origen'] # Más info al pasar el mouse
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

        with c2:
            st.subheader("Distribución")
            fig_pie = px.pie(
                df_filtrado, # Usamos el DF filtrado
                names="estado", color="estado",
                color_discrete_map={"APROBADA": "green", "RECHAZADA": "red", "PENDIENTE": "gray"},
                hole=0.4
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        # Fila 3 - Tabla Detalle
        st.subheader("Detalle de Transacciones (Según Filtros)")

        # Mostramos las últimas 15 del filtro actual
        st.dataframe(
            df_filtrado.sort_values(by='transaccion_id', ascending=False).head(15),
            use_container_width=True,
            hide_index=True # Ocultamos el índice numérico feo de pandas
        )
    else:
        st.warning("No hay datos que coincidan con los filtros seleccionados.")

except Exception as e:
    st.error(f"Error de Sistema: {e}")
    st.exception(e)