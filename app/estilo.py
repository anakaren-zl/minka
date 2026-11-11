"""Identidad visual de Minka: paleta, tipografía, fondo animado y componentes reutilizables.

Paleta solo de verdes, del verde menta al verde pino, con el pino oscuro para textos y botones, de
modo que todo tenga contraste suficiente. Detrás de la página flotan dibujos ecológicos que se mueven
despacio. Montserrat en todos los textos, con Black para los títulos. Los personajes Vera y Don
Ciclo son diseño de la autora.
"""
import base64
from pathlib import Path

import streamlit as st

PALETA = {
    "menta": "#E7F1D2",   # fondos suaves de bloques
    "brote": "#D0E6A6",   # resaltados suaves
    "hoja": "#BFD37A",    # bordes y acentos claros
    "chispa": "#6DBE45",  # verde vivo para botones y logros
    "musgo": "#3E8E63",   # verde medio
    "salvia": "#4E7A5C",  # textos secundarios
    "pino": "#1E4D3A",    # títulos, textos y bloques oscuros (contraste alto)
    "bosque": "#24372C",  # degradados oscuros
}
ASSETS = Path(__file__).resolve().parent / "assets"
LEMA = "Juntos, cada aporte cuenta"

# Textura de papel muy suave, hecha con ruido SVG (no requiere descargar imágenes)
RUIDO = ("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'>"
         "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/>"
         "<feColorMatrix values='0 0 0 0 0.16 0 0 0 0 0.24 0 0 0 0 0.25 0 0 0 .07 0'/></filter>"
         "<rect width='100%' height='100%' filter='url(%23n)'/></svg>")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;900&display=swap');

/* ---------- base ---------- */
.stApp {
  background-color: #F5F8EE;
  background-image:
    radial-gradient(1100px 520px at 8% -8%, rgba(191,211,122,.38), transparent 60%),
    radial-gradient(900px 520px at 105% 4%, rgba(140,192,132,.34), transparent 60%),
    radial-gradient(800px 600px at 50% 120%, rgba(208,230,166,.45), transparent 60%),
    url("__RUIDO__");
  background-attachment: fixed; }
/* dibujos ecológicos flotando detrás de todo */
.stApp::before { content: ""; position: fixed; inset: -300px; z-index: 0; pointer-events: none;
  background-image: url("__PATRON__"); background-size: 300px 300px; opacity: .13;
  animation: deriva 90s linear infinite; }
.stApp::after { content: ""; position: fixed; inset: 0; z-index: 0; pointer-events: none;
  background: radial-gradient(600px 400px at var(--x, 80%) 20%, rgba(109,190,69,.18), transparent 70%);
  animation: respira 14s ease-in-out infinite alternate; }
[data-testid="stAppViewContainer"] > *, [data-testid="stMain"] { position: relative; z-index: 1; }
@keyframes deriva { from { transform: translate(0, 0); } to { transform: translate(300px, 300px); } }
@keyframes respira { from { --x: 75%; opacity: .7; } to { --x: 25%; opacity: 1; } }
header[data-testid="stHeader"] { display: none; }
.stApp, .stApp *:not([data-testid="stIconMaterial"]):not(.material-symbols-rounded):not(code):not(pre) {
  font-family: 'Montserrat', sans-serif !important; }
