import streamlit as st
import pandas as pd
import gspread
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="ToNOI - Resultados",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
<style>
    .stApp { background-color: #f0f2f6; }
    .big-font { font-size: 24px !important; font-weight: bold; }
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
    .leyenda-box {
        background-color: #e8f4f8;
        border: 1px solid #d1e7dd;
        padding: 10px;
        border-radius: 5px;
        font-size: 0.9rem;
        margin-bottom: 15px;
        color: #0f5132;
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

def limpiar_numero(valor):
    """Convierte cualquier formato numérico raro (con comas o puntos) a float seguro"""
    if valor == "" or valor is None: return 0.0
    try:
        # Si ya es un número, devolverlo
        if isinstance(valor, (int, float)): return float(valor)
        # Si es string, reemplazar coma por punto (formato ES -> US) y convertir
        valor_str = str(valor).replace(',', '.')
        return float(valor_str)
    except:
        return 0.0

# --- PÁGINAS ---

def pagina_inicio():
    st.title("⚽ ToNOI - Panel Central")
    
    historial = cargar_datos_gsheets("HistorialPartidos")
    if not historial: st.info("El torneo aún no ha comenzado."); return

    # 1. TARJETA DEL CAMPEÓN (Texto corregido)
    campeon = obtener_campeon_actual(historial)
    st.markdown(f"""
    <div class="champion-card">
        <div style="font-size: 1.2rem;">👑 CAMPEÓN ACTUAL 👑</div>
        <div style="font-size: 3rem; font-weight: 800; margin: 10px 0;">{campeon}</div>
        <div style="font-size: 0.9rem;">Defendiendo el título actualmente</div>
    </div>
    """, unsafe_allow_html=True)

    # 2. ÚLTIMO PARTIDO
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
    
    historial = cargar_datos_gsheets("HistorialPartidos")
    campeon = obtener_campeon_actual(historial)
    
    # Ordenar y Añadir Posición
    if "P" in df.columns:
        df = df.sort_values(by="P", ascending=False).reset_index(drop=True)
    df.insert(0, 'Pos.', range(1, len(df) + 1))
    
    # Marcar Campeón
    if "Equipo" in df.columns:
        df['Equipo'] = df.apply(lambda row: f"{row['Equipo']} 👑" if row['Equipo'] == campeon else row['Equipo'], axis=1)
    
    # --- CORRECCIÓN DE DECIMALES ---
    # Limpiamos primero los datos usando la función auxiliar para evitar el error de 1.000.000%
    if "PPM" in df.columns:
        df['PPM'] = df['PPM'].apply(limpiar_numero).map('{:,.2f}'.format)
    
    if "Indice Destronamiento" in df.columns:
        df['Indice Destronamiento'] = df['Indice Destronamiento'].apply(limpiar_numero).map('{:,.2f}%'.format)

    # Renombrar
    cols_map = {
        "T": "PJ", "Partidos con Trofeo": "PcT", "Mejor Racha": "MR",
        "Destronamientos": "Des", "Intentos": "I", "Indice Destronamiento": "ID"
    }
    df = df.rename(columns=cols_map)
    
    # Orden
    orden_cols = ["Pos.", "Equipo", "PJ", "V", "E", "D", "P", "GF", "GC", "DG", "PPP", "PcT", "MR", "Des", "I", "ID"]
    cols_finales = [c for c in orden_cols if c in df.columns]
    
    # --- LEYENDA CORREGIDA ---
    # Usamos HTML puro para asegurar que se ve todo y no se corta
    st.markdown("""
    <div class="leyenda-box">
        <b>GLOSARIO:</b> <br>
        <b>PJ:</b> Partidos Jugados | <b>V/E/D:</b> Victorias/Empates/Derrotas | <b>P:</b> Puntos | <b>PPP:</b> Puntos por Partido <br>
        <b>GF/GC/DG:</b> Goles Favor / Contra / Diferencia <br>
        🏆 <b>PcT:</b> Partidos con Trofeo | <b>Des:</b> Títulos Ganados | <b>ID:</b> % Éxito en finales
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