import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client, Client
from datetime import datetime

# Configuración de página responsive con estilo oscuro premium (estilo image_05044a.png)
st.set_page_config(page_title="PWM Personal Dashboard", layout="wide", initial_sidebar_state="collapsed")

# Inicialización de conexión a Supabase (Reemplaza con tus credenciales secretas)
# En producción o Streamlit Cloud, usa st.secrets
SUPABASE_URL = "TU_SUPABASE_URL"
SUPABASE_KEY = "TU_SUPABASE_ANON_KEY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- CARGA DE DATOS ---
def load_data():
    tx_query = supabase.table("transactions").select("*").order("date", desc=True).execute()
    acc_query = supabase.table("accounts").select("*").execute()
    return pd.DataFrame(tx_query.data), pd.DataFrame(acc_query.data)

df_tx, df_acc = load_data()

# --- HEADER GENERAL (Estilo PWM Instrument) ---
st.markdown("<h2 style='color:#00b37e; margin-bottom:0;'>PWM Personal Instrument</h2>", unsafe_scale=True)
st.caption(f"Fictional-style Private Financial Ledger | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# --- CÁLCULO DE MÉTRICAS CLAVE ---
assets = df_acc[df_acc['type'] == 'Asset']['balance'].sum() if not df_acc.empty else 0
liabilities = df_acc[df_acc['type'] == 'Liability']['balance'].sum() if not df_acc.empty else 0
net_worth = assets - liabilities

# --- SECCIÓN 1: KPI PRINCIPALES Y TOTALES (Fiel a image_05044a.png) ---
col_main, col_widgets = st.columns([2, 1])

with col_main:
    # Contenedor Oscuro de Net Worth
    st.markdown(
        f"""
        <div style='background-color:#1c1c1e; padding:30px; border-radius:12px; border: 1px solid #2c2c2e;'>
            <p style='color:#8e8e93; font-size:0.9rem; text-transform:uppercase; margin:0;'>Net Worth Consolidado</p>
            <h1 style='color:#ffffff; font-size:3.5rem; margin:10px 0;'>${net_worth:,.2f} COP</h1>
            <p style='color:#00b37e; font-size:0.9rem; margin:0;'>● Activos Líquidos: ${assets:,.2f} | 🚩 Deudas Activas: ${liabilities:,.2f}</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

with col_widgets:
    st.metric(label="Millas Estimadas Acumuladas BBVA (Este mes)", value="2,450 mi", delta="+120 mi por consumos")
    st.info("💡 Consejo: Pagar almuerzos y deseos a 1 cuota con la BBVA para optimizar el viaje familiar sin generar intereses.")

# --- SECCIÓN 2: REGISTRO DE TRANSACCIONES EN TIEMPO REAL (Mobile Friendly) ---
st.markdown("### 📝 Registrar Movimiento / Antojo Financiero")
with st.expander("➕ Añadir Gasto o Ingreso al Instante (Funciona en tu Celular)"):
    with st.form("tx_form", clear_on_submit=True):
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            desc = st.text_input("Descripción (Ej: Almuerzo Ejecutivo, Pago ETB)")
            amount = st.number_input("Monto en COP", min_value=0.0, step=1000.0)
        with col_f2:
            category = st.selectbox("Categoría Contable", ["Necesidad", "Deseo", "Ahorro", "Ingreso"])
            method = st.selectbox("Método de Pago / Cuenta afectada", df_acc['name'].tolist())
        with col_f3:
            date_sel = st.date_input("Fecha", datetime.today())
            submit = st.form_submit_button("Ejecutar Transacción y Actualizar Balance")
            
        if submit and desc and amount > 0:
            month_str = date_sel.strftime('%Y-%m')
            # 1. Insertar la transacción histórica
            supabase.table("transactions").insert({
                "date": str(date_sel), "month_year": month_str, "description": desc,
                "amount": amount, "category": category, "payment_method": method
            }).execute()
            
            # 2. Actualizar el saldo contable de la cuenta/tarjeta en tiempo real
            current_balance = df_acc[df_acc['name'] == method]['balance'].values[0]
            acc_type = df_acc[df_acc['name'] == method]['type'].values[0]
            
            # Si es pasivo (tarjeta de crédito), el gasto aumenta la deuda. Si es activo, disminuye el saldo.
            new_balance = current_balance + amount if acc_type == 'Liability' else current_balance - amount
            if category == "Ingreso":
                new_balance = current_balance - amount if acc_type == 'Liability' else current_balance + amount
                
            supabase.table("accounts").update({"balance": new_balance}).eq("name", method).execute()
            st.success("Transacción registrada con éxito. ¡Refrescando Dashboards!")
            st.rerun()

# --- SECCIÓN 3: DASHBOARDS Y CHARTS VISUALES (Estilo Multi-Sección) ---
st.markdown("### 📊 Gráficos Analíticos de Rendimiento")
tab1, tab2, tab3 = st.tabs(["Distribución de Gastos", "Evolución Mensual", "Estado de Cuentas"])

with tab1:
    if not df_tx.empty and df_tx[df_tx['category'] != 'Ingreso'].shape[0] > 0:
        df_expenses = df_tx[df_tx['category'] != 'Ingreso']
        fig_pie = px.pie(df_expenses, values='amount', names='category', 
                         title='Gastos por Categoría (Contabilidad Mental)',
                         color_discrete_sequence=['#f75a68', '#4ea8de', '#00b37e'])
        fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No hay gastos registrados este mes para generar el gráfico.")

with tab2:
    if not df_tx.empty:
        df_trend = df_tx.groupby(['month_year', 'category']).sum().reset_index()
        fig_trend = px.bar(df_trend, x='month_year', y='amount', color='category', 
                           title='Flujo de Caja Histórico por Mes', barmode='group')
        fig_trend.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_trend, use_container_width=True)

with tab3:
    # Tabla de posiciones e instrumentos financieros basada en image_05044a.png
    st.markdown("#### Saldos Consolidados en Cuentas y Tarjetas")
    if not df_acc.empty:
        st.dataframe(df_acc[['name', 'type', 'balance']].style.format({"balance": "${:,.2f}"}), use_container_width=True)