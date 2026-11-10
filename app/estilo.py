"""Identidad visual de ReciclaGov: paleta, tipografía, textura y componentes reutilizables.

Paleta de seis tonos (verdes de hoja y azules de agua) y Montserrat en tres pesos. Black para
títulos, Medium para subtítulos y Regular para el cuerpo del texto. Los personajes Vera y Don Ciclo
son diseño de la autora.
"""
import base64
from pathlib import Path

import streamlit as st

PALETA = {
    "brote": "#D0E6A6",   # fondos suaves y resaltados
    "hoja": "#BFD37A",    # acento principal
    "laguna": "#89B2AE",  # acento secundario
    "rio": "#5B818E",     # textos secundarios grandes y bordes
    "noche": "#234257",   # títulos y botones
    "bosque": "#293E3F",  # texto principal
    "chispa": "#6DBE45",  # verde vivo para resaltar logros
    "musgo": "#3E8E63",   # verde profundo para degradados
}
ASSETS = Path(__file__).resolve().parent / "assets"

# Textura de papel muy suave, hecha con ruido SVG (no requiere descargar imágenes)
RUIDO = ("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'>"
         "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/>"
         "<feColorMatrix values='0 0 0 0 0.16 0 0 0 0 0.24 0 0 0 0 0.25 0 0 0 .07 0'/></filter>"
         "<rect width='100%' height='100%' filter='url(%23n)'/></svg>")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;900&display=swap');

/* ---------- base y textura ---------- */
.stApp {
  background-color: #F5F8EE;
  background-image:
    radial-gradient(1100px 520px at 8% -8%, rgba(191,211,122,.38), transparent 60%),
    radial-gradient(900px 520px at 105% 4%, rgba(137,178,174,.34), transparent 60%),
    radial-gradient(800px 600px at 50% 120%, rgba(208,230,166,.45), transparent 60%),
    url("__RUIDO__");
  background-attachment: fixed;
}
/* patrón ecológico flotando detrás de todo */
.stApp::before { content: ""; position: fixed; inset: -300px; z-index: 0; pointer-events: none;
  background-image: url("__PATRON__"); background-size: 300px 300px; opacity: .13;
  animation: deriva 90s linear infinite; }
.stApp::after { content: ""; position: fixed; inset: 0; z-index: 0; pointer-events: none;
  background: radial-gradient(600px 400px at var(--x, 80%) 20%, rgba(109,190,69,.18), transparent 70%);
  animation: respira 14s ease-in-out infinite alternate; }
