import streamlit as st
import pandas as pd
import gspread

# --- 1. DICCIONARIO DE COLORES ---
COLORES_EQUIPOS = {
    "FC Bayern Munich": "#DC052D",
    "Real Madrid": "#000000",
    "FC Barcelona": "#A50044",
    # Añade más equipos aquí...
}

# --- 2. DICCIONARIO DE ESCUDOS ---
LOGOS_EQUIPOS = {
    "FC Bayern Munich": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/FC_Bayern_M%C3%BCnchen_logo_%282017%29.svg/1024px-FC_Bayern_M%C3%BCnchen_logo_%282017%29.svg.png",
    # Añade más logos aquí...
}

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="ToNOI - Resultados",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS CSS (DISEÑO PRO) ---
st.markdown("""
<style>
    /* 1. LIMPIEZA DE INTERFAZ */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display: none;}
    
    /* ESTO QUITA EL HUECO BLANCO DE ARRIBA */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
    }
    
    /* 2. ESTILOS DE LA APP */
    .stApp { background-color: #f0f2f6; }
    
    /* --- NUEVO HEADER TIPO SANDWICH --- */
    .custom-header {
        display: flex;
        justify-content: space-between; /* Separa los elementos a los extremos */
        align-items: center; /* Centra verticalmente */
        background-color: white;
        padding: 15px 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 25px;
        border-bottom: 4px solid #31333F;
    }
    /* Secciones laterales para los logos */
    .header-side {
        flex: 0 0 auto;
    }
    .header-logo {
        width: 90px; /* Un poco más grandes */
        height: auto;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
        display: block;
    }
    /* Sección central */
    .header-center {
        flex: 1;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 0 20px;
    }
    /* Título ROJO y GRANDE */
    .header-title {
        font-size: 2.2rem; /* Mucho más grande */
        font-weight: 900; /* Más grueso */
        color: #D00000; /* ROJO INTENSO */
        margin: 0;
        line-height: 1.1;
        text-transform: uppercase;
    }
    .header-subtitle {
        font-size: 1rem; color: #555; margin-bottom: 15px; font-weight: bold;
    }
    .header-socials {
        display: flex;
        gap: 15px;
    }
    /* Botones sociales */
    .social-btn {
        text-decoration: none !important;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
        display: flex;
        align-items: center;
        gap: 8px;
        transition: transform 0.2s;
        border: none;
        white-space: nowrap;
    }
    .social-btn:hover { transform: scale(1.05); opacity: 0.9; }
    .btn-x { background-color: #000000; color: white !important; }
    .btn-wa { background-color: #25D366; color: white !important; }

    /* --- TARJETAS --- */
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
    .reglas-container {
        background-color: #fff3cd; 
        border: 1px solid #ffeeba; 
        border-radius: 8px; 
        padding: 15px; 
        margin-top: 20px;
        color: #856404; 
        font-size: 0.9rem;
    }
    /* Ajuste para móviles: en pantallas pequeñas, apilar verticalmente */
    @media (max-width: 768px) {
        .custom-header { flex-direction: column; gap: 15px; padding: 15px; }
        .header-title { font-size: 1.5rem; }
        .header-logo { width: 70px; }
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

# --- HEADER GLOBAL (ESTRUCTURA SANDWICH) ---
def mostrar_header():
    img_url = "https://github.com/TorneoNoOficialDeInglaterra/TorneoNoOficialdeInglaterra/blob/main/logo.png?raw=true"
    x_url = "https://x.com/ToNOI_oficial"
    wa_url = "https://whatsapp.com/channel/0029Vb6s1kSJ93wblhQfYY3q"
    
    # IMPORTANTE: Todo el HTML pegado a la izquierda.
    # Estructura: LogoIzq - Centro - LogoDer
    html_header = f"""
<div class="custom-header">
<div class="header-side">
<img src="{img_url}" class="header-logo">
</div>
<div class="header-center">
<div class="header-title">Torneo No Oficial de Inglaterra</div>
<div class="header-subtitle">(ToNOI)</div>
<div class="header-socials">
<a href="{x_url}" target="_blank" class="social-btn btn-x"><span>𝕏</span> Síguenos</a>
<a href="{wa_url}" target="_blank" class="social-btn btn-wa"><span>💬</span> WhatsApp</a>
</div>
</div>
<div class="header-side">
<img src="{img_url}" class="header-logo">
</div>
</div>
"""
    st.markdown(html_header, unsafe_allow_html=True)

# --- PÁGINAS ---

def pagina_inicio():
    historial = cargar_datos_gsheets("HistorialPartidos")
    if not historial: st.info("El torneo aún no ha comenzado."); return

    campeon = obtener_campeon_actual(historial)
    
    colores = globals().get('COLORES_EQUIPOS', {}) 
    logos = globals().get('LOGOS_EQUIPOS', {})
    
    color_fondo = colores.get(campeon, "#FFD700") 
    logo_url = logos.get(campeon, "https://cdn-icons-png.flaticon.com/512/1603/1603859.png") 
    
    color_texto = "white" if color_fondo in ["#000000", "#0000FF", "#8B0000", "#DC052D", "#A50044"] else "black"

    html_campeon = f"""
<div class="champion-card" style="background-color: {color_fondo}; color: {color_texto};">
<div style="font-size: 1rem; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9;">🏆 Campeón Actual 🏆</div>
<img src="{logo_url}" style="width: 120px; height: 120px; margin: 15px auto; display: block; filter: drop-shadow(0 0 10px rgba(0,0,0,0.3)); object-fit: contain;">
<div style="font-size: 3rem; font-weight: 800; margin: 5px 0; line-height: 1;">{campeon}</div>
<div style="font-size: 0.9rem; opacity: 0.9; margin-top: 10px;">Defendiendo el título actualmente</div>
</div>
"""
    st.markdown(html_campeon, unsafe_allow_html=True)

    ultimo = historial[-1]
    res_manual = f"({ultimo['ResultadoManual']})" if ultimo.get('ResultadoManual') else ""
    
    html_partido = f"""
<div class="match-card">
<div style="color: #666; font-size: 0.8rem; margin-bottom: 5px;">📢 ÚLTIMO RESULTADO ({ultimo['Fecha']})</div>
<div style="font-size: 1.5rem; font-weight: bold;">
{ultimo['Equipo Ganador']} <span style='color:#ff4b4b'>vs</span> {ultimo['Equipo Perdedor']}
</div>
<div style="font-size: 1.2rem; margin-top: 5px;">
Resultado: <b>{ultimo['Resultado']}</b> {res_manual}
</div>
</div>
"""
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown(html_partido, unsafe_allow_html=True)

def pagina_clasificacion():
    st.header("📊 Clasificación Oficial") 
    
    data = cargar_datos_gsheets("Hoja1")
    if not data: st.warning("No hay datos disponibles."); return
    
    df = pd.DataFrame(data)
    
    cols_map = {"T": "PJ", "Partidos con Trofeo": "PcT", "Mejor Racha": "MJ", "Destronamientos": "Des", "Intentos": "I"}
    df = df.rename(columns=cols_map)

    for col in ['P', 'PJ', 'Des', 'I']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df['PPP'] = df.apply(lambda x: x['P'] / x['PJ'] if x['PJ'] > 0 else 0.0, axis=1)
    df['ID'] = df.apply(lambda x: (x['Des'] / x['I']) * 100 if x['I'] > 0 else 0.0, axis=1)

    historial = cargar_datos_gsheets("HistorialPartidos")
    campeon = obtener_campeon_actual(historial)

    if "P" in df.columns:
        df = df.sort_values(by="P", ascending=False).reset_index(drop=True)
    
    df.insert(0, 'Pos.', range(1, len(df) + 1))
    
    if "Equipo" in df.columns:
        df['Equipo'] = df.apply(lambda row: f"{row['Equipo']} 👑" if row['Equipo'] == campeon else row['Equipo'], axis=1)
    
    df['PPP'] = df['PPP'].map('{:,.2f}'.format)
    df['ID'] = df['ID'].map('{:,.2f}%'.format)

    orden_cols = ["Pos.", "Equipo", "PJ", "V", "E", "D", "P", "GF", "GC", "DG", "PPP", "PcT", "MJ", "Des", "I", "ID"]
    cols_finales = [c for c in orden_cols if c in df.columns]
    
    html_leyenda = """
<div class="leyenda-container">
<div style="font-weight: bold; margin-bottom: 8px; font-size: 1rem;">📖 GLOSARIO DE DATOS:</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
<div>• <b>PJ:</b> Partidos Jugados</div>
<div>• <b>V/E/D:</b> Victorias / Empates / Derrotas</div>
<div>• <b>P:</b> Puntos Totales</div>
<div>• <b>PPP:</b> Puntos por Partido</div>
<div>• <b>GF/GC/DG:</b> Goles Favor / Contra / Diferencia</div>
<div>• <b>PcT:</b> Partidos con Trofeo</div>
</div>
<hr style="margin: 10px 0; border-color: #d1e7dd;">
<div>• <b>MJ:</b> Mejor racha (partidos seguidos con el trofeo)</div>
<div>• <b>I:</b> Número de intentos para destronar al campeón</div>
<div>• <b>Des:</b> Destronamientos (títulos ganados)</div>
<div>• <b>ID:</b> Porcentaje de éxito (Des/I)</div>
</div>
"""
    st.markdown(html_leyenda, unsafe_allow_html=True)
    st.dataframe(df[cols_finales], hide_index=True, use_container_width=True)

    html_reglas = """
<div class="reglas-container">
<div style="font-weight: bold; margin-bottom: 8px;">⚖️ SISTEMA DE PUNTUACIÓN:</div>
<ul style="margin: 0; padding-left: 20px; list-style-type: disc;">
<li><b>Victoria:</b> 2 Puntos</li>
<li><b>Empate (Siendo Campeón):</b> 1 Punto (Retiene título)</li>
<li><b>Empate (Siendo Aspirante):</b> 0 Puntos</li>
<li><b>Derrota:</b> 0 Puntos</li>
</ul>
</div>
"""
    st.markdown(html_reglas, unsafe_allow_html=True)

def pagina_estadisticas():
    st.header("⭐ Salón de la Fama")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👟 Goleadores")
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
    st.header("📜 Historial Completo")
    historial = cargar_datos_gsheets("HistorialPartidos")
    if not historial: st.warning("No hay partidos."); return
    
    df = pd.DataFrame(historial)
    cols = [c for c in ["Fecha", "Equipo Ganador", "Resultado", "Equipo Perdedor", "ResultadoManual"] if c in df.columns]
    st.dataframe(df[cols].iloc[::-1], hide_index=True, use_container_width=True)

# --- EJECUCIÓN PRINCIPAL ---

# 1. Mostrar el Header Global (Lo primero de todo)
mostrar_header()

# 2. Mostrar el Menú de Pestañas
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Inicio", "📊 Clasificación", "⭐ Estadísticas", "📜 Historial"])

with tab1: pagina_inicio()
with tab2: pagina_clasificacion()
with tab3: pagina_estadisticas()
with tab4: pagina_historial()

# Footer simple
st.markdown("---")
st.caption("🔄 Los datos se actualizan automáticamente cada minuto.")
