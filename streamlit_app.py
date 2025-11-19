import streamlit as st
import pandas as pd
import gspread

# --- DICCIONARIO DE COLORES ---
# Añade aquí todos tus equipos con su código de color (Hex)
COLORES_EQUIPOS = {
    "FC Bayern Munich": "#FF0000", # Rojo ejemplo
    # Si un equipo no está aquí, saldrá Dorado por defecto
}

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="ToNOI - Resultados",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .stApp { background-color: #f0f2f6; }
    .champion-card {
        background-color: #FFD700;
        padding: 20px;
        border-radius: 10px;
        color: black;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .match-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .leyenda-container {
        background-color: #e8f4f8;
        border: 1px solid #d1e7dd;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
        color: #0f5132;
        font-size: 0.9rem;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN Y CACHÉ ---
@st.cache_data(ttl=60)
def cargar_datos_gsheets(nombre_hoja):
    try:
        creds = st.secrets["gcp_creds"]
        gc = gspread.service_account_from_dict(creds)
        ID_HOJA = "18x6wCv0E7FOpuvwZpWYRSFi56E-_RR2Gm1deHyCLo2Y"
        sh = gc.open_by_key(ID_HOJA).worksheet(nombre_hoja)
        return sh.get_all_records()
    except Exception as e:
        return []

# --- LÓGICA DE AYUDA ---
def obtener_campeon_actual(historial):
    if not historial: return "Vacante"
    portador = None
    for partido in historial:
        ganador = partido.get('Equipo Ganador')
        perdedor = partido.get('Equipo Perdedor')
        resultado = partido.get('Resultado')
        
        if not portador:
            portador = ganador
        else:
            if portador == ganador or portador == perdedor:
                aspirante = ganador if perdedor == portador else perdedor
                if resultado == "Victoria" and ganador == aspirante:
                    portador = aspirante
    return portador

# --- PÁGINAS ---

def pagina_inicio():
    st.title("⚽ ToNOI - Panel Central")
    
    historial = cargar_datos_gsheets("HistorialPartidos")
    if not historial: st.info("El torneo aún no ha comenzado."); return

    # 1. TARJETA DEL CAMPEÓN (Dinámica)
    campeon = obtener_campeon_actual(historial)
    
    # Buscamos el color en el diccionario. Si no existe, usa Dorado (#FFD700)
    color_fondo = COLORES_EQUIPOS.get(campeon, "#FFD700")
    
    # Lógica simple para el texto: Si el fondo es negro/oscuro, pon letras blancas.
    # Si usas colores muy claros, cambia 'white' por 'black' manualmente aquí.
    color_texto = "white" if color_fondo in ["#000000", "#0000FF", "#DarkRed"] else "black"

    st.markdown(f"""
    <div class="champion-card" style="background-color: {color_fondo}; color: {color_texto};">
        <div style="font-size: 1.2rem; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9;">🏆 Campeón Actual 🏆</div>
        <div style="font-size: 3.5rem; font-weight: 800; margin: 10px 0;">{campeon}</div>
        <div style="font-size: 1rem; opacity: 0.9;">Defendiendo el título actualmente</div>
    </div>
    """, unsafe_allow_html=True)

    # 2. ÚLTIMO PARTIDO (Esto sigue igual)
    ultimo = historial[-1]
    res_manual = f"({ultimo['ResultadoManual']})" if ultimo.get('ResultadoManual') else ""
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown(f"""
        <div class="match-card">
            <div style="color: #666; font-size: 0.8rem; margin-bottom: 5px;">📢 ÚLTIMO RESULTADO ({ultimo['Fecha']})</div>
            <div style="font-size: 1.5rem; font-weight: bold;">
                {ultimo['Equipo Ganador']} <span style='color:#ff4b4b'>vs</span> {ultimo['Equipo Perdedor']}
            </div>
            <div style="font-size: 1.2rem; margin-top: 5px;">
                Resultado: <b>{ultimo['Resultado']}</b> {res_manual}
            </div>
        </div>
        """, unsafe_allow_html=True)

def pagina_clasificacion():
    st.title("📊 Clasificación Oficial")
    
    data = cargar_datos_gsheets("Hoja1")
    if not data: st.warning("No hay datos disponibles."); return
    
    df = pd.DataFrame(data)
    
    # 1. RENOMBRADO PREVIO (Para poder calcular con nombres cortos)
    cols_map = {
        "T": "PJ", "Partidos con Trofeo": "PcT", "Mejor Racha": "MR",
        "Destronamientos": "Des", "Intentos": "I"
        # Nota: No renombramos PPP ni ID porque los vamos a recalcular de cero
    }
    df = df.rename(columns=cols_map)

    # 2. RECÁLCULO DE EMERGENCIA (Fix números gigantes)
    # Convertimos a numérico por seguridad
    for col in ['P', 'PJ', 'Des', 'I']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Calculamos PPP (Puntos / Partidos Jugados)
    df['PPP'] = df.apply(lambda x: x['P'] / x['PJ'] if x['PJ'] > 0 else 0.0, axis=1)

    # Calculamos ID (Destronamientos / Intentos)
    df['ID'] = df.apply(lambda x: (x['Des'] / x['I']) * 100 if x['I'] > 0 else 0.0, axis=1)

    # 3. FORMATO VISUAL
    historial = cargar_datos_gsheets("HistorialPartidos")
    campeon = obtener_campeon_actual(historial)

    if "P" in df.columns:
        df = df.sort_values(by="P", ascending=False).reset_index(drop=True)
    
    df.insert(0, 'Pos.', range(1, len(df) + 1))
    
    if "Equipo" in df.columns:
        df['Equipo'] = df.apply(lambda row: f"{row['Equipo']} 👑" if row['Equipo'] == campeon else row['Equipo'], axis=1)
    
    # Formatear los decimales correctamente ahora que los datos son buenos
    df['PPP'] = df['PPP'].map('{:,.2f}'.format)
    df['ID'] = df['ID'].map('{:,.2f}%'.format)

    # 4. ORDEN FINAL DE COLUMNAS
    orden_cols = ["Pos.", "Equipo", "PJ", "V", "E", "D", "P", "GF", "GC", "DG", "PPP", "PcT", "MR", "Des", "I", "ID"]
    cols_finales = [c for c in orden_cols if c in df.columns]
    
    # --- LEYENDA COMPLETA ---
    st.markdown("""
    <div class="leyenda-container">
        <div style="font-weight: bold; margin-bottom: 5px;">📖 GLOSARIO DE DATOS:</div>
        • <b>PJ:</b> Partidos Jugados &nbsp;|&nbsp; <b>V/E/D:</b> Victorias / Empates / Derrotas<br>
        • <b>P:</b> Puntos Totales &nbsp;|&nbsp; <b>PPP:</b> Promedio de Puntos por Partido<br>
        • <b>GF/GC/DG:</b> Goles a Favor / En Contra / Diferencia de Goles<br>
        • 🏆 <b>PcT:</b> Partidos defendiendo el Trofeo &nbsp;|&nbsp; <b>Des:</b> Títulos ganados al campeón<br>
        • <b>ID (% Éxito):</b> Porcentaje de veces que ganó el título cuando tuvo la oportunidad (Des/I).
    </div>
    """, unsafe_allow_html=True)
    
    st.dataframe(df[cols_finales], hide_index=True, use_container_width=True)

def pagina_estadisticas():
    st.title("⭐ Salón de la Fama")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👟 Goleadores (G+A)")
        goles = cargar_datos_gsheets("ClasificacionGoleadores")
        if goles:
            df_g = pd.DataFrame(goles).sort_values(by="G/A", ascending=False)
            st.dataframe(df_g, hide_index=True, use_container_width=True)
        else:
            st.caption("Sin datos.")

    with col2:
        st.subheader("🧤 Porterías a Cero")
        porteros = cargar_datos_gsheets("ClasificacionPorteros")
        if porteros:
            df_p = pd.DataFrame(porteros).sort_values(by="Porterías a 0", ascending=False)
            st.dataframe(df_p, hide_index=True, use_container_width=True)
        else:
            st.caption("Sin datos.")

def pagina_historial():
    st.title("📜 Historial Completo")
    historial = cargar_datos_gsheets("HistorialPartidos")
    if not historial: st.warning("No hay partidos."); return
    
    df = pd.DataFrame(historial)
    cols = [c for c in ["Fecha", "Equipo Ganador", "Resultado", "Equipo Perdedor", "ResultadoManual"] if c in df.columns]
    st.dataframe(df[cols].iloc[::-1], hide_index=True, use_container_width=True)

# --- MENÚ ---
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Inicio", "📊 Clasificación", "⭐ Estadísticas", "📜 Historial"])

with tab1: pagina_inicio()
with tab2: pagina_clasificacion()
with tab3: pagina_estadisticas()
with tab4: pagina_historial()

st.markdown("---")
st.caption("🔄 Los datos se actualizan automáticamente cada minuto.")