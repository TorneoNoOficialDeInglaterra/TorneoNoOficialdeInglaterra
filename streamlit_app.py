import streamlit as st
import pandas as pd
import gspread
from datetime import datetime

# --- 1. DICCIONARIO DE COLORES ---
COLORES_EQUIPOS = {
    "FC Bayern Munich": "#DC052D",
    "Arsenal": "#DC052D",
    "Real Madrid": "#000000",
    "FC Barcelona": "#A50044",
    # Añade más equipos aquí...
}

# --- 2. DICCIONARIO DE ESCUDOS ---
LOGOS_EQUIPOS = {
    "FC Bayern Munich": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/FC_Bayern_M%C3%BCnchen_logo_%282017%29.svg/1024px-FC_Bayern_M%C3%BCnchen_logo_%282017%29.svg.png",
    "Arsenal": "https://upload.wikimedia.org/wikipedia/hif/8/82/Arsenal_FC.png",    
    "Aston Villa": "https://upload.wikimedia.org/wikipedia/pt/thumb/1/15/Aston_Villa.svg/732px-Aston_Villa.svg.png"
    # Añade más logos aquí...
}

# --- CONFIGURACIÓN DE LA PÁGINA (ICONO CAMBIADO) ---
st.set_page_config(
    page_title="ToNOI - Resultados",
    page_icon="https://github.com/TorneoNoOficialDeInglaterra/TorneoNoOficialdeInglaterra/blob/main/logo.png?raw=true",
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
        justify-content: space-between;
        align-items: center;
        background-color: white;
        padding: 15px 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 25px;
        border-bottom: 4px solid #31333F;
    }
    .header-side { flex: 0 0 auto; }
    .header-logo {
        width: 90px;
        height: auto;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
        display: block;
    }
    .header-center {
        flex: 1;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 0 20px;
    }
    .header-title {
        font-size: 2.2rem;
        font-weight: 900;
        color: #D00000;
        margin: 0;
        line-height: 1.1;
        text-transform: uppercase;
    }
    .header-subtitle {
        font-size: 1rem; color: #555; margin-bottom: 15px; font-weight: bold;
    }
    .header-socials { display: flex; gap: 15px; }
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
    /* ESTILO NUEVO PARA LA DESCRIPCIÓN */
    .desc-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        color: #333;
        font-size: 0.95rem;
        line-height: 1.6;
        text-align: justify;
    }
    .desc-title {
        font-weight: 800;
        color: #31333F;
        font-size: 1.1rem;
        margin-bottom: 10px;
        text-transform: uppercase;
        border-bottom: 2px solid #f0f2f6;
        padding-bottom: 5px;
    }
    .match-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 20px; /* Espacio extra abajo */
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
def obtener_datos_campeon(historial):
    if not historial: return "Vacante", None
    portador = None
    fecha_inicio = None
    
    for partido in historial:
        ganador = partido.get('Equipo Ganador')
        perdedor = partido.get('Equipo Perdedor')
        resultado = partido.get('Resultado')
        fecha_partido = partido.get('Fecha')
        
        if not portador:
            portador = ganador
            fecha_inicio = fecha_partido
        else:
            if portador == ganador or portador == perdedor:
                aspirante = ganador if perdedor == portador else perdedor
                if resultado == "Victoria" and ganador == aspirante:
                    portador = aspirante
                    fecha_inicio = fecha_partido 
                    
    return portador, fecha_inicio

