import streamlit as st
from datetime import datetime
import json
import os

# --- 1. CONFIGURACIÓN Y ARCHIVOS (TU LÓGICA ORIGINAL) ---
DATA_FILE = "inventario_data.json"

def verificar_archivos():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f: json.dump({}, f)

def cargar_datos():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f: 
                data = json.load(f)
                return {str(k): v for k, v in data.items()}
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
    with st.container():
        user = st.text_input("Usuario (admin)")
        password = st.text_input("Contraseña (12345)", type="password")
        if st.button("ENTRAR"):
            if user == "admin" and password == "12345":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
else:
    # --- 4. MENÚ PRINCIPAL ---
    st.sidebar.title("🧔 Bigotes Valentin")
    menu = st.sidebar.radio("MENÚ", ["📦 GESTIÓN E HISTORIAL", "❓ AYUDA", "❌ SALIR"])

    if menu == "❌ SALIR":
        st.session_state.autenticado = False
        st.rerun()

    elif menu == "❓ AYUDA":
        st.info("### GUÍA RÁPIDA:\n- **NUEVO:** Registra un producto.\n- **MOVER:** Salida a profesor.\n- **REINTEGRO:** Limpia historial y devuelve stock.\n- **ELIMINAR:** Borra del archivo.")

    elif menu == "📦 GESTIÓN E HISTORIAL":
        st.title("📦 Gestión de Inventario")
        
        # BARRA DE BOTONES
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("➕ NUEVO"): st.session_state.accion = "nuevo"
        with col2:
            if st.button("🔍 BUSCAR"): st.session_state.accion = "buscar"
        with col3:
            if st.button("🚚 MOVER"): st.session_state.accion = "mover"
        with col4:
            if st.button("🔄 REINTEGRO"): st.session_state.accion = "reintegro"

        accion = st.session_state.get('accion', None)

        # FORMULARIO: NUEVO
        if accion == "nuevo":
            with st.expander("📝 NUEVO PRODUCTO", expanded=True):
                c = st.text_input("CÓDIGO")
                n = st.text_input("NOMBRE").upper()
                s = st.number_input("SIRVE", min_value=0)
                ns = st.number_input("NO SIRVE", min_value=0)
                if st.button("GUARDAR"):
                    st.session_state.inventario[c] = [n, s, ns, []]
                    guardar_todo(st.session_state.inventario)
                    st.success("Guardado correctamente")
                    st.rerun()

        # FORMULARIO: BUSCAR
        elif accion == "buscar":
            with st.expander("🔍 BUSCAR PRODUCTO", expanded=True):
                busq = st.text_input("Código a buscar")
                if st.button("BUSCAR"):
                    if busq in st.session_state.inventario:
                        d = st.session_state.inventario[busq]
                        st.info(f"Nombre: {d[0]} | Total: {d[1]+d[2]}")
                    else: st.error("No existe")

        # FORMULARIO: MOVER
        elif accion == "mover":
            if st.session_state.inventario:
                with st.expander("🚚 MOVER A PROFESOR", expanded=True):
                    c = st.selectbox("Código", list(st.session_state.inventario.keys()))
                    q = st.number_input("Cantidad", min_value=1)
                    est = st.radio("Estado", ["Sirve", "No Sirve"])
                    profe = st.text_input("Nombre del Profesor").upper()
                    if st.button("REGISTRAR"):
                        idx = 1 if est == "Sirve" else 2
                        if st.session_state.inventario[c][idx] >= q:
                            st.session_state.inventario[c][idx] -= q
                            f = datetime.now().strftime("%d/%m %H:%M")
                            st.session_state.inventario[c][3].append([f, c, q, est, profe])
                            guardar_todo(st.session_state.inventario)
                            st.success("Movimiento registrado")
                            st.rerun()
                        else: st.error("Sin stock suficiente")
            else: st.warning("No hay productos")

        # FORMULARIO: REINTEGRO
        elif accion == "reintegro":
            if st.session_state.inventario:
                with st.expander("🔄 REINTEGRO", expanded=True):
                    c = st.selectbox("Código para reintegro", list(st.session_state.inventario.keys()))
                    q = st.number_input("Cantidad a devolver", min_value=1)
                    est = st.radio("Tipo", ["Sirve", "No Sirve"])
                    if st.button("REINTEGRAR"):
                        idx = 1 if est == "Sirve" else 2
                        st.session_state.inventario[c][idx] += q
                        st.session_state.inventario[c][3] = [] 
                        guardar_todo(st.session_state.inventario)
                        st.success("Stock recuperado")
                        st.rerun()

        # --- TABLAS DE DATOS ---
        st.markdown("---")
        st.subheader("📊 Registro Actual")
        if st.session_state.inventario:
            datos_tabla = []
            for cod, d in st.session_state.inventario.items():
                datos_tabla.append({"Código": cod, "Nombre": d[0], "Sirve": d[1], "No Sirve": d[2], "Total": d[1]+d[2]})
            st.table(datos_tabla)

            cod_del = st.selectbox("Eliminar Producto (Permanente)", [""] + list(st.session_state.inventario.keys()))
            if st.button("🗑️ ELIMINAR SELECCIONADO"):
                if cod_del:
                    del st.session_state.inventario[cod_del]
                    guardar_todo(st.session_state.inventario)
                    st.rerun()

        st.subheader("📜 Historial")
        historial = []
        for cod, d in st.session_state.inventario.items():
            for h in d[3]: historial.append({"Fecha": h[0], "Cod": h[1], "Cant": h[2], "E": h[3], "Profe": h[4]})
        if historial: st.dataframe(historial)
        else: st.write("Historial vacío")
    