[data-testid="stAppViewContainer"] > *, [data-testid="stMain"] { position: relative; z-index: 1; }
@keyframes deriva { from { transform: translate(0, 0) rotate(0deg); } to { transform: translate(300px, 300px) rotate(0deg); } }
@keyframes respira { from { --x: 75%; opacity: .7; } to { --x: 25%; opacity: 1; } }
@keyframes subir { from { opacity: 0; transform: translateY(26px); } to { opacity: 1; transform: none; } }
@keyframes flotar { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
@keyframes brillo { 0% { background-position: 0% 50%; } 100% { background-position: 200% 50%; } }
@keyframes latido { 0%, 100% { box-shadow: 0 0 0 0 rgba(109,190,69,.55); } 50% { box-shadow: 0 0 0 12px rgba(109,190,69,0); } }
header[data-testid="stHeader"] { display: none; }

/* barra de navegación de lado a lado */
.st-key-barra { position: fixed; top: 0; left: 0; right: 0; z-index: 1000; padding: .55rem 2.2rem;
  background: rgba(245,248,238,.82); backdrop-filter: blur(16px); border-bottom: 1px solid rgba(35,66,87,.1);
  box-shadow: 0 10px 30px -22px rgba(35,66,87,.6); }
.st-key-barra [data-testid="stHorizontalBlock"] { align-items: center; gap: .35rem; }
.st-key-barra .logo { font-weight: 900; font-size: 1.35rem; color: #234257; letter-spacing: -.03em; white-space: nowrap; }
.st-key-barra .logo b { color: #3E8E63; }
.st-key-barra [data-testid="stPageLink"] a { border-radius: 999px; padding: .35rem .8rem; justify-content: center; }
.st-key-barra [data-testid="stPageLink"] a:hover { background: rgba(191,211,122,.35); }
.st-key-barra [data-testid="stPageLink"] p { font-weight: 500; font-size: .9rem; white-space: nowrap; }
.st-key-barra [data-testid="stPageLink"] a[aria-current="page"], .st-key-barra [data-testid="stPageLink"] a[data-active="true"] {
  background: #234257; } 
.st-key-barra [data-testid="stPageLink"] a[aria-current="page"] p { color: #FFFFFF !important; }
.st-key-nav-vera [data-testid="stPageLink"] a { border: 2px solid #6DBE45; background: #FFFFFF; }
.st-key-nav-vera [data-testid="stPageLink"] p { color: #3E8E63 !important; font-weight: 900 !important; }
.st-key-nav-recicla [data-testid="stPageLink"] a, .st-key-cta-recicla [data-testid="stPageLink"] a {
  background: linear-gradient(135deg, #3E8E63, #6DBE45); animation: latido 2.6s ease-in-out infinite;
  box-shadow: 0 10px 22px -12px rgba(62,142,99,.9); }
.st-key-nav-recicla [data-testid="stPageLink"] p, .st-key-cta-recicla [data-testid="stPageLink"] p,
.st-key-nav-recicla [data-testid="stPageLink"] span, .st-key-cta-recicla [data-testid="stPageLink"] span {
  color: #FFFFFF !important; font-weight: 900 !important; }
.st-key-cta-muni [data-testid="stPageLink"] a { background: #FFFFFF; border: 2px solid #234257; }
.st-key-cta-muni [data-testid="stPageLink"] p { font-weight: 900 !important; color: #234257 !important; }
.st-key-cta-recicla [data-testid="stPageLink"] a, .st-key-cta-muni [data-testid="stPageLink"] a {
  border-radius: 999px; padding: .75rem 1.4rem; justify-content: center; }

/* ticket digital */
.ticket { display: flex; gap: 1.6rem; align-items: center; background: #FFFFFF; border-radius: 26px;
  padding: 1.6rem; border: 2px dashed #6DBE45; box-shadow: 0 22px 46px -24px rgba(35,66,87,.55);
  animation: subir .6s ease both; }
.ticket img { width: 170px; border-radius: 14px; }
.ticket .codigo { font-weight: 900; font-size: 2.2rem; color: #234257; letter-spacing: .04em; }
.ticket .estado { display: inline-block; background: #F3E7C9; color: #6B4E00; border-radius: 999px;
  padding: .2rem .8rem; font-size: .78rem; font-weight: 500; }
.ticket .estado.ok { background: #D0E6A6; color: #234257; }
.ticket p { margin: .35rem 0 0 0; font-size: .92rem; }
.retrato { display: flex; justify-content: center; align-items: flex-end; height: 280px; border-radius: 28px;
  overflow: hidden; background: radial-gradient(circle at 50% 30%, #E7F1D2 0%, #BFD37A 60%, #89B2AE 100%);
  box-shadow: 0 18px 40px -22px rgba(35,66,87,.6); }
.retrato img { width: 80% !important; margin: 0 auto; animation: flotar 6s ease-in-out infinite; }
html, body, p, li, label, input, textarea, button, td, th, .stMarkdown, [data-testid="stMetricLabel"],
[data-testid="stWidgetLabel"] { font-family: 'Montserrat', sans-serif !important; color: #293E3F; }
h1, h2, h3, h4 { font-family: 'Montserrat', sans-serif !important; color: #234257 !important; }
h1, h2, h3, h4, h5 { font-weight: 900 !important; letter-spacing: -0.025em; }
.block-container { padding-top: 6.4rem; max-width: 1220px; }
[data-testid="stWidgetLabel"] p { font-weight: 500 !important; color: #234257 !important; }

/* ---------- encabezado de sección ---------- */
.portada { position: relative; overflow: hidden; border-radius: 28px; padding: 2.6rem 2.8rem;
  margin-bottom: 2rem; display: flex; align-items: center; gap: 2.4rem;
  background: linear-gradient(120deg, #234257, #293E3F, #3E8E63, #234257); background-size: 300% 300%;
  animation: brillo 18s ease-in-out infinite alternate, subir .7s ease both;
  box-shadow: 0 24px 60px -24px rgba(35,66,87,.55); }
.portada::before { content: ""; position: absolute; width: 420px; height: 420px; right: -120px; top: -180px;
  border-radius: 50%; background: radial-gradient(circle, rgba(191,211,122,.35), transparent 70%); }
.portada::after { content: ""; position: absolute; width: 300px; height: 300px; left: 38%; bottom: -200px;
  border-radius: 50%; background: radial-gradient(circle, rgba(137,178,174,.30), transparent 70%); }
.portada > div { position: relative; z-index: 1; }
.portada h1 { color: #FFFFFF !important; font-size: 2.9rem; margin: 0; line-height: 1.08; }
.portada .eyebrow { display: inline-block; color: #234257; background: #BFD37A; font-weight: 900;
  letter-spacing: .14em; text-transform: uppercase; font-size: .7rem; padding: .35rem .8rem;
  border-radius: 999px; margin-bottom: 1rem; }
.portada p { color: #E6F0D0 !important; font-weight: 400; font-size: 1.08rem; line-height: 1.6;
  margin: 1rem 0 0 0; max-width: 44rem; }
.portada h1 .resalte { font-style: normal; background: linear-gradient(90deg, #BFD37A, #6DBE45, #D0E6A6); -webkit-background-clip: text;
  background-clip: text; color: transparent; }
.portada .ilustracion { animation: flotar 6s ease-in-out infinite; position: relative; z-index: 1; flex-shrink: 0; width: 46%; border-radius: 22px;
  overflow: hidden; box-shadow: 0 18px 40px -18px rgba(0,0,0,.55); border: 4px solid rgba(255,255,255,.18); }
.portada .ilustracion img { width: 100%; display: block; }

/* ---------- títulos de bloque ---------- */
.seccion { margin: 2.4rem 0 1rem 0; }
.seccion .kicker { color: #5B818E; font-weight: 900; letter-spacing: .16em; text-transform: uppercase;
  font-size: .72rem; }
.seccion h2 { margin: .2rem 0 0 0 !important; font-size: 2rem; }

/* ---------- tarjetas ---------- */
.tarjeta { background: rgba(255,255,255,.78); backdrop-filter: blur(10px); border: 1px solid rgba(191,211,122,.55);
  border-radius: 22px; padding: 1.5rem 1.5rem 1.4rem; height: 100%;
  box-shadow: 0 14px 34px -18px rgba(35,66,87,.35); transition: transform .25s ease, box-shadow .25s ease;
  animation: subir .7s ease both; }
[data-testid="stColumn"]:nth-child(2) .tarjeta { animation-delay: .12s; }
[data-testid="stColumn"]:nth-child(3) .tarjeta { animation-delay: .24s; }
[data-testid="stColumn"]:nth-child(4) .tarjeta { animation-delay: .36s; }
.tarjeta .num { background: linear-gradient(90deg, #234257, #3E8E63); -webkit-background-clip: text;
  background-clip: text; color: transparent !important; }
.tarjeta:hover { transform: translateY(-6px) rotate(-.3deg); border-color: #6DBE45; box-shadow: 0 22px 44px -18px rgba(35,66,87,.45); }
.tarjeta .num { font-weight: 900; font-size: 2.3rem; color: #234257; line-height: 1; letter-spacing: -.02em; }
.tarjeta .tit { font-weight: 900; color: #234257; font-size: 1.08rem; margin: .55rem 0 .35rem 0; }
.tarjeta .txt { font-size: .93rem; color: #293E3F; line-height: 1.6; }
.paso { animation: latido 2.8s ease-in-out infinite; display: inline-flex; align-items: center; justify-content: center; width: 2.4rem; height: 2.4rem;
  border-radius: 14px; background: linear-gradient(135deg, #BFD37A, #D0E6A6); color: #234257;
  font-weight: 900; margin-bottom: .4rem; box-shadow: 0 8px 18px -10px rgba(35,66,87,.6); }
.etiqueta { display: inline-block; padding: .28rem .85rem; border-radius: 999px; font-size: .76rem;
  font-weight: 500; background: #D0E6A6; color: #234257; margin: 0 .35rem .45rem 0; }
.etiqueta.alerta { background: #F3E7C9; color: #6B4E00; }
.banda { animation: subir .7s ease both; background: linear-gradient(110deg, #D0E6A6, #E7F1D2, #BFD37A); border-radius: 20px; padding: 1.2rem 1.5rem;
  color: #234257; font-weight: 500; font-size: 1.06rem; margin: .8rem 0 1.2rem 0;
  border: 1px solid rgba(191,211,122,.8); }
.banda b { font-weight: 900; }
.nota { color: #5B818E; font-size: .84rem; line-height: 1.5; margin-top: 1rem; }
.pie { text-align: center; color: #5B818E; font-size: .8rem; margin-top: 3.5rem; padding-top: 1.4rem;
  border-top: 1px solid rgba(35,66,87,.1); }

/* ---------- métricas como tarjetas ---------- */
div[data-testid="stMetric"] { animation: subir .6s ease both; background: rgba(255,255,255,.8); backdrop-filter: blur(8px);
  border: 1px solid rgba(137,178,174,.45); border-radius: 20px; padding: 1.1rem 1.25rem;
  box-shadow: 0 12px 28px -18px rgba(35,66,87,.35); }
div[data-testid="stMetricValue"] { font-family: 'Montserrat', sans-serif; font-weight: 900; color: #234257;
  letter-spacing: -.02em; }

/* ---------- controles ---------- */
.stButton > button, .stDownloadButton > button, .stLinkButton > a { border-radius: 14px !important;
  font-weight: 500 !important; border: 1px solid rgba(35,66,87,.18) !important; }
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {
  background: linear-gradient(135deg, #234257, #3E8E63, #6DBE45) !important; background-size: 200% 200% !important; color: #FFFFFF !important; border: none !important; transition: background-position .4s ease !important;
  box-shadow: 0 10px 22px -12px rgba(35,66,87,.8); }
.stButton > button[kind="primary"] p, .stDownloadButton > button[kind="primary"] p { color: #FFFFFF !important; }
div[data-baseweb="select"] > div, .stTextArea textarea, .stDateInput input, .stNumberInput input {
  border-radius: 14px !important; background: rgba(255,255,255,.85) !important; }
[data-testid="stDataFrame"], iframe { border-radius: 18px; overflow: hidden; }
/* cinta de datos en movimiento */
.cinta { overflow: hidden; border-radius: 999px; background: #234257; margin: 0 0 2rem 0;
  box-shadow: 0 12px 30px -18px rgba(35,66,87,.8); }
.cinta .pista { display: inline-flex; gap: 3rem; white-space: nowrap; padding: .75rem 0;
  animation: cinta 38s linear infinite; }
.cinta span { color: #D0E6A6; font-weight: 500; font-size: .9rem; }
.cinta b { color: #BFD37A; font-weight: 900; }
@keyframes cinta { from { transform: translateX(0); } to { transform: translateX(-50%); } }

/* personaje guía */
.guia { position: fixed; right: 26px; bottom: 26px; z-index: 999; display: flex; align-items: flex-end; gap: .7rem;
  animation: subir .8s ease 1s both; text-decoration: none !important; }
.guia .globo { max-width: 270px; background: #FFFFFF; color: #234257; border-radius: 20px 20px 6px 20px;
  padding: .85rem 1rem; font-size: .88rem; line-height: 1.45; box-shadow: 0 16px 34px -14px rgba(35,66,87,.55);
  border: 2px solid #BFD37A; }
.guia .globo b { font-weight: 900; display: block; margin-bottom: .15rem; color: #3E8E63; }
.guia .cara { width: 92px; height: 92px; border-radius: 50%; overflow: hidden; flex-shrink: 0;
  border: 4px solid #FFFFFF; box-shadow: 0 0 0 4px #6DBE45, 0 16px 30px -12px rgba(35,66,87,.7);
  animation: flotar 4s ease-in-out infinite; background: radial-gradient(circle at 50% 35%, #E7F1D2, #BFD37A); }
.guia .cara img { width: 100%; display: block; }
.guia:hover .globo { border-color: #6DBE45; transform: translateY(-3px); transition: .2s; }

/* chat estilo mensajes del celular */
.chat { display: flex; flex-direction: column; gap: .45rem; padding: 1.2rem; min-height: 360px;
  background: rgba(255,255,255,.82); backdrop-filter: blur(10px); border-radius: 26px;
  border: 1px solid rgba(137,178,174,.45); box-shadow: 0 18px 40px -22px rgba(35,66,87,.45); }
.chat .hora { text-align: center; color: #8A9A9B; font-size: .72rem; font-weight: 500; margin: .2rem 0 .6rem; }
.chat .fila { display: flex; align-items: flex-end; gap: .45rem; animation: subir .35s ease both; }
.chat .fila.yo { justify-content: flex-end; }
.chat .mini { width: 34px; height: 34px; border-radius: 50%; overflow: hidden; flex-shrink: 0;
  background: radial-gradient(circle at 50% 35%, #E7F1D2, #BFD37A); }
.chat .mini img { width: 100%; }
.chat .burbuja { max-width: 72%; padding: .62rem .95rem; font-size: .95rem; line-height: 1.45; border-radius: 20px; }
.chat .ella .burbuja { background: #E9E9EB; color: #1C1C1E; border-bottom-left-radius: 6px; }
.chat .yo .burbuja { background: linear-gradient(135deg, #6DBE45, #3E8E63); color: #FFFFFF; border-bottom-right-radius: 6px; }
.chat .fuente { font-size: .7rem; color: #8A9A9B; margin: -.1rem 0 .3rem 2.4rem; }
.chat .vacio { margin: auto; text-align: center; color: #5B818E; }
[data-testid="stChatInput"] { border-radius: 999px !important; border: 2px solid #BFD37A !important; }
/* ---------- tipografía uniforme en todo ---------- */
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;900&display=swap');
.stApp, .stApp *:not([data-testid="stIconMaterial"]):not(.material-symbols-rounded):not(code):not(pre) {
  font-family: 'Montserrat', sans-serif !important; }
.stApp p, .stApp li, .stApp label { color: #293E3F; }

/* ---------- contraste ---------- */
.etiqueta { background: #234257 !important; color: #FFFFFF !important; }
.etiqueta.clara { background: #FFFFFF !important; color: #234257 !important; border: 1.5px solid #89B2AE; }
.etiqueta.sol { background: #F2A541 !important; color: #234257 !important; }
.banda { background: #FFFFFF !important; border: none !important; border-left: 8px solid #F2A541 !important;
  box-shadow: 0 14px 30px -20px rgba(35,66,87,.5); color: #234257 !important; }
.banda b { color: #3E8E63; }

/* ---------- opciones como botones (sin desplegables) ---------- */
[data-testid="stPills"] button, [data-testid="stButtonGroup"] button {
  background: #FFFFFF !important; border: 1.5px solid rgba(35,66,87,.25) !important; color: #234257 !important;
  border-radius: 999px !important; font-weight: 600 !important; }
[data-testid="stPills"] button[kind*="Active"], [data-testid="stButtonGroup"] button[kind*="Active"],
[data-testid="stPills"] button[aria-checked="true"], [data-testid="stButtonGroup"] button[aria-checked="true"] {
  background: #234257 !important; color: #FFFFFF !important; border-color: #234257 !important; }
[data-testid="stPills"] button[kind*="Active"] *, [data-testid="stButtonGroup"] button[kind*="Active"] *,
[data-testid="stPills"] button[aria-checked="true"] *, [data-testid="stButtonGroup"] button[aria-checked="true"] * {
  color: #FFFFFF !important; }
.stTabs [data-baseweb="tab-list"] { gap: .4rem; }
.stTabs [data-baseweb="tab"] { background: #FFFFFF; border-radius: 999px; padding: .4rem 1.1rem !important;
  border: 1.5px solid rgba(35,66,87,.2); }
.stTabs [aria-selected="true"] { background: #234257 !important; }
.stTabs [aria-selected="true"] p { color: #FFFFFF !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

/* ---------- logo ---------- */
.marca-logo { display: flex; align-items: center; gap: .55rem; }
.marca-logo img { width: 40px !important; height: 40px; }
.marca-logo .nombre { font-weight: 900; font-size: 1.3rem; color: #234257; letter-spacing: -.03em; }
.marca-logo .nombre b { color: #3E8E63; font-weight: 900; }

/* ---------- paneles, barras, ranking ---------- */
.panel { background: #FFFFFF; border-radius: 22px; padding: 1.3rem 1.4rem; box-shadow: 0 16px 36px -22px rgba(35,66,87,.5);
  border: 1px solid rgba(35,66,87,.08); animation: subir .6s ease both; }
.barra { margin: .2rem 0 1rem 0; }
.barra-top { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: .35rem; }
.barra-etq { font-weight: 700; color: #234257; font-size: .95rem; }
.barra-val { font-weight: 900; color: #234257; font-size: .95rem; }
.barra-pista { background: #EEF2F4; border-radius: 999px; height: 14px; overflow: hidden; flex: 1; }
.barra-pista.grande { height: 26px; }
.barra-relleno { height: 100%; border-radius: 999px; animation: crecer 1.1s cubic-bezier(.2,.8,.2,1) both; }
@keyframes crecer { from { width: 0 !important; } }
.barra-det { font-size: .78rem; color: #5B818E; margin-top: .25rem; }
.rk { display: flex; gap: .9rem; align-items: center; margin-bottom: .9rem; }
.rk-pos { width: 2.3rem; height: 2.3rem; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-weight: 900; flex-shrink: 0; }
.rk-cuerpo { flex: 1; }
.cmp-fila { display: flex; align-items: center; gap: .9rem; margin: .6rem 0; }
.cmp-etq { width: 110px; font-weight: 700; color: #234257; }
.cmp-val { width: 70px; text-align: right; font-weight: 900; color: #234257; }
.cmp-msg { margin-top: .8rem; padding: .7rem 1rem; background: #FFF6E6; border-radius: 14px; color: #6B4E00; font-weight: 600; }
.vacio-panel { color: #5B818E; text-align: center; }

/* ---------- tabla ---------- */
.tabla { overflow: auto; border-radius: 18px; box-shadow: 0 14px 30px -22px rgba(35,66,87,.55); background: #FFFFFF; }
.tabla table { width: 100%; border-collapse: collapse; font-size: .88rem; }
.tabla th { position: sticky; top: 0; background: #234257; color: #FFFFFF !important; text-align: left; padding: .75rem .9rem;
  font-weight: 700; }
.tabla td { padding: .65rem .9rem; color: #293E3F; border-bottom: 1px solid #EEF2F4; }
.tabla tr:nth-child(even) td { background: #F7FAF3; }
.tabla td.num { text-align: right; font-weight: 700; color: #234257; }

/* ---------- línea de tiempo ---------- */
.lt { position: relative; }
.lt-item { display: flex; gap: .9rem; position: relative; padding-bottom: .9rem; }
.lt-item:not(:last-child)::before { content: ""; position: absolute; left: 7px; top: 18px; bottom: 0; width: 2px; background: #E3EAEE; }
.lt-punto { width: 16px; height: 16px; border-radius: 50%; margin-top: .25rem; flex-shrink: 0; box-shadow: 0 0 0 4px #FFFFFF, 0 0 0 5px #E3EAEE; }
.lt-caja { flex: 1; }
.lt-fecha { font-weight: 900; color: #234257; font-size: .9rem; }
.lt-txt { font-size: .86rem; color: #293E3F; margin: .15rem 0 .3rem 0; }
.lt-est { font-size: .72rem; font-weight: 700; padding: .15rem .6rem; border-radius: 999px; }
.lt-est.ok { background: #E3F2DA; color: #2C6B47; } .lt-est.no { background: #FFF1DA; color: #8A5A00; }

/* ---------- tarjetas de material ---------- */
.mat { background: #FFFFFF; border-radius: 22px; padding: 1.1rem .8rem .9rem; text-align: center;
  box-shadow: 0 14px 30px -22px rgba(35,66,87,.55); border: 1px solid rgba(35,66,87,.08); transition: transform .2s ease; }
.mat:hover { transform: translateY(-4px) rotate(-1deg); }
.mat svg { display: block; margin: 0 auto .5rem auto; }
.mat-nom { font-weight: 900; color: #234257; }
.mat-pts { font-size: .75rem; color: #5B818E; }

/* ---------- inicio estilo ONG ---------- */
.video-portada { position: relative; overflow: hidden; border-radius: 30px; margin-bottom: 2rem; min-height: 480px;
  display: flex; align-items: flex-end; box-shadow: 0 30px 60px -30px rgba(35,66,87,.7); }
.video-portada video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.video-portada .velo { position: absolute; inset: 0; background: linear-gradient(0deg, rgba(35,66,87,.92) 10%, rgba(35,66,87,.15) 70%); }
.video-portada .contenido { position: relative; padding: 2.6rem; max-width: 46rem; }
.video-portada h1 .resalte { font-style: normal; background: linear-gradient(90deg, #BFD37A, #6DBE45); -webkit-background-clip: text; background-clip: text; color: transparent; }
.video-portada h1 { color: #FFFFFF !important; font-size: 3.2rem; line-height: 1.05; margin: .4rem 0 0 0; }
.video-portada p { color: #E6F0D0 !important; font-size: 1.1rem; }
.eyebrow-vid { display: inline-block; color: #234257; background: #BFD37A; font-weight: 900; letter-spacing: .14em; text-transform: uppercase; font-size: .7rem; padding: .35rem .8rem; border-radius: 999px; }
.historia { display: grid; grid-template-columns: 1fr 1.3fr; gap: 2rem; align-items: center; background: #FFFFFF;
  border-radius: 30px; padding: 2rem; box-shadow: 0 20px 44px -26px rgba(35,66,87,.55); animation: subir .7s ease both; }
.historia .foto { border-radius: 24px; overflow: hidden; background: radial-gradient(circle at 50% 30%, #E7F1D2, #BFD37A 60%, #89B2AE);
  display: flex; justify-content: center; align-items: flex-end; height: 320px; }
.historia .foto img { width: 85% !important; }
.historia blockquote { margin: 0; font-size: 1.25rem; line-height: 1.5; color: #234257; font-weight: 600; border: none; padding: 0; }
.historia .firma { margin-top: 1rem; color: #5B818E; font-size: .88rem; }
.historia p { line-height: 1.7; }
.cifra { text-align: center; padding: 1.4rem .8rem; }
.cifra .n { font-size: 2.8rem; font-weight: 900; color: #FFFFFF; line-height: 1; }
.cifra .t { color: #D0E6A6; font-size: .9rem; margin-top: .4rem; }
.franja { background: linear-gradient(120deg, #234257, #3E8E63); border-radius: 28px; padding: 1rem 1.2rem; margin: 1rem 0 2rem 0;
  display: grid; grid-template-columns: repeat(4, 1fr); box-shadow: 0 24px 50px -28px rgba(35,66,87,.8); }
.valor { display: flex; gap: .9rem; align-items: flex-start; }
.valor .ic { width: 3rem; height: 3rem; border-radius: 16px; display: flex; align-items: center; justify-content: center;
  background: #234257; color: #BFD37A; font-weight: 900; font-size: 1.2rem; flex-shrink: 0; }
.actor { background: #FFFFFF; border-radius: 18px; padding: 1rem 1.1rem; border-left: 6px solid #3E8E63; height: 100%;
  box-shadow: 0 12px 26px -20px rgba(35,66,87,.55); }
.actor.estado { border-left-color: #234257; } .actor.academia { border-left-color: #F2A541; }
.actor .tipo { font-size: .7rem; font-weight: 900; letter-spacing: .12em; text-transform: uppercase; color: #5B818E; }
.actor .nom { font-weight: 900; color: #234257; margin: .2rem 0; }
.actor .txt { font-size: .85rem; color: #293E3F; line-height: 1.5; }
.pasos-guia { display: grid; grid-template-columns: repeat(4, 1fr); gap: .9rem; margin-bottom: 1.4rem; }
.pasos-guia .p { background: #FFFFFF; border-radius: 18px; padding: 1rem; box-shadow: 0 12px 26px -20px rgba(35,66,87,.55); }
.pasos-guia .p b { display: block; color: #234257; font-weight: 900; margin: .4rem 0 .2rem 0; }
.pasos-guia .p span { font-size: .84rem; }
.pasos-guia .n { display: inline-flex; width: 2rem; height: 2rem; border-radius: 50%; background: #F2A541; color: #234257;
  align-items: center; justify-content: center; font-weight: 900; }
</style>
""".replace("__RUIDO__", RUIDO).replace("__PATRON__", "data:image/svg+xml;base64," + base64.b64encode((ASSETS / "patron.svg").read_bytes()).decode())


def aplicar() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def _b64(nombre: str) -> str:
    return base64.b64encode((ASSETS / nombre).read_bytes()).decode()


def imagen(nombre: str, alt: str, ancho: str = "100%", radio: str = "22px") -> str:
    """Una imagen de assets/ incrustada en HTML, para que cargue sin servidor de archivos."""
    tipo = {"svg": "svg+xml", "png": "png"}.get(nombre.rsplit(".", 1)[-1], "jpeg")
    return (f'<img src="data:image/{tipo};base64,{_b64(nombre)}" alt="{alt}" '
            f'style="width:{ancho};border-radius:{radio};display:block">')


def portada(eyebrow: str, titulo: str, texto: str, personaje: bool = False) -> None:
    """Encabezado de sección con degradado y, si se pide, Vera y Don Ciclo."""
    img = ""
    if personaje:
        img = (f'<div class="ilustracion">{imagen("personajes.jpg", "Don Ciclo y Vera, vecinos guía de ReciclaGov", radio="0")}'
               f'</div>')
    st.markdown(f"""<div class="portada"><div><div class="eyebrow">{eyebrow}</div>
        <h1>{titulo}</h1><p>{texto}</p></div>{img}</div>""", unsafe_allow_html=True)


def seccion(kicker: str, titulo: str) -> None:
    st.markdown(f'<div class="seccion"><div class="kicker">{kicker}</div><h2>{titulo}</h2></div>',
                unsafe_allow_html=True)


def tarjeta(titulo: str, texto: str, numero: str = "", paso: str = "") -> str:
    cabeza = f'<div class="paso">{paso}</div>' if paso else (f'<div class="num">{numero}</div>' if numero else "")
    return f'<div class="tarjeta">{cabeza}<div class="tit">{titulo}</div><div class="txt">{texto}</div></div>'


def fila_tarjetas(tarjetas: list[str]) -> None:
    cols = st.columns(len(tarjetas))
    for c, t in zip(cols, tarjetas):
        c.markdown(t, unsafe_allow_html=True)


def pie() -> None:
    st.markdown('<div class="pie">ReciclaGov · Proyecto final de la Diplomatura de Ciencia de Datos, Q-Lab PUCP · '
                'Datos de viviendas sintéticos · Vera y Don Ciclo, personajes diseñados por Ana Karen Zamalloa</div>',
                unsafe_allow_html=True)


def cinta(datos: list[str]) -> None:
    """Cinta de datos que se desplaza sola (se duplica para que el bucle no tenga cortes)."""
    items = "".join(f"<span>{d}</span>" for d in datos)
    st.markdown(f'<div class="cinta"><div class="pista">{items}{items}</div></div>', unsafe_allow_html=True)


def guia(personaje: str, mensaje: str, destino: str = "asistente") -> None:
    """Personaje flotante que guía al vecino y lo lleva al chat."""
    nombre = {"vera": "Vera", "ciclo": "Don Ciclo"}[personaje]
    st.markdown(f'''<a class="guia" href="/{destino}" target="_self" aria-label="Hablar con {nombre}">
        <div class="globo"><b>{nombre}</b>{mensaje}</div>
        <div class="cara">{imagen(personaje + ".png", nombre, radio="0")}</div></a>''', unsafe_allow_html=True)


def chat(mensajes: list[tuple[str, str, list[str]]]) -> None:
    """Conversación con burbujas al estilo de los mensajes del celular."""
    mini = f'<div class="mini">{imagen("vera.png", "Vera", radio="0")}</div>'
    filas = ['<div class="hora">Hoy · Vera, asistente de ReciclaGov</div>']
    if not mensajes:
        filas.append('<div class="vacio">Escríbele a Vera o toca una de las preguntas frecuentes.</div>')
    for rol, texto, fuentes in mensajes:
        if rol == "user":
            filas.append(f'<div class="fila yo"><div class="burbuja">{texto}</div></div>')
        else:
            filas.append(f'<div class="fila ella">{mini}<div class="burbuja">{texto}</div></div>')
            if fuentes:
                filas.append(f'<div class="fuente">Según la guía, {", ".join(fuentes).lower()}</div>')
    st.markdown(f'<div class="chat">{"".join(filas)}</div>', unsafe_allow_html=True)


def retrato(personaje: str, alt: str) -> None:
    """El personaje centrado sobre un círculo de luz verde, sin fondo plomo."""
    st.markdown(f'<div class="retrato">{imagen(personaje + ".png", alt, radio="0")}</div>', unsafe_allow_html=True)


def qr(texto: str) -> str:
    """Código QR del ticket digital, como imagen PNG en base64."""
    import io
    import qrcode
    img = qrcode.QRCode(box_size=8, border=2)
    img.add_data(texto)
    img.make(fit=True)
    buf = io.BytesIO()
    img.make_image(fill_color="#234257", back_color="white").save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def ticket(codigo: str, detalle: str, validado: bool = False) -> None:
    estado = '<span class="estado ok">Validado</span>' if validado else '<span class="estado">Pendiente de recojo</span>'
    st.markdown(f'''<div class="ticket"><img src="data:image/png;base64,{qr(codigo)}" alt="Código QR del ticket {codigo}">
        <div>{estado}<div class="codigo">{codigo}</div>{detalle}</div></div>''', unsafe_allow_html=True)


def logo() -> str:
    return (f'<div class="marca-logo">{imagen("logo.svg", "Logo de ReciclaGov", "40px", "0")}'
            f'<span class="nombre">Recicla<b>Gov</b></span></div>')


def video_portada(eyebrow: str, titulo: str, texto: str) -> bool:
    """Portada con video de fondo (app/static/portada.mp4), servido como archivo estático de Streamlit."""
    if not (ASSETS.parent / "static" / "portada.mp4").exists():
        return False
    st.markdown(f'''<div class="video-portada"><video autoplay muted loop playsinline poster="app/static/portada.jpg">
        <source src="app/static/portada.mp4" type="video/mp4"></video><div class="velo"></div>
        <div class="contenido"><span class="eyebrow-vid">{eyebrow}</span><h1>{titulo}</h1>
        <p>{texto}</p></div></div>''', unsafe_allow_html=True)
    return True