# --- HEADER GLOBAL ---
def mostrar_header():
    img_url = "https://github.com/TorneoNoOficialDeInglaterra/TorneoNoOficialdeInglaterra/blob/main/logo.png?raw=true"
    x_url = "https://x.com/ToNOI_oficial"
    wa_url = "https://whatsapp.com/channel/0029Vb6s1kSJ93wblhQfYY3q"
    
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

    campeon, fecha_inicio_str = obtener_datos_campeon(historial)
    
    texto_tiempo = "Recién coronado"
    if fecha_inicio_str:
        try:
            fecha_inicio = pd.to_datetime(fecha_inicio_str, dayfirst=True)
            ahora = pd.Timestamp.now()
            diferencia = ahora - fecha_inicio
            
            dias = diferencia.days
            segundos_totales = diferencia.seconds
            horas = segundos_totales // 3600
            minutos = (segundos_totales % 3600) // 60
            
            texto_tiempo = f"⏳ {dias} días, {horas}h, {minutos}m defendiendo el título"
        except Exception as e:
            texto_tiempo = f"Desde: {fecha_inicio_str}"

    colores = globals().get('COLORES_EQUIPOS', {}) 
    logos = globals().get('LOGOS_EQUIPOS', {})
    
    color_fondo = colores.get(campeon, "#FFD700") 
    logo_url = logos.get(campeon, "https://cdn-icons-png.flaticon.com/512/1603/1603859.png") 
    
    color_texto = "white" if color_fondo in ["#000000", "#0000FF", "#8B0000", "#DC052D", "#A50044"] else "black"

    # --- 1. CAMPEÓN ACTUAL (Arriba) ---
    html_campeon = f"""
<div class="champion-card" style="background-color: {color_fondo}; color: {color_texto};">
<div style="font-size: 1rem; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9;">🏆 Campeón Actual 🏆</div>
<img src="{logo_url}" style="width: 120px; height: 120px; margin: 15px auto; display: block; filter: drop-shadow(0 0 10px rgba(0,0,0,0.3)); object-fit: contain;">
<div style="font-size: 3rem; font-weight: 800; margin: 5px 0; line-height: 1;">{campeon}</div>
<div style="font-size: 1.1rem; font-weight: bold; margin-top: 5px; background-color: rgba(0,0,0,0.2); display: inline-block; padding: 5px 15px; border-radius: 15px;">
    {texto_tiempo}
</div>
<div style="font-size: 0.9rem; opacity: 0.9; margin-top: 10px;">Defendiendo el título actualmente</div>
</div>
"""
    st.markdown(html_campeon, unsafe_allow_html=True)

    # --- 2. ÚLTIMO PARTIDO (En medio) ---
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
    # Usamos columnas para centrarlo
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown(html_partido, unsafe_allow_html=True)

    # --- 3. INFORMACIÓN Y VIDEO (Abajo) ---
    with col2:
        html_desc = """
<div class="desc-card">
<div class="desc-title">¿Qué es el ToNOI?</div>
<p><b>¿Te imaginas que pasaría si en el fútbol se decidiera quién es el campeón como se hace en el boxeo?</b> Pues nosotros estamos aquí para contarlo.</p>
<p>El <b>Torneo No Oficial de Inglaterra (ToNOI)</b> es un campeonato en el que para ser campeón debes ganar al actual campeón. No existen fase de grupos, eliminatorias ni nada por el estilo, solo finales. Si te enfrentas al equipo campeón y resultas victorioso, serás el nuevo <b>CAMPEÓN NO OFICIAL DE INGLATERRA</b> y comenzarás a hacer historia hasta verte derrotado por otro equipo.</p>
<div class="desc-title" style="font-size: 1rem; margin-top: 15px;">📜 Reglamento Oficial</div>
<ul style="margin-left: 20px; padding: 0;">
<li>Si ganas al actual campeón, te conviertes en campeón.</li>
<li>Solo valen partidos oficiales.</li>
<li>Si en una liga no hay registros oficiales se contará el siguiente partido oficial.</li>
<li>En caso de desaparición del club campeón, el título vuelve al anterior campeón.</li>
<li>Todas las prórrogas cuentan.</li>
<li><b>Los penaltis cuentan:</b> si el partido acaba en empate global o requiere desempate, el ganador se lleva el título.</li>
</ul>
<p style="margin-top: 15px; text-align: center; font-weight: bold;">Sumérgete con nosotros en esta aventura y disfruta del fútbol como nunca.</p>
</div>
"""
        st.markdown(html_desc, unsafe_allow_html=True)
        
        st.info("🎥 **Para entenderlo mejor, te recomendamos este vídeo de La Media Inglesa:**")
        st.video("https://youtu.be/SpRxKO4BRfk")
        st.markdown("<br>", unsafe_allow_html=True)

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
    campeon, _ = obtener_datos_campeon(historial)

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







