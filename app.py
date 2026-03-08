app.py
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Mi Negocio - Contabilidad", layout="centered")

# --- CONEXIÓN BASE DE DATOS ---
conn = sqlite3.connect('contabilidad_pro.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS movimientos 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, tipo TEXT, categoria TEXT, monto REAL)''')
conn.commit()

# --- TÍTULO Y ESTILO ---
st.title("📊 Control de Finanzas")
st.markdown("---")

# --- FORMULARIO DE REGISTRO ---
with st.expander("➕ Registrar Nuevo Movimiento", expanded=True):
    tipo = st.radio("Tipo de movimiento", ["Ingreso", "Gasto"], horizontal=True)
    col1, col2 = st.columns(2)
    
    with col1:
        monto = st.number_input("Monto ($)", min_value=0.0, step=1.0)
    with col2:
        if tipo == "Ingreso":
            cat = st.selectbox("Categoría", ["Venta Directa", "Servicios", "Otros"])
        else:
            cat = st.selectbox("Categoría", ["Insumos", "Renta", "Servicios", "Sueldos", "Otros"])
            
    if st.button("Guardar Registro"):
        fecha_actual = datetime.now().strftime("%d-%m-%Y")
        c.execute("INSERT INTO movimientos (fecha, tipo, categoria, monto) VALUES (?, ?, ?, ?)", 
                  (fecha_actual, tipo, cat, monto))
        conn.commit()
        st.success(f"¡{tipo} registrado correctamente!")

# --- VISUALIZACIÓN DE DATOS ---
st.markdown("### Resumen Actual")
df = pd.read_sql_query("SELECT * FROM movimientos", conn)

if not df.empty:
    # Cálculos rápidos
    ingresos = df[df['tipo'] == 'Ingreso']['monto'].sum()
    gastos = df[df['tipo'] == 'Gasto']['monto'].sum()
    balance = ingresos - gastos
    
    # Métricas visuales
    m1, m2, m3 = st.columns(3)
    m1.metric("Ingresos", f"${ingresos:,.2f}")
    m2.metric("Gastos", f"-${gastos:,.2f}", delta_color="inverse")
    m3.metric("Balance", f"${balance:,.2f}")

    # Gráfico de gastos (Solo si hay gastos)
    if gastos > 0:
        st.markdown("#### Distribución de Gastos")
        df_gastos = df[df['tipo'] == 'Gasto'].groupby('categoria')['monto'].sum()
        st.bar_chart(df_gastos)

    # Tabla de historial
    st.markdown("#### Historial de Movimientos")
    st.dataframe(df.sort_values(by='id', ascending=False), use_container_width=True)
else:
    st.info("Aún no hay datos. ¡Registra tu primer movimiento arriba!")

# Cerrar conexión al finalizar
conn.close()
