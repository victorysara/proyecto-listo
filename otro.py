import streamlit as st
from datetime import datetime
import json
import os
import pandas as pd

# --- 1. CONFIGURACIÓN DE ARCHIVOS ---
DATA_FILE = "inventario_data.json"

def verificar_archivos():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f: json.dump({}, f)

def cargar_datos():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f: 
                return json.load(f)
    except: return {}
    return {}

def guardar_todo(inventario):
    with open(DATA_FILE, "w") as f:
        json.dump(inventario, f, indent=4)

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Bigotes Valentin", page_icon="🧔", layout="wide")
verificar_archivos()

if 'inventario' not in st.session_state:
    st.session_state.inventario = cargar_datos()

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# --- 3. LOGIN ---
if not st.session_state.autenticado:
    st.title("🧔 BIENVENIDO A BIGOTES VALENTIN")
    col_l, col_r = st.columns(2)
    with col_l:
        user = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if st.button("ENTRAR"):
            if user == "admin" and password == "12345":
                st.session_state.autenticado = True
                st.rerun()
            else: st.error("Credenciales incorrectas")
else:
    # --- 4. PANEL PRINCIPAL ---
    st.title("🧔 Sistema Bigotes Valentin - Panel de Control")
    
    # MÉTRICAS RÁPIDAS (Resumen arriba)
    total_prods = len(st.session_state.inventario)
    total_movs = sum(len(d[3]) for d in st.session_state.inventario.values())
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Productos Registrados", total_prods)
    c2.metric("Movimientos Totales", total_movs)
    c3.write("📅 Fecha actual: " + datetime.now().strftime("%d/%m/%Y"))

    st.divider()

    # --- SECCIÓN DE ACCIONES ---
    with st.sidebar:
        st.header("⚙️ Operaciones")
        opcion = st.radio("Selecciona una tarea:", ["Ver Inventario", "Registrar Nuevo", "Mover a Profesor", "Reintegro/Limpiar"])
        if st.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()

    # --- PANTALLA: VER INVENTARIO e HISTORIAL (La que pediste) ---
    if opcion == "Ver Inventario":
        st.subheader("📦 Registro de Productos e Historial")
        
        # BUSCADOR
        busqueda = st.text_input("🔍 Buscar por código o nombre:").upper()

        # Preparar datos para las tablas
        datos_reg = []
        datos_his = []
        for cod, d in st.session_state.inventario.items():
            # Filtrar para la tabla de registros
            if busqueda in str(cod).upper() or busqueda in str(d[0]).upper():
                datos_reg.append({
                    "Código": cod, "Nombre": d[0], "Sirve": d[1], 
                    "No Sirve": d[2], "Total": d[1]+d[2]
                })
                # Llenar historial
                for h in d[3]:
                    datos_his.append({
                        "Fecha": h[0], "Código": h[1], "Cant.": h[2], 
                        "Estado": h[3], "Profesor": h[4]
                    })

        # Mostrar Tabla de Registros
        st.write("### 🗃️ Inventario Actual")
        if datos_reg:
            df_reg = pd.DataFrame(datos_reg)
            st.dataframe(df_reg, use_container_width=True, hide_index=True)
        else: st.info("No hay productos que coincidan.")

        # Mostrar Tabla de Historial
        st.write("### 📜 Historial de Movimientos")
        if datos_his:
            df_his = pd.DataFrame(datos_his)
            st.dataframe(df_his, use_container_width=True, hide_index=True)
        else: st.info("No hay movimientos registrados.")

    # --- PANTALLA: NUEVO ---
    elif opcion == "Registrar Nuevo":
        st.subheader("📝 Agregar Nuevo Producto")
        with st.form("form_nuevo"):
            c = st.text_input("Código")
            n = st.text_input("Nombre").upper()
            s = st.number_input("Cantidad Sirve", min_value=0)
            ns = st.number_input("Cantidad No Sirve", min_value=0)
            if st.form_submit_button("Guardar Producto"):
                if c:
                    st.session_state.inventario[c] = [n, s, ns, []]
                    guardar_todo(st.session_state.inventario)
                    st.success(f"Producto {c} guardado correctamente.")
                    st.balloons()
                else: st.error("El código es obligatorio.")

    # --- PANTALLA: MOVER ---
    elif opcion == "Mover a Profesor":
        st.subheader("🚚 Registro de Salida")
        if st.session_state.inventario:
            c = st.selectbox("Selecciona el Código", list(st.session_state.inventario.keys()))
            q = st.number_input("Cantidad a entregar", min_value=1)
            est = st.radio("Estado de la pieza", ["Sirve", "No Sirve"])
            profe = st.text_input("Nombre del Profesor").upper()
            if st.button("Registrar Salida"):
                idx = 1 if est == "Sirve" else 2
                if st.session_state.inventario[c][idx] >= q:
                    st.session_state.inventario[c][idx] -= q
                    f = datetime.now().strftime("%d/%m %H:%M")
                    st.session_state.inventario[c][3].append([f, c, q, est, profe])
                    guardar_todo(st.session_state.inventario)
                    st.success("Movimiento registrado con éxito.")
                else: st.error("Stock insuficiente en esa categoría.")
        else: st.warning("Primero debes registrar productos.")

    # --- PANTALLA: REINTEGRO ---
    elif opcion == "Reintegro/Limpiar":
        st.subheader("🔄 Reintegro y Limpieza")
        c = st.selectbox("Selecciona Código", list(st.session_state.inventario.keys()))
        q = st.number_input("Cantidad a reintegrar", min_value=1)
        est = st.radio("Tipo de Reintegro", ["Sirve", "No Sirve"])
        col_r1, col_r2 = st.columns(2)
        if col_r1.button("REINTEGRAR"):
            idx = 1 if est == "Sirve" else 2
            st.session_state.inventario[c][idx] += q
            st.session_state.inventario[c][3] = [] # Limpia historial
            guardar_todo(st.session_state.inventario)
            st.success("Reintegro procesado e historial limpio.")
        
        if col_r2.button("⚠️ ELIMINAR PRODUCTO"):
            del st.session_state.inventario[c]
            guardar_todo(st.session_state.inventario)
            st.warning("Producto eliminado permanentemente.")
            st.rerun()
