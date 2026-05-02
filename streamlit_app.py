import streamlit as st
import pandas as pd
import gspread
from datetime import datetime

# --- 1. DICCIONARIO DE COLORES ---
COLORES_EQUIPOS = {
    "FC Bayern Munich": "#DC052D",
    "Arsenal": "#EF0107", # Rojo Arsenal
    "Real Madrid CF": "#000000",
    "FC Barcelona": "#A50044",
    "Aston Villa": "#BF082B",
    "Manchester City": "#6CABDD",
    "Liverpool": "#C8102E",
    "Manchester United": "#C8102E",
    "RCD Mallorca": "#BD1B0D",
    "Deportivo Alaves": "#1300FC",
    "Athletic Club de Bilbao": "#EF0107"
}

# --- 2. DICCIONARIO DE ESCUDOS ---
LOGOS_EQUIPOS = {
    "FC Bayern Munich": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/FC_Bayern_M%C3%BCnchen_logo_%282017%29.svg/1024px-FC_Bayern_M%C3%BCnchen_logo_%282017%29.svg.png",
    "Arsenal": "https://upload.wikimedia.org/wikipedia/hif/8/82/Arsenal_FC.png",      
    "Aston Villa": "https://upload.wikimedia.org/wikipedia/pt/thumb/1/15/Aston_Villa.svg/732px-Aston_Villa.svg.png",
    "Manchester United": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/soccer/500/360.png",
    "Real Madrid CF": "https://upload.wikimedia.org/wikipedia/en/thumb/5/56/Real_Madrid_CF.svg/960px-Real_Madrid_CF.svg.png",
    "RCD Mallorca": "https://upload.wikimedia.org/wikipedia/en/thumb/e/e0/Rcd_mallorca.svg/960px-Rcd_mallorca.svg.png",
    "Deportivo Alaves": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f8/Deportivo_Alaves_logo_%282020%29.svg/1280px-Deportivo_Alaves_logo_%282020%29.svg.png",
    "Athletic Club de Bilbao": "data:image/png;base64,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"
}

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="ToNOI - Resultados",
    page_icon="https://github.com/TorneoNoOficialDeInglaterra/TorneoNoOficialdeInglaterra/blob/main/logo.png?raw=true",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS CSS ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppDeployButton {display: none;}
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
    }
    
    .stApp { background-color: #f0f2f6; }
    
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

    .champion-card {
        background-color: #FFD700;
        padding: 20px;
        border-radius: 10px;
        color: black;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
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
        margin-bottom: 20px;
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
            # CORRECCIÓN AQUÍ: Quitamos 'dayfirst=True' para que detecte mejor los formatos mixtos (US/EU)
            fecha_inicio = pd.to_datetime(fecha_inicio_str) 
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
    
    color_texto = "white" if color_fondo in ["#000000", "#0000FF", "#8B0000", "#DC052D", "#A50044", "#BF082B"] else "black"

    # --- 1. CAMPEÓN ACTUAL ---
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

    # --- 2. ÚLTIMO PARTIDO ---
    ultimo = historial[-1]
    
    # Blindaje con .get()
    u_fecha = ultimo.get('Fecha', 'Fecha desconocida')
    u_ganador = ultimo.get('Equipo Ganador', 'Equipo A')
    u_perdedor = ultimo.get('Equipo Perdedor', 'Equipo B')
    u_resultado = ultimo.get('Resultado', 'Finalizado')
    u_manual = f"({ultimo.get('ResultadoManual', '')})" if ultimo.get('ResultadoManual') else ""
    
    html_partido = f"""
<div class="match-card">
<div style="color: #666; font-size: 0.8rem; margin-bottom: 5px;">📢 ÚLTIMO RESULTADO ({u_fecha})</div>
<div style="font-size: 1.5rem; font-weight: bold;">
{u_ganador} <span style='color:#ff4b4b'>vs</span> {u_perdedor}
</div>
<div style="font-size: 1.2rem; margin-top: 5px;">
Resultado: <b>{u_resultado}</b> {u_manual}
</div>
</div>
"""
    # Usamos columnas para centrarlo
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown(html_partido, unsafe_allow_html=True)

    # --- 3. INFORMACIÓN Y VIDEO ---
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








