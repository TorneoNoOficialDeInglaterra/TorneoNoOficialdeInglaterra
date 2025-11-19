import streamlit as st
import pandas as pd
import gspread
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="ToNOI - Resultados",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed" # Menú cerrado para parecer más una App
)

# --- ESTILOS CSS PERSONALIZADOS ---
# Esto le da un toque más "pro" y quita el relleno sobrante
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
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN Y CACHÉ ---
# Usamos ttl=60 para que los datos se actualicen solos cada 60 segundos
@st.cache_data(ttl=60)
def cargar_datos_gsheets(nombre_hoja):
    try:
        # Conexión (Usa los mismos secretos que la privada)
        creds = st.secrets["gcp_creds"]
        gc = gspread.service_account_from_dict(creds)
        # ID de tu hoja de cálculo (EL MISMO que la privada)
        ID_HOJA = "18x6wCv0E7FOpuvwZpWYRSFi56E-_RR2Gm1deHyCLo2Y"
        sh = gc.open_by_key(ID_HOJA).worksheet(nombre_hoja)
        return sh.get_all_records()
    except Exception as e:
        return []

# --- LÓGICA LIGERA (Solo para detectar al campeón actual) ---
def obtener_campeon_actual(historial):
    if not historial: return "Vacante"
    portador = None
    for partido in historial:
        ganador = partido.get('Equipo Ganador')
        perdedor = partido.get('Equipo Perdedor')
        resultado = partido.get('Resultado')
        
        if not portador:
            portador = ganador # El primero en ganar se lo lleva
        else:
            # Si el portador juega
            if portador == ganador or portador == perdedor:
                aspirante = ganador if perdedor == portador else perdedor
                # Solo cambia de manos si el aspirante GANA (no vale empate)
                if resultado == "Victoria" and ganador == aspirante:
                    portador = aspirante
    return portador

# --- PÁGINAS ---

def pagina_inicio():
    st.title("⚽ ToNOI - Panel Central")
    
    # Cargar datos mínimos necesarios
    historial = cargar_datos_gsheets("HistorialPartidos")
    
    if not historial:
        st.info("El torneo aún no ha comenzado.")
        return

    # 1. TARJETA DEL CAMPEÓN
    campeon = obtener_campeon_actual(historial)
    st.markdown(f"""
    <div class="champion-card">
        <div style="font-size: 1.2rem;">👑 REY DE LA COLINA ACTUAL 👑</div>
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
    
    # Cargar datos YA PROCESADOS por la web privada
    data = cargar_datos_gsheets("Hoja1")
    if not data: st.warning("No hay datos disponibles."); return
    
    df = pd.DataFrame(data)
    
    # Detectar campeón para ponerle la corona en la tabla visualmente
    historial = cargar_datos_gsheets("HistorialPartidos")
    campeon = obtener_campeon_actual(historial)
    
    # Preparar tabla
    df = df.sort_values(by="P", ascending=False).reset_index(drop=True)
    df.insert(0, 'Pos.', range(1, len(df) + 1))
    
    # Marcar Campeón
    df['Equipo'] = df.apply(lambda row: f"{row['Equipo']} 👑" if row['Equipo'] == campeon else row['Equipo'], axis=1)
    
    # Formateo numérico visual
    try:
        df['PPP'] = pd.to_numeric(df['PPP']).map('{:,.2f}'.format)
        df['Indice Destronamiento'] = pd.to_numeric(df['Indice Destronamiento']).map('{:,.2f}%'.format)
    except:
        pass # Si falla el formato, se muestra tal cual

    # Renombrar y Reordenar (Exactamente como pediste)
    cols_map = {
        "T": "PJ", "Partidos con Trofeo": "PcT", "Mejor Racha": "MR",
        "Destronamientos": "Des", "Intentos": "I", "Indice Destronamiento": "ID"
    }
    df = df.rename(columns=cols_map)
    
    # Orden solicitado
    orden_cols = ["Pos.", "Equipo", "PJ", "V", "E", "D", "P", "GF", "GC", "DG", "PPP", "PcT", "MR", "Des", "I", "ID"]
    cols_finales = [c for c in orden_cols if c in df.columns]
    
    # Leyenda
    st.info("💡 **Leyenda:** **PcT:** Partidos con Trofeo | **Des:** Títulos Ganados | **ID:** % Éxito en finales")
    
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
    # Seleccionar solo columnas limpias
    cols = [c for c in ["Fecha", "Equipo Ganador", "Resultado", "Equipo Perdedor", "ResultadoManual"] if c in df.columns]
    # Mostrar lo más nuevo arriba
    st.dataframe(df[cols].iloc[::-1], hide_index=True, use_container_width=True)

# --- MENÚ DE NAVEGACIÓN (TABS) ---
# Usamos pestañas superiores para una experiencia más "Móvil/App"
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Inicio", "📊 Clasificación", "⭐ Estadísticas", "📜 Historial"])

with tab1: pagina_inicio()
with tab2: pagina_clasificacion()
with tab3: pagina_estadisticas()
with tab4: pagina_historial()

# Footer discreto
st.markdown("---")
st.caption("🔄 Los datos se actualizan automáticamente cada minuto.")