.stApp p, .stApp li, .stApp label, .stApp td { color: #1E4D3A; }
h1, h2, h3, h4, h5 { color: #1E4D3A !important; font-weight: 900 !important; letter-spacing: -0.02em; }
.block-container { padding-top: 6.6rem; max-width: 1220px; }
[data-testid="stWidgetLabel"] p { font-weight: 600 !important; color: #1E4D3A !important; }
a { color: #3E7A55; font-weight: 600; }
@keyframes subir { from { opacity: 0; transform: translateY(18px); } to { opacity: 1; transform: none; } }
@keyframes flotar { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }

/* ---------- barra de navegación ---------- */
.st-key-barra { position: fixed; top: 0; left: 0; right: 0; z-index: 1000; padding: .5rem 2rem;
  background: rgba(245,248,238,.88); backdrop-filter: blur(16px); border-bottom: 2px solid #E7F1D2; box-shadow: 0 8px 24px -18px rgba(30,77,58,.55); }
.st-key-barra [data-testid="stHorizontalBlock"] { align-items: center !important; gap: .25rem; flex-wrap: nowrap; }
.st-key-barra [data-testid="stHorizontalBlock"] { justify-content: space-between; }
.st-key-barra [data-testid="stColumn"] { display: flex; align-items: center; justify-content: center;
  flex: 0 1 auto !important; width: auto !important; min-width: max-content !important; }
.st-key-barra [data-testid="stPageLink"] p, .st-key-barra [data-testid="stPageLink"] a { overflow: visible !important;
  text-overflow: clip !important; max-width: none !important; }
.st-key-barra [data-testid="stColumn"]:first-child { justify-content: flex-start; }
.st-key-barra [data-testid="stColumn"] > div { width: 100%; }
.st-key-barra [data-testid="stElementContainer"], .st-key-barra [data-testid="stMarkdownContainer"] { margin: 0 !important; }
.st-key-barra [data-testid="stVerticalBlock"] { gap: 0 !important; justify-content: center; }
.st-key-barra [data-testid="stPageLink"] { display: flex; justify-content: center; }
.st-key-barra [data-testid="stPageLink"] a { border-radius: 999px; padding: .45rem .75rem; justify-content: center;
  margin: 0; min-height: 2.5rem; align-items: center; }
.st-key-barra [data-testid="stPageLink"] a:hover { background: #E7F1D2; }
.st-key-barra [data-testid="stPageLink"] p { font-weight: 600; font-size: .86rem; white-space: nowrap; margin: 0;
  color: #1E4D3A !important; line-height: 1; }
.st-key-barra [data-testid="stPageLink"] a[aria-current="page"] { background: #E7F1D2; }
.st-key-barra [data-testid="stPageLink"] a[aria-current="page"] p { font-weight: 900; }
.st-key-nav-vera [data-testid="stPageLink"] a { border: 2px solid #6DBE45; background: #FFFFFF; }
.st-key-nav-vera [data-testid="stPageLink"] p { font-weight: 900 !important; }
.st-key-nav-recicla [data-testid="stPageLink"] a, .st-key-cta-recicla [data-testid="stPageLink"] a {
  background: #6DBE45; box-shadow: 0 8px 18px -10px rgba(30,77,58,.7); }
.st-key-nav-recicla [data-testid="stPageLink"] a:hover, .st-key-cta-recicla [data-testid="stPageLink"] a:hover { background: #BFD37A; }
.st-key-nav-recicla [data-testid="stPageLink"] p, .st-key-cta-recicla [data-testid="stPageLink"] p,
.st-key-nav-recicla [data-testid="stPageLink"] span, .st-key-cta-recicla [data-testid="stPageLink"] span {
  color: #1E4D3A !important; font-weight: 900 !important; }
.st-key-cta-muni [data-testid="stPageLink"] a { background: #FFFFFF; border: 2px solid #1E4D3A; }
.st-key-cta-muni [data-testid="stPageLink"] p { font-weight: 900 !important; }
.st-key-cta-recicla [data-testid="stPageLink"] a, .st-key-cta-muni [data-testid="stPageLink"] a {
  border-radius: 999px; padding: .8rem 1.4rem; justify-content: center; }

/* ---------- logo ---------- */
.marca-logo { display: flex; align-items: center; }
.marca-logo .nombre { font-weight: 900; font-size: 1.75rem; color: #1E4D3A; letter-spacing: -.045em; line-height: .95; }
.marca-logo .nombre b { color: #3E8E63; font-weight: 900; }
.marca-logo .lema { font-weight: 500; font-size: .66rem; color: #3E7A55; letter-spacing: .02em; margin-top: .2rem;
  white-space: nowrap; }

/* ---------- portada de cada sección ---------- */
.portada { position: relative; overflow: hidden; border-radius: 28px; padding: 2.5rem 2.8rem; margin-bottom: 1.6rem;
  background-color: #1E4D3A; background-size: cover; background-position: center; box-shadow: 0 24px 50px -28px rgba(30,77,58,.8);
  animation: subir .6s ease both; }
.portada > div { position: relative; z-index: 1; max-width: 48rem; }
.portada h1 { color: #FFFFFF !important; font-size: 2.7rem; margin: 0; line-height: 1.08; }
.portada h1 .resalte { font-style: normal; background: linear-gradient(90deg, #BFD37A, #6DBE45, #D0E6A6);
  -webkit-background-clip: text; background-clip: text; color: transparent; }
.portada p { color: #FFFFFF !important; font-size: 1.05rem; line-height: 1.6; margin: .9rem 0 0 0; opacity: .92; }
.eyebrow { display: inline-block; color: #1E4D3A; background: #BFD37A; font-weight: 900; letter-spacing: .14em;
  text-transform: uppercase; font-size: .7rem; padding: .35rem .85rem; border-radius: 999px; margin-bottom: .9rem; }

/* ---------- títulos de bloque ---------- */
.seccion { margin: 2.6rem 0 1rem 0; }
.seccion .kicker { color: #3E7A55; font-weight: 900; letter-spacing: .16em; text-transform: uppercase; font-size: .72rem; }
.seccion h2 { margin: .2rem 0 0 0 !important; font-size: 2rem; }
.seccion .intro { margin: .5rem 0 0 0; font-size: 1rem; line-height: 1.6; max-width: 52rem; }

/* ---------- tarjetas con contraste ---------- */
.tarjeta { background: #FFFFFF; border: 2px solid #BFD37A; border-radius: 22px; padding: 1.4rem 1.4rem 1.3rem;
  height: 100%; box-shadow: 0 14px 30px -20px rgba(30,77,58,.55); animation: subir .6s ease both;
  transition: transform .2s ease, border-color .2s ease; }
.tarjeta:hover { transform: translateY(-4px); border-color: #6DBE45; }
.tarjeta .num { font-weight: 900; font-size: 2.4rem; color: #1E4D3A; line-height: 1; letter-spacing: -.02em; }
.tarjeta .unidad { font-weight: 700; color: #3E7A55; font-size: .85rem; margin-top: .3rem; }
.tarjeta .tit { font-weight: 900; color: #1E4D3A; font-size: 1.08rem; margin: .7rem 0 .35rem 0; }
.tarjeta .txt { font-size: .93rem; color: #1E4D3A; line-height: 1.6; }
.paso { display: inline-flex; align-items: center; justify-content: center; width: 2.4rem; height: 2.4rem;
  border-radius: 50%; background: #6DBE45; color: #1E4D3A; font-weight: 900; }
.etiqueta { display: inline-block; padding: .3rem .85rem; border-radius: 999px; font-size: .78rem; font-weight: 700;
  background: #1E4D3A; color: #FFFFFF; margin: 0 .35rem .45rem 0; }
.etiqueta.clara { background: #FFFFFF; color: #1E4D3A; border: 2px solid #6DBE45; }
.etiqueta.sol { background: #D0E6A6; color: #1E4D3A; }
.banda { background: #FFFFFF; border-radius: 18px; padding: 1.1rem 1.4rem; color: #1E4D3A; font-weight: 500;
  font-size: 1.02rem; margin: .8rem 0 1.2rem 0; border-left: 8px solid #6DBE45;
  box-shadow: 0 12px 26px -20px rgba(30,77,58,.6); }
.banda b { font-weight: 900; }
.nota { color: #3E7A55 !important; font-size: .85rem; line-height: 1.5; margin-top: .8rem; }
.pie { text-align: center; color: #3E7A55; font-size: .8rem; margin-top: 3.5rem; padding-top: 1.4rem;
  border-top: 2px solid #E7F1D2; }

/* ---------- guía de uso de cada sección ---------- */
.como { background: #E7F1D2; border-radius: 22px; padding: 1.2rem 1.3rem; margin: 0 0 1.6rem 0; }
.como .t { font-weight: 900; color: #1E4D3A; font-size: .78rem; letter-spacing: .14em; text-transform: uppercase;
  margin-bottom: .8rem; }
.como .grid { display: grid; gap: .8rem; }
.como .p { background: #FFFFFF; border-radius: 16px; padding: .9rem 1rem; display: flex; gap: .75rem; align-items: flex-start; }
.como .n { flex-shrink: 0; width: 2rem; height: 2rem; border-radius: 50%; background: #6DBE45; color: #1E4D3A;
  display: flex; align-items: center; justify-content: center; font-weight: 900; }
.como b { display: block; color: #1E4D3A; font-weight: 900; font-size: .92rem; }
.como span { font-size: .84rem; color: #1E4D3A; line-height: 1.45; }

/* ---------- métricas explicadas ---------- */
.metrica { background: #FFFFFF; border: 2px solid #BFD37A; border-radius: 20px; padding: 1.1rem 1.2rem; height: 100%;
  box-shadow: 0 12px 26px -20px rgba(30,77,58,.55); }
.metrica .et { font-size: .8rem; font-weight: 700; color: #3E7A55; text-transform: uppercase; letter-spacing: .06em; }
.metrica .v { font-size: 2rem; font-weight: 900; color: #1E4D3A; line-height: 1.15; margin: .25rem 0; }
.metrica .ex { font-size: .82rem; color: #1E4D3A; line-height: 1.45; }
.metrica.ok { border-color: #6DBE45; background: #F4F9EA; }
div[data-testid="stMetric"] { background: #FFFFFF; border: 2px solid #BFD37A; border-radius: 20px; padding: 1rem 1.2rem;
  box-shadow: 0 12px 26px -20px rgba(30,77,58,.55); }
div[data-testid="stMetricValue"] { font-weight: 900; color: #1E4D3A; }

/* ---------- controles ---------- */
.stButton > button, .stDownloadButton > button, .stLinkButton > a { border-radius: 14px !important; font-weight: 600 !important;
  border: 2px solid #BFD37A !important; background: #FFFFFF !important; color: #1E4D3A !important; }
.stButton > button:hover, .stLinkButton > a:hover { border-color: #6DBE45 !important; }
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"], .stFormSubmitButton > button {
  background: #1E4D3A !important; color: #FFFFFF !important; border: none !important;
  box-shadow: 0 10px 20px -12px rgba(30,77,58,.9); }
.stButton > button[kind="primary"] *, .stDownloadButton > button[kind="primary"] *, .stFormSubmitButton > button * { color: #FFFFFF !important; }
.stButton > button[kind="primary"]:hover, .stFormSubmitButton > button:hover { background: #3E7A55 !important; }
.stTextInput input, .stTextArea textarea, .stDateInput input, .stNumberInput input {
  border-radius: 12px !important; background: #FFFFFF !important; color: #1E4D3A !important; }
[data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="base-input"] { border-radius: 12px !important;
  border-color: #BFD37A !important; background: #FFFFFF !important; }
[data-testid="stForm"] { background: #FFFFFF; border: 2px solid #BFD37A; border-radius: 22px; padding: 1.4rem; }
iframe { border-radius: 20px; }

/* opciones como botones (sin desplegables) */
[data-testid="stPills"] button, [data-testid="stButtonGroup"] button {
  background: #FFFFFF !important; border: 2px solid #BFD37A !important; color: #1E4D3A !important;
  border-radius: 999px !important; font-weight: 600 !important; }
[data-testid="stPills"] button[kind*="Active"], [data-testid="stButtonGroup"] button[kind*="Active"],
[data-testid="stPills"] button[aria-checked="true"], [data-testid="stButtonGroup"] button[aria-checked="true"] {
  background: #1E4D3A !important; border-color: #1E4D3A !important; }
[data-testid="stPills"] button[kind*="Active"] *, [data-testid="stButtonGroup"] button[kind*="Active"] *,
[data-testid="stPills"] button[aria-checked="true"] *, [data-testid="stButtonGroup"] button[aria-checked="true"] * {
  color: #FFFFFF !important; }

/* pestañas como interruptor redondeado */
.stTabs [role="tablist"], .stTabs div:has(> [data-testid="stTab"]) { gap: .3rem !important; background: #E7F1D2;
  padding: .35rem !important; border-radius: 999px; width: fit-content !important; max-width: 100%;
  margin-bottom: 1rem; border: none !important; box-shadow: none !important; }
.stTabs div:has(> div > [data-testid="stTab"]) { border: none !important; box-shadow: none !important; }
.stTabs div:has(> [data-testid="stTab"]) > div:not([data-testid="stTab"]) { display: none !important; }
.stTabs [data-testid="stTab"] { background: transparent !important; border: none !important; border-radius: 999px !important;
  padding: .55rem 1.3rem !important; height: auto !important; margin: 0 !important; cursor: pointer; }
.stTabs [data-testid="stTab"]::after, .stTabs [data-testid="stTab"]::before { display: none !important; }
.stTabs [data-testid="stTab"] p { font-weight: 600 !important; color: #1E4D3A !important; font-size: .92rem; margin: 0; }
.stTabs [data-testid="stTab"][aria-selected="true"] { background: #FFFFFF !important;
  box-shadow: 0 6px 14px -8px rgba(30,77,58,.6); }
.stTabs [data-testid="stTab"][aria-selected="true"] p { font-weight: 900 !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ---------- ticket digital ---------- */
.ticket { display: flex; gap: 1.6rem; align-items: center; background: #FFFFFF; border-radius: 26px; padding: 1.6rem;
  border: 3px dashed #6DBE45; box-shadow: 0 22px 46px -24px rgba(30,77,58,.55); animation: subir .5s ease both; }
.ticket img { width: 170px; border-radius: 14px; }
.ticket .codigo { font-weight: 900; font-size: 2.2rem; color: #1E4D3A; letter-spacing: .04em; }
.ticket .estado { display: inline-block; background: #BFD37A; color: #1E4D3A; border-radius: 999px; padding: .2rem .8rem;
  font-size: .78rem; font-weight: 700; }
.ticket .estado.ok { background: #6DBE45; color: #1E4D3A; }
.ticket p { margin: .35rem 0 0 0; font-size: .92rem; }

/* ---------- personaje guía ---------- */
.retrato { display: flex; justify-content: center; align-items: flex-end; height: 280px; border-radius: 28px; overflow: hidden;
  background: radial-gradient(circle at 50% 35%, #FFFFFF 0%, #E7F1D2 45%, #BFD37A 100%); }
.retrato img { width: 80% !important; margin: 0 auto; animation: flotar 6s ease-in-out infinite; }
.guia { position: fixed; right: 26px; bottom: 26px; z-index: 999; display: flex; align-items: flex-end; gap: .7rem;
  animation: subir .8s ease 1s both; text-decoration: none !important; }
.guia .globo { max-width: 270px; background: #FFFFFF; color: #1E4D3A; border-radius: 20px 20px 6px 20px; padding: .85rem 1rem;
  font-size: .88rem; line-height: 1.45; font-weight: 500; box-shadow: 0 16px 34px -14px rgba(30,77,58,.55);
  border: 2px solid #6DBE45; }
.guia .globo b { font-weight: 900; display: block; margin-bottom: .15rem; color: #3E7A55; }
.guia .cara { width: 88px; height: 88px; border-radius: 50%; overflow: hidden; flex-shrink: 0; border: 4px solid #FFFFFF;
  box-shadow: 0 0 0 4px #6DBE45, 0 16px 30px -12px rgba(30,77,58,.7); animation: flotar 4s ease-in-out infinite;
  background: radial-gradient(circle at 50% 35%, #FFFFFF, #BFD37A); }
.guia .cara img { width: 100%; display: block; }

/* ---------- chat estilo mensajes del celular ---------- */
.chat { display: flex; flex-direction: column; gap: .45rem; padding: 1.2rem; min-height: 360px; background: #FFFFFF;
  border-radius: 26px; border: 2px solid #BFD37A; box-shadow: 0 18px 40px -24px rgba(30,77,58,.5); }
.chat .hora { text-align: center; color: #3E7A55; font-size: .72rem; font-weight: 600; margin: .2rem 0 .6rem; }
.chat .fila { display: flex; align-items: flex-end; gap: .45rem; animation: subir .3s ease both; }
.chat .fila.yo { justify-content: flex-end; }
.chat .mini { width: 34px; height: 34px; border-radius: 50%; overflow: hidden; flex-shrink: 0;
  background: radial-gradient(circle at 50% 35%, #FFFFFF, #BFD37A); }
.chat .mini img { width: 100%; }
.chat .burbuja { max-width: 72%; padding: .62rem .95rem; font-size: .95rem; line-height: 1.45; border-radius: 20px; }
.chat .ella .burbuja { background: #E9E9EB; color: #1C1C1E; border-bottom-left-radius: 6px; }
.chat .yo .burbuja { background: #1E4D3A; color: #FFFFFF; border-bottom-right-radius: 6px; }
.chat .fuente { font-size: .7rem; color: #3E7A55; margin: -.1rem 0 .3rem 2.4rem; }
.chat .vacio { margin: auto; text-align: center; color: #3E7A55; }
[data-testid="stChatInput"] { border-radius: 999px !important; border: 2px solid #6DBE45 !important; background: #FFFFFF !important; }

/* ---------- paneles, barras, ranking, tablas ---------- */
.panel { background: #FFFFFF; border-radius: 22px; padding: 1.3rem 1.4rem; border: 2px solid #E7F1D2;
  box-shadow: 0 16px 34px -24px rgba(30,77,58,.6); animation: subir .5s ease both; }
.barra { margin: .2rem 0 1rem 0; }
.barra-top { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: .35rem; gap: 1rem; }
.barra-etq { font-weight: 700; color: #1E4D3A; font-size: .95rem; }
.barra-val { font-weight: 900; color: #1E4D3A; font-size: .95rem; white-space: nowrap; }
.barra-pista { background: #E7F1D2; border-radius: 999px; height: 14px; overflow: hidden; flex: 1; }
.barra-pista.grande { height: 26px; }
.barra-relleno { height: 100%; border-radius: 999px; animation: crecer 1s cubic-bezier(.2,.8,.2,1) both; }
@keyframes crecer { from { width: 0 !important; } }
.barra-det { font-size: .8rem; color: #3E7A55; margin-top: .25rem; }
.rk { display: flex; gap: .9rem; align-items: center; margin-bottom: .9rem; }
.rk-pos { width: 2.3rem; height: 2.3rem; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-weight: 900; flex-shrink: 0; }
.rk-cuerpo { flex: 1; }
.cmp-fila { display: flex; align-items: center; gap: .9rem; margin: .6rem 0; }
.cmp-etq { width: 110px; font-weight: 700; color: #1E4D3A; }
.cmp-val { width: 70px; text-align: right; font-weight: 900; color: #1E4D3A; }
.cmp-msg { margin-top: .8rem; padding: .7rem 1rem; background: #EEF6E0; border-radius: 14px; color: #1E4D3A; font-weight: 600; }
.vacio-panel { color: #3E7A55; text-align: center; }
.tabla { overflow: auto; border-radius: 18px; border: 2px solid #E7F1D2; background: #FFFFFF;
  box-shadow: 0 14px 30px -24px rgba(30,77,58,.6); }
.tabla table { width: 100%; border-collapse: collapse; font-size: .9rem; }
.tabla th { position: sticky; top: 0; background: #1E4D3A; color: #FFFFFF !important; text-align: left; padding: .8rem .95rem;
  font-weight: 700; }
.tabla td { padding: .7rem .95rem; color: #1E4D3A; border-bottom: 1px solid #E7F1D2; }
.tabla tr:nth-child(even) td { background: #F7FAF3; }
.tabla td.num { text-align: right; font-weight: 700; }
.lt-item { display: flex; gap: .9rem; position: relative; padding-bottom: .9rem; }
.lt-item:not(:last-child)::before { content: ""; position: absolute; left: 7px; top: 18px; bottom: 0; width: 2px; background: #E7F1D2; }
.lt-punto { width: 16px; height: 16px; border-radius: 50%; margin-top: .25rem; flex-shrink: 0; box-shadow: 0 0 0 4px #FFFFFF, 0 0 0 5px #E7F1D2; }
.lt-caja { flex: 1; }
.lt-fecha { font-weight: 900; color: #1E4D3A; font-size: .9rem; }
.lt-txt { font-size: .86rem; color: #1E4D3A; margin: .15rem 0 .3rem 0; }
.lt-est { font-size: .72rem; font-weight: 700; padding: .15rem .6rem; border-radius: 999px; }
.lt-est.ok { background: #E7F1D2; color: #1E4D3A; } .lt-est.no { background: #EEF6E0; color: #2F6B3F; }
.mat { background: #FFFFFF; border-radius: 22px; padding: 1.1rem .8rem .9rem; text-align: center; border: 2px solid #E7F1D2;
  box-shadow: 0 14px 30px -24px rgba(30,77,58,.6); }
.mat svg { display: block; margin: 0 auto .5rem auto; }
.mat-nom { font-weight: 900; color: #1E4D3A; }
.mat-pts { font-size: .78rem; color: #3E7A55; }

/* ---------- inicio ---------- */
.video-portada { position: relative; overflow: hidden; border-radius: 30px; margin-bottom: 1.4rem; min-height: 500px;
  display: flex; align-items: flex-end; box-shadow: 0 30px 60px -30px rgba(30,77,58,.8); }
.video-portada video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.video-portada .velo { position: absolute; inset: 0;
  background: linear-gradient(0deg, rgba(30,77,58,.96) 0%, rgba(30,77,58,.82) 28%, rgba(62,142,99,.35) 62%, rgba(109,190,69,0) 100%); }
.video-portada .contenido { position: relative; padding: 2.6rem; max-width: 50rem; }
.video-portada h1 { color: #FFFFFF !important; font-size: 3.3rem; line-height: 1.04; margin: .5rem 0 0 0; }
.video-portada p { color: #FFFFFF !important; font-size: 1.1rem; line-height: 1.6; }
.video-portada .lema-vid { color: #FFFFFF; font-weight: 500; font-size: 1rem; letter-spacing: .02em; }
.perfil { position: relative; border-radius: 26px; overflow: hidden; height: 350px; display: flex; flex-direction: column;
  justify-content: flex-end; padding: 1.4rem; box-shadow: 0 20px 40px -24px rgba(30,77,58,.75); transition: transform .25s ease; }
.perfil:hover { transform: translateY(-6px); }
.perfil .fig { position: absolute; inset: 0; display: flex; justify-content: center; align-items: flex-start; padding-top: 1.2rem; }
.perfil .fig img { height: 175px !important; width: auto !important; }
.perfil .fig svg { width: 170px; height: 170px; }
.perfil::after { content: ""; position: absolute; inset: 0; background: linear-gradient(0deg, rgba(30,77,58,.97) 0%, rgba(30,77,58,.75) 30%, rgba(30,77,58,0) 50%); }
.perfil .txt { position: relative; z-index: 1; }
.perfil .ptit { color: #FFFFFF !important; font-weight: 900; font-size: 1.55rem !important; margin: 0 !important; padding: 0 !important; line-height: 1.15; }
.perfil span { color: #FFFFFF; font-size: .88rem; display: block; margin-top: .3rem; line-height: 1.4; }
.perfil .ir { display: inline-block; margin-top: .7rem; background: #6DBE45; color: #1E4D3A; font-weight: 900;
  font-size: .8rem; padding: .3rem .8rem; border-radius: 999px; }
[class*="st-key-perfil-"] { position: relative; }
[class*="st-key-perfil-"] [data-testid="stPageLink"] { position: absolute; inset: 0; z-index: 5; }
[class*="st-key-perfil-"] [data-testid="stPageLink"] a { position: absolute; inset: 0; opacity: 0; }
[class*="st-key-perfil-"] [data-testid="stElementContainer"]:has([data-testid="stPageLink"]) { position: absolute; inset: 0; z-index: 5;
  margin: 0; width: 100% !important; height: 100% !important; }
[class*="st-key-perfil-"] [data-testid="stPageLink"], [class*="st-key-perfil-"] [data-testid="stPageLink"] a {
  width: 100% !important; height: 100% !important; max-width: none !important; }
.historia { display: grid; grid-template-columns: .9fr 1.4fr; gap: 2.2rem; align-items: center; background: #FFFFFF;
  border-radius: 30px; padding: 2rem; border: 2px solid #BFD37A; box-shadow: 0 20px 44px -28px rgba(30,77,58,.6); }
.historia figure { margin: 0; }
.historia figure img { width: 100% !important; border-radius: 24px; display: block; }
.historia figcaption { font-size: .75rem; color: #3E7A55; margin-top: .45rem; text-align: center; }
.historia blockquote, .historia blockquote * { color: #1E4D3A !important; opacity: 1 !important; }
.historia blockquote { margin: 0; font-size: 1.12rem; line-height: 1.6; color: #1E4D3A; font-weight: 500; border: none;
  padding: 0 0 0 1.2rem; border-left: 6px solid #6DBE45; }
.historia .firma { margin-top: 1rem; color: #1E4D3A; font-size: .9rem; }
.historia .firma b { font-weight: 900; }
.reflexion { font-size: 1.02rem; line-height: 1.7; margin: 0 !important; padding-top: 2.4rem; max-width: 60rem; }
.idea-fuerza { margin: 1.2rem 0 0 0; background: #1E4D3A; border-radius: 26px; padding: 1.8rem 2rem; position: relative;
  overflow: hidden; box-shadow: 0 22px 44px -26px rgba(30,77,58,.9); }
.idea-fuerza p { position: relative; color: #FFFFFF !important; font-size: 1.28rem; line-height: 1.55; font-weight: 700; margin: 0; }
.idea-fuerza p b { color: #BFD37A; font-weight: 900; }
.mosaico { border-radius: 30px; padding: 3rem 2rem; margin: 1rem 0;
  background: linear-gradient(120deg, #1E4D3A, #3E8E63); box-shadow: 0 24px 50px -28px rgba(30,77,58,.8); }
.mosaico .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.4rem; max-width: 1080px; margin: 0 auto; }
.mosaico .c { background: #FFFFFF; padding: 1.7rem 1.6rem 1.6rem; border-radius: 22px; border-bottom: 10px solid #6DBE45; }
.mosaico .c h3 { font-size: 1.7rem; margin: 0 0 .7rem 0; }
.mosaico .c p { font-size: .98rem; line-height: 1.65; margin: 0; }
.valores { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
.valor { background: #FFFFFF; border-radius: 22px; padding: 1.3rem; border: 2px solid #BFD37A; display: flex; gap: 1rem;
  align-items: flex-start; box-shadow: 0 12px 26px -22px rgba(30,77,58,.6); }
.valor .ic { flex-shrink: 0; width: 3.2rem; height: 3.2rem; border-radius: 16px; display: flex; align-items: center;
  justify-content: center; }
.valor b { display: block; color: #1E4D3A; font-weight: 900; font-size: 1.05rem; margin-bottom: .2rem; }
.valor span { font-size: .9rem; line-height: 1.5; color: #1E4D3A; }
.franja { background: #1E4D3A; border-radius: 28px; padding: 1rem 1.2rem; margin: 1rem 0 .4rem 0;
  display: grid; grid-template-columns: repeat(4, 1fr); box-shadow: 0 24px 50px -28px rgba(30,77,58,.8); }
.cifra { text-align: center; padding: 1.3rem .8rem; }
.cifra .n { font-size: 2.6rem; font-weight: 900; color: #BFD37A; line-height: 1; }
.cifra .t { color: #FFFFFF; font-size: .9rem; margin-top: .45rem; }
.actor { background: #FFFFFF; border-radius: 18px; padding: 1rem 1.1rem; border: 2px solid #E7F1D2; border-left: 8px solid #6DBE45;
  height: 100%; box-shadow: 0 12px 26px -22px rgba(30,77,58,.6); }
.actor.estado { border-left-color: #1E4D3A; } .actor.academia { border-left-color: #6DBE45; }
.actor .tipo { font-size: .7rem; font-weight: 900; letter-spacing: .12em; text-transform: uppercase; color: #3E7A55; }
.actor .nom { font-weight: 900; color: #1E4D3A; margin: .2rem 0; }
.actor .txt { font-size: .86rem; color: #1E4D3A; line-height: 1.5; }
.founder { display: grid; grid-template-columns: 180px 1fr; gap: 1.6rem; align-items: center; background: #FFFFFF;
  border-radius: 26px; padding: 1.5rem; border: 2px solid #BFD37A; }
.founder img { width: 180px !important; border-radius: 50%; border: 6px solid #E7F1D2; }
.founder h3 { margin: 0 0 .4rem 0; }
.founder p { margin: .3rem 0; line-height: 1.6; }
.founder p.rol { font-size: .88rem; font-style: italic; color: #4E7A5C !important; }
.noticia { background: #FFFFFF; border-radius: 22px; overflow: hidden; border: 2px solid #BFD37A; height: 100%;
  box-shadow: 0 14px 30px -22px rgba(30,77,58,.6); display: flex; flex-direction: column; }
.noticia .img { height: 130px; display: flex; align-items: center; justify-content: center; }
.noticia .cuerpo { padding: 1.1rem 1.2rem 1.2rem; }
.noticia .medio { font-size: .72rem; font-weight: 900; letter-spacing: .1em; text-transform: uppercase; color: #3E7A55; }
.noticia .tit { font-weight: 900; color: #1E4D3A; margin: .35rem 0; line-height: 1.35; }
.noticia .txt { font-size: .86rem; line-height: 1.5; color: #1E4D3A !important; font-weight: 500 !important; }
.noticia .tit { color: #1E4D3A !important; }
.identidad { display: flex; gap: .9rem; align-items: center; background: #FFFFFF; border: 2px solid #6DBE45; border-radius: 18px;
  padding: .8rem 1rem; margin: .4rem 0 1rem 0; }
.identidad .av { width: 52px; height: 52px; border-radius: 50%; overflow: hidden; flex-shrink: 0;
  background: radial-gradient(circle at 50% 35%, #FFFFFF, #BFD37A); }
.identidad .av img { width: 100%; }
.identidad b { color: #1E4D3A; font-weight: 900; display: block; }
.identidad span { font-size: .85rem; color: #3E7A55; }

/* ---------- planes ---------- */
.planes { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.2rem; align-items: stretch; }
.plan { background: #FFFFFF; border: 2px solid #BFD37A; border-radius: 26px; padding: 1.6rem 1.5rem; display: flex;
  flex-direction: column; box-shadow: 0 18px 40px -28px rgba(30,77,58,.7); position: relative; }
.plan.top { border: 3px solid #3E8E63; transform: translateY(-6px); }
.plan .cinta-plan { position: absolute; top: -14px; left: 1.5rem; background: #3E8E63; color: #FFFFFF; font-weight: 900;
  font-size: .72rem; letter-spacing: .08em; text-transform: uppercase; padding: .3rem .8rem; border-radius: 999px; }
.plan .para { font-size: .74rem; font-weight: 900; letter-spacing: .12em; text-transform: uppercase; color: #4E7A5C; }
.plan .nom { font-size: 1.5rem; font-weight: 900; color: #1E4D3A; margin: .2rem 0 .4rem 0; }
.plan .precio { font-size: 2.4rem; font-weight: 900; color: #1E4D3A; line-height: 1.05; margin-top: .5rem; }
.plan .precio small { font-size: .95rem; font-weight: 600; color: #4E7A5C; }
.plan .nota-precio { font-size: .82rem; color: #4E7A5C; margin: .3rem 0 .9rem 0; min-height: 2.4em; }
.plan .desc { font-size: .9rem; line-height: 1.5; margin-bottom: .9rem; }
.plan ul { list-style: none; padding: 0; margin: 0 0 1rem 0; flex: 1; }
.plan li { font-size: .88rem; line-height: 1.45; padding: .35rem 0 .35rem 1.7rem; position: relative; color: #1E4D3A; }
.plan li::before { content: "✓"; position: absolute; left: 0; top: .32rem; width: 1.2rem; height: 1.2rem; border-radius: 50%;
  background: #E7F1D2; color: #3E8E63; font-weight: 900; font-size: .75rem; display: flex; align-items: center; justify-content: center; }
.plan .como-pago { font-size: .8rem; font-weight: 700; color: #1E4D3A; background: #E7F1D2; border-radius: 12px; padding: .55rem .8rem; }
.premio-arb { background: linear-gradient(140deg, #1E4D3A, #3E8E63); border-radius: 24px; padding: 1.5rem; height: 100%;
  box-shadow: 0 18px 40px -26px rgba(30,77,58,.9); }
.premio-arb .et { color: #D0E6A6; font-weight: 900; font-size: .78rem; letter-spacing: .1em; text-transform: uppercase; }
.premio-arb .v { color: #FFFFFF; font-weight: 900; font-size: 3rem; line-height: 1.1; margin: .5rem 0 .2rem; }
.premio-arb .ex { color: #FFFFFF; font-size: .9rem; line-height: 1.5; }
.premio-arb .ex b { color: #D0E6A6; }
.premio-arb .estado { display: inline-block; margin-top: .9rem; background: #FFFFFF; color: #1E4D3A; font-weight: 700;
  font-size: .82rem; border-radius: 999px; padding: .35rem .9rem; }
.et-premios { font-size: .78rem; font-weight: 900; letter-spacing: .1em; text-transform: uppercase; color: #4E7A5C; margin-bottom: 1rem; }
.et-premios b { color: #1E4D3A; }
.servicios { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
.servicios div { background: #F5F8EE; border-radius: 16px; padding: 1rem 1.1rem; }
.servicios b { display: block; color: #1E4D3A; font-weight: 900; margin-bottom: .3rem; }
.servicios span { color: #4E7A5C; font-size: .9rem; line-height: 1.45; }
.banda.confianza { margin-top: 1rem; border-left: 6px solid #6DBE45; }
.meta-barrio { background: linear-gradient(140deg, #1E4D3A, #3E8E63); border-radius: 24px; padding: 1.6rem 1.8rem; color: #FFFFFF; }
.meta-barrio .mb-num { font-size: 1.15rem; } .meta-barrio .mb-num b { color: #D0E6A6; font-weight: 900; font-size: 1.6rem; }
.meta-barrio .casas { display: flex; gap: .6rem; margin: 1rem 0; flex-wrap: wrap; }
.meta-barrio .casa { width: 2.4rem; height: 2.4rem; background: rgba(255,255,255,.22);
  clip-path: polygon(50% 0, 100% 42%, 100% 100%, 0 100%, 0 42%); }
.meta-barrio .casa.on { background: #BFD37A; }
.meta-barrio .casa.meta { outline: none; box-shadow: inset 0 -6px 0 #FFFFFF; }
.meta-barrio .mb-est { font-weight: 700; }
.premio { display: flex; gap: .9rem; align-items: center; margin-bottom: .9rem; }
.premio .pt { width: 4.4rem; height: 4.4rem; border-radius: 18px; background: #E7F1D2; color: #1E4D3A; font-weight: 900;
  display: flex; flex-direction: column; align-items: center; justify-content: center; flex-shrink: 0; font-size: 1.05rem; }
.premio .pt span { font-size: .65rem; font-weight: 700; }
.premio.listo .pt { background: #6DBE45; color: #FFFFFF; }
.premio .cuerpo { flex: 1; }
.qr-ok { background: #FFFFFF; border: 2px solid #6DBE45; border-radius: 16px; padding: .8rem 1rem; font-weight: 600; }
/* ---------- menú hamburguesa (solo en celular) ---------- */
.st-key-nav-hamb { display: none !important; }
.st-key-nav-hamb button { border-radius: 14px !important; border: 2px solid #BFD37A !important; background: #FFFFFF !important;
  min-height: 2.6rem; }
[data-testid="stPopoverBody"] [data-testid="stPageLink"] a { border-radius: 12px; padding: .5rem .8rem; }
[data-testid="stPopoverBody"] [data-testid="stPageLink"] a:hover { background: #E7F1D2; }
[data-testid="stPopoverBody"] [data-testid="stPageLink"] p { font-weight: 600; color: #1E4D3A !important; }

/* ---------- laptops pequeñas ---------- */
@media (max-width: 1400px) {
  .st-key-barra { padding: .5rem 1rem; }
  .st-key-barra [data-testid="stPageLink"] a { padding: .4rem .5rem; }
  .st-key-barra [data-testid="stPageLink"] p { font-size: .8rem; }
  .marca-logo .lema { display: none; }
}

/* ---------- celular ---------- */
@media (max-width: 900px) {
  .servicios { grid-template-columns: 1fr; }
  .meta-barrio .casa { width: 1.7rem; height: 1.7rem; }
  .st-key-nav-hamb { display: block !important; }
  [class*="st-key-navsec-"], .st-key-nav-vera { display: none !important; }
  .st-key-barra [data-testid="stHorizontalBlock"] { overflow-x: visible !important; justify-content: space-between !important; }
  .st-key-barra [data-testid="stColumn"]:has([class*="st-key-navsec-"]), .st-key-barra [data-testid="stColumn"]:has(.st-key-nav-vera) {
    display: none !important; }
  .st-key-barra { padding: .4rem .6rem; }
  .st-key-barra [data-testid="stHorizontalBlock"] { overflow-x: auto; scrollbar-width: none; justify-content: flex-start; }
  .st-key-barra [data-testid="stHorizontalBlock"]::-webkit-scrollbar { display: none; }
  .st-key-barra [data-testid="stColumn"] { flex: 0 0 auto !important; width: auto !important; min-width: auto !important; }
  .st-key-barra [data-testid="stHorizontalBlock"] { justify-content: space-between !important; }
  .st-key-barra [data-testid="stPageLink"] p { font-size: .82rem; }
  .marca-logo .lema { display: none; }
  .marca-logo .nombre { font-size: 1.45rem; margin-right: .4rem; }
  .block-container { padding-top: 5rem; padding-left: 1rem; padding-right: 1rem; }
  .como .grid, .valores, .planes, .franja, .mosaico .grid { grid-template-columns: 1fr !important; }
  .historia, .founder { grid-template-columns: 1fr; text-align: left; }
  .founder img { width: 140px !important; }
  .video-portada { min-height: 420px; }
  .video-portada h1, .portada h1 { font-size: 2.1rem; }
  .video-portada .contenido, .portada { padding: 1.6rem; }
  .ticket { flex-direction: column; text-align: center; }
  .guia .globo { display: none; }
  .guia .cara { width: 64px; height: 64px; }
  .plan.top { transform: none; }
}
</style>
""".replace("__RUIDO__", RUIDO).replace(
    "__PATRON__", "data:image/svg+xml;base64," + base64.b64encode((ASSETS / "patron.svg").read_bytes()).decode())


def aplicar() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def _b64(nombre: str) -> str:
    return base64.b64encode((ASSETS / nombre).read_bytes()).decode()


def imagen(nombre: str, alt: str, ancho: str = "100%", radio: str = "22px") -> str:
    """Una imagen de assets/ incrustada en HTML."""
    tipo = {"svg": "svg+xml", "png": "png"}.get(nombre.rsplit(".", 1)[-1], "jpeg")
    return (f'<img src="data:image/{tipo};base64,{_b64(nombre)}" alt="{alt}" '
            f'style="width:{ancho};border-radius:{radio};display:block">')


def portada(eyebrow: str, titulo: str, texto: str, fondo: str = "fardos.jpg") -> None:
    """Encabezado de cada sección. Una foto en blanco y negro (app/static/fondos) se funde con el verde del bloque."""
    capa = ("linear-gradient(110deg, rgba(30,77,58,.96) 0%, rgba(30,77,58,.88) 45%, rgba(62,142,99,.72) 100%), "
            f"url('app/static/fondos/{fondo}')")
    st.markdown(f'<div class="portada" style="background-image:{capa}"><div><div class="eyebrow">{eyebrow}</div>'
                f'<h1>{titulo}</h1><p>{texto}</p></div></div>', unsafe_allow_html=True)


def seccion(kicker: str, titulo: str, intro: str = "") -> None:
    extra = f'<p class="intro">{intro}</p>' if intro else ""
    st.markdown(f'<div class="seccion"><div class="kicker">{kicker}</div><h2>{titulo}</h2>{extra}</div>',
                unsafe_allow_html=True)


def tarjeta(titulo: str, texto: str, numero: str = "", paso: str = "", unidad: str = "") -> str:
    cabeza = ""
    if paso:
        cabeza = f'<div class="paso">{paso}</div>'
    elif numero:
        cabeza = f'<div class="num">{numero}</div>' + (f'<div class="unidad">{unidad}</div>' if unidad else "")
    return f'<div class="tarjeta">{cabeza}<div class="tit">{titulo}</div><div class="txt">{texto}</div></div>'


def fila_tarjetas(tarjetas: list[str]) -> None:
    cols = st.columns(len(tarjetas))
    for c, t in zip(cols, tarjetas):
        c.markdown(t, unsafe_allow_html=True)


def como_usar(pasos: list[tuple[str, str]], titulo: str = "Cómo usar esta sección") -> None:
    """Instrucciones breves, numeradas, al inicio de cada sección."""
    items = "".join(f'<div class="p"><div class="n">{i}</div><div><b>{t}</b><span>{x}</span></div></div>'
                    for i, (t, x) in enumerate(pasos, 1))
    st.markdown(f'<div class="como"><div class="t">{titulo}</div><div class="grid" '
                f'style="grid-template-columns:repeat({len(pasos)},1fr)">{items}</div></div>', unsafe_allow_html=True)


def metricas(items: list[tuple[str, str, str]], destacar: int | None = None) -> None:
    """Cifras con su explicación en lenguaje sencillo. items = (etiqueta, valor, qué significa)."""
    cols = st.columns(len(items))
    for i, (c, (et, v, ex)) in enumerate(zip(cols, items)):
        c.markdown(f'<div class="metrica{" ok" if i == destacar else ""}"><div class="et">{et}</div>'
                   f'<div class="v">{v}</div><div class="ex">{ex}</div></div>', unsafe_allow_html=True)


def pie() -> None:
    st.markdown(f'<div class="pie"><b>Minka</b> · {LEMA} · Proyecto final de la Diplomatura de Ciencia de Datos, '
                'Q-Lab PUCP · Viviendas y entregas sintéticas, residuos del distrito según datos abiertos del MINAM · '
                'Vera y Don Ciclo, personajes diseñados por Ana Karen Zamalloa</div>', unsafe_allow_html=True)


def guia(personaje: str, mensaje: str, destino: str = "asistente") -> None:
    """Personaje flotante que guía al vecino y lo lleva al chat."""
    nombre = {"vera": "Vera", "ciclo": "Don Ciclo"}[personaje]
    st.markdown(f'''<a class="guia" href="/{destino}" target="_self" aria-label="Hablar con {nombre}">
        <div class="globo"><b>{nombre}</b>{mensaje}</div>
        <div class="cara">{imagen(personaje + ".png", nombre, radio="0")}</div></a>''', unsafe_allow_html=True)


def identidad(personaje: str, nombre: str, detalle: str) -> None:
    """Tarjeta de la persona que tiene la sesión abierta."""
    st.markdown(f'<div class="identidad"><div class="av">{imagen(personaje + ".png", nombre, radio="0")}</div>'
                f'<div><b>{nombre}</b><span>{detalle}</span></div></div>', unsafe_allow_html=True)


def chat(mensajes: list[tuple[str, str, list[str]]]) -> None:
    """Conversación con burbujas al estilo de los mensajes del celular."""
    mini = f'<div class="mini">{imagen("vera.png", "Vera", radio="0")}</div>'
    filas = ['<div class="hora">Hoy · Vera, asistente de Minka</div>']
    if not mensajes:
        filas.append('<div class="vacio">Escríbele a Vera o toca una de las preguntas frecuentes.</div>')
    for rol, texto, fuentes in mensajes:
        if rol == "user":
            filas.append(f'<div class="fila yo"><div class="burbuja">{texto}</div></div>')
        else:
            filas.append(f'<div class="fila ella">{mini}<div class="burbuja">{texto}</div></div>')
            if fuentes:
                filas.append(f'<div class="fuente">Según la guía de Minka, {", ".join(fuentes).lower()}</div>')
    st.markdown(f'<div class="chat">{"".join(filas)}</div>', unsafe_allow_html=True)


def retrato(personaje: str, alt: str) -> None:
    st.markdown(f'<div class="retrato">{imagen(personaje + ".png", alt, radio="0")}</div>', unsafe_allow_html=True)


def sticker(codigo: str) -> bytes:
    """Sticker de puerta «Esta casa recicla con Minka», con el QR de la vivienda, como PNG."""
    import base64
    import io
    from PIL import Image, ImageDraw, ImageFont

    def fuente(tam: int, negrita: bool = True):
        for ruta in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if negrita else
                     "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
            try:
                return ImageFont.truetype(ruta, tam)
            except OSError:
                pass
        return ImageFont.load_default(size=tam)

    W, H = 640, 860
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, W - 1, H - 1], radius=48, fill="#1E4D3A")
    d.rounded_rectangle([18, 18, W - 19, H - 19], radius=38, outline="#BFD37A", width=4)
    centro = lambda y, txt, f, color: d.text((W / 2, y), txt, font=f, fill=color, anchor="mm")
    centro(95, "Esta casa recicla con", fuente(36), "#D0E6A6")
    grande = fuente(92)
    ancho_min, ancho_ka = d.textlength("min", font=grande), d.textlength("ka", font=grande)
    x0 = (W - ancho_min - ancho_ka) / 2
    d.text((x0, 170), "min", font=grande, fill="#FFFFFF", anchor="lm")
    d.text((x0 + ancho_min, 170), "ka", font=grande, fill="#6DBE45", anchor="lm")
    codigo_qr = Image.open(io.BytesIO(base64.b64decode(qr(codigo)))).convert("RGB").resize((380, 380))
    d.rounded_rectangle([110, 240, 530, 660], radius=28, fill="#FFFFFF")
    img.paste(codigo_qr, (130, 260))
    centro(710, f"Vivienda {codigo}", fuente(30), "#FFFFFF")
    centro(770, "Juntos, cada aporte cuenta", fuente(26, False), "#D0E6A6")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def qr(texto: str) -> str:
    """Código QR del ticket digital, como imagen PNG en base64."""
    import io
    import qrcode
    img = qrcode.QRCode(box_size=8, border=2)
    img.add_data(texto)
    img.make(fit=True)
    buf = io.BytesIO()
    img.make_image(fill_color="#1E4D3A", back_color="white").save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def ticket(codigo: str, detalle: str, validado: bool = False) -> None:
    estado = '<span class="estado ok">Validado</span>' if validado else '<span class="estado">Pendiente de recojo</span>'
    st.markdown(f'''<div class="ticket"><img src="data:image/png;base64,{qr(codigo)}" alt="Código QR del ticket {codigo}">
        <div>{estado}<div class="codigo">{codigo}</div>{detalle}</div></div>''', unsafe_allow_html=True)


def logo() -> str:
    """Logotipo solo con el nombre, en Montserrat Black, y su bajada."""
    return f'<div class="marca-logo"><div><div class="nombre">min<b>ka</b></div><div class="lema">{LEMA}</div></div></div>'


def video_portada(eyebrow: str, titulo: str, texto: str) -> bool:
    """Portada con video de fondo (app/static/portada.mp4), servido como archivo estático de Streamlit."""
    if not (ASSETS.parent / "static" / "portada.mp4").exists():
        return False
    st.markdown(f'''<div class="video-portada"><video autoplay muted loop playsinline poster="app/static/portada.jpg">
        <source src="app/static/portada.mp4" type="video/mp4"></video><div class="velo"></div>
        <div class="contenido"><span class="eyebrow">{eyebrow}</span><h1>{titulo}</h1>
        <p>{texto}</p></div></div>''', unsafe_allow_html=True)
    return True
