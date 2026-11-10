"""Identidad visual de Minka: paleta, tipografía y componentes reutilizables.

Paleta de celestes y amarillos sobre fondo marfil, con un azul petróleo profundo para textos y
botones, de modo que todo tenga contraste suficiente. Montserrat en todos los textos, con Black
para los títulos. Los personajes Vera y Don Ciclo son diseño de la autora.
"""
import base64
from pathlib import Path

import streamlit as st

PALETA = {
    "celeste": "#50B6CF",   # acento principal
    "pastel": "#A8DCE8",    # bordes y fondos suaves
    "hielo": "#D9F0F2",     # fondos de bloques
    "mostaza": "#E5B94F",   # llamadas a la acción y destacados
    "suave": "#F5D98D",     # fondos cálidos
    "marfil": "#FFF8E9",    # fondo general
    "tinta": "#17414F",     # textos, títulos y botones (contraste alto)
    "agua": "#2A6F84",      # textos secundarios sobre blanco
}
ASSETS = Path(__file__).resolve().parent / "assets"
LEMA = "Juntos, cada aporte cuenta"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;900&display=swap');

/* ---------- base ---------- */
.stApp { background: #FFF8E9; }
header[data-testid="stHeader"] { display: none; }
.stApp, .stApp *:not([data-testid="stIconMaterial"]):not(.material-symbols-rounded):not(code):not(pre) {
  font-family: 'Montserrat', sans-serif !important; }
.stApp p, .stApp li, .stApp label, .stApp td { color: #17414F; }
h1, h2, h3, h4, h5 { color: #17414F !important; font-weight: 900 !important; letter-spacing: -0.02em; }
.block-container { padding-top: 6.6rem; max-width: 1220px; }
[data-testid="stWidgetLabel"] p { font-weight: 600 !important; color: #17414F !important; }
a { color: #2A6F84; font-weight: 600; }
@keyframes subir { from { opacity: 0; transform: translateY(18px); } to { opacity: 1; transform: none; } }
@keyframes flotar { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }

/* ---------- barra de navegación ---------- */
.st-key-barra { position: fixed; top: 0; left: 0; right: 0; z-index: 1000; padding: .5rem 2rem;
  background: #FFFFFF; border-bottom: 2px solid #D9F0F2; box-shadow: 0 8px 24px -18px rgba(23,65,79,.55); }
.st-key-barra [data-testid="stHorizontalBlock"] { align-items: center !important; gap: .25rem; flex-wrap: nowrap; }
.st-key-barra [data-testid="stColumn"] { display: flex; align-items: center; justify-content: center; min-width: 0; }
.st-key-barra [data-testid="stColumn"]:first-child { justify-content: flex-start; }
.st-key-barra [data-testid="stColumn"] > div { width: 100%; }
.st-key-barra [data-testid="stElementContainer"], .st-key-barra [data-testid="stMarkdownContainer"] { margin: 0 !important; }
.st-key-barra [data-testid="stVerticalBlock"] { gap: 0 !important; justify-content: center; }
.st-key-barra [data-testid="stPageLink"] { display: flex; justify-content: center; }
.st-key-barra [data-testid="stPageLink"] a { border-radius: 999px; padding: .45rem .75rem; justify-content: center;
  margin: 0; min-height: 2.5rem; align-items: center; }
.st-key-barra [data-testid="stPageLink"] a:hover { background: #D9F0F2; }
.st-key-barra [data-testid="stPageLink"] p { font-weight: 600; font-size: .86rem; white-space: nowrap; margin: 0;
  color: #17414F !important; line-height: 1; }
.st-key-barra [data-testid="stPageLink"] a[aria-current="page"] { background: #D9F0F2; }
.st-key-barra [data-testid="stPageLink"] a[aria-current="page"] p { font-weight: 900; }
.st-key-nav-vera [data-testid="stPageLink"] a { border: 2px solid #50B6CF; background: #FFFFFF; }
.st-key-nav-vera [data-testid="stPageLink"] p { font-weight: 900 !important; }
.st-key-nav-recicla [data-testid="stPageLink"] a, .st-key-cta-recicla [data-testid="stPageLink"] a {
  background: #E5B94F; box-shadow: 0 8px 18px -10px rgba(23,65,79,.7); }
.st-key-nav-recicla [data-testid="stPageLink"] a:hover, .st-key-cta-recicla [data-testid="stPageLink"] a:hover { background: #F5D98D; }
.st-key-nav-recicla [data-testid="stPageLink"] p, .st-key-cta-recicla [data-testid="stPageLink"] p,
.st-key-nav-recicla [data-testid="stPageLink"] span, .st-key-cta-recicla [data-testid="stPageLink"] span {
  color: #17414F !important; font-weight: 900 !important; }
.st-key-cta-muni [data-testid="stPageLink"] a { background: #FFFFFF; border: 2px solid #17414F; }
.st-key-cta-muni [data-testid="stPageLink"] p { font-weight: 900 !important; }
.st-key-cta-recicla [data-testid="stPageLink"] a, .st-key-cta-muni [data-testid="stPageLink"] a {
  border-radius: 999px; padding: .8rem 1.4rem; justify-content: center; }

/* ---------- logo ---------- */
.marca-logo { display: flex; align-items: center; gap: .6rem; }
.marca-logo img { width: 42px !important; height: 42px; }
.marca-logo .nombre { font-weight: 900; font-size: 1.5rem; color: #17414F; letter-spacing: -.04em; line-height: 1; }
.marca-logo .lema { font-weight: 500; font-size: .66rem; color: #2A6F84; letter-spacing: .02em; margin-top: .2rem;
  white-space: nowrap; }

/* ---------- portada de cada sección ---------- */
.portada { position: relative; overflow: hidden; border-radius: 28px; padding: 2.5rem 2.8rem; margin-bottom: 1.6rem;
  background: #17414F; box-shadow: 0 24px 50px -28px rgba(23,65,79,.8); animation: subir .6s ease both; }
.portada::before { content: ""; position: absolute; width: 380px; height: 380px; right: -110px; top: -170px;
  border-radius: 50%; background: #50B6CF; opacity: .35; }
.portada::after { content: ""; position: absolute; width: 220px; height: 220px; right: 140px; bottom: -150px;
  border-radius: 50%; background: #A8DCE8; opacity: .18; }
.portada > div { position: relative; z-index: 1; max-width: 48rem; }
.portada h1 { color: #FFFFFF !important; font-size: 2.7rem; margin: 0; line-height: 1.08; }
.portada h1 .resalte, .video-portada h1 .resalte { font-style: normal; color: #F5D98D; }
.portada p { color: #FFFFFF !important; font-size: 1.05rem; line-height: 1.6; margin: .9rem 0 0 0; opacity: .92; }
.eyebrow { display: inline-block; color: #17414F; background: #F5D98D; font-weight: 900; letter-spacing: .14em;
  text-transform: uppercase; font-size: .7rem; padding: .35rem .85rem; border-radius: 999px; margin-bottom: .9rem; }

/* ---------- títulos de bloque ---------- */
.seccion { margin: 2.6rem 0 1rem 0; }
.seccion .kicker { color: #2A6F84; font-weight: 900; letter-spacing: .16em; text-transform: uppercase; font-size: .72rem; }
.seccion h2 { margin: .2rem 0 0 0 !important; font-size: 2rem; }
.seccion .intro { margin: .5rem 0 0 0; font-size: 1rem; line-height: 1.6; max-width: 52rem; }

/* ---------- tarjetas con contraste ---------- */
.tarjeta { background: #FFFFFF; border: 2px solid #A8DCE8; border-radius: 22px; padding: 1.4rem 1.4rem 1.3rem;
  height: 100%; box-shadow: 0 14px 30px -20px rgba(23,65,79,.55); animation: subir .6s ease both;
  transition: transform .2s ease, border-color .2s ease; }
.tarjeta:hover { transform: translateY(-4px); border-color: #50B6CF; }
.tarjeta .num { font-weight: 900; font-size: 2.4rem; color: #17414F; line-height: 1; letter-spacing: -.02em; }
.tarjeta .unidad { font-weight: 700; color: #2A6F84; font-size: .85rem; margin-top: .3rem; }
.tarjeta .tit { font-weight: 900; color: #17414F; font-size: 1.08rem; margin: .7rem 0 .35rem 0; }
.tarjeta .txt { font-size: .93rem; color: #17414F; line-height: 1.6; }
.paso { display: inline-flex; align-items: center; justify-content: center; width: 2.4rem; height: 2.4rem;
  border-radius: 50%; background: #E5B94F; color: #17414F; font-weight: 900; }
.etiqueta { display: inline-block; padding: .3rem .85rem; border-radius: 999px; font-size: .78rem; font-weight: 700;
  background: #17414F; color: #FFFFFF; margin: 0 .35rem .45rem 0; }
.etiqueta.clara { background: #FFFFFF; color: #17414F; border: 2px solid #50B6CF; }
.etiqueta.sol { background: #F5D98D; color: #17414F; }
.banda { background: #FFFFFF; border-radius: 18px; padding: 1.1rem 1.4rem; color: #17414F; font-weight: 500;
  font-size: 1.02rem; margin: .8rem 0 1.2rem 0; border-left: 8px solid #E5B94F;
  box-shadow: 0 12px 26px -20px rgba(23,65,79,.6); }
.banda b { font-weight: 900; }
.nota { color: #2A6F84 !important; font-size: .85rem; line-height: 1.5; margin-top: .8rem; }
.pie { text-align: center; color: #2A6F84; font-size: .8rem; margin-top: 3.5rem; padding-top: 1.4rem;
  border-top: 2px solid #D9F0F2; }

/* ---------- guía de uso de cada sección ---------- */
.como { background: #D9F0F2; border-radius: 22px; padding: 1.2rem 1.3rem; margin: 0 0 1.6rem 0; }
.como .t { font-weight: 900; color: #17414F; font-size: .78rem; letter-spacing: .14em; text-transform: uppercase;
  margin-bottom: .8rem; }
.como .grid { display: grid; gap: .8rem; }
.como .p { background: #FFFFFF; border-radius: 16px; padding: .9rem 1rem; display: flex; gap: .75rem; align-items: flex-start; }
.como .n { flex-shrink: 0; width: 2rem; height: 2rem; border-radius: 50%; background: #E5B94F; color: #17414F;
  display: flex; align-items: center; justify-content: center; font-weight: 900; }
.como b { display: block; color: #17414F; font-weight: 900; font-size: .92rem; }
.como span { font-size: .84rem; color: #17414F; line-height: 1.45; }

/* ---------- métricas explicadas ---------- */
.metrica { background: #FFFFFF; border: 2px solid #A8DCE8; border-radius: 20px; padding: 1.1rem 1.2rem; height: 100%;
  box-shadow: 0 12px 26px -20px rgba(23,65,79,.55); }
.metrica .et { font-size: .8rem; font-weight: 700; color: #2A6F84; text-transform: uppercase; letter-spacing: .06em; }
.metrica .v { font-size: 2rem; font-weight: 900; color: #17414F; line-height: 1.15; margin: .25rem 0; }
.metrica .ex { font-size: .82rem; color: #17414F; line-height: 1.45; }
.metrica.ok { border-color: #E5B94F; background: #FFFBEF; }
div[data-testid="stMetric"] { background: #FFFFFF; border: 2px solid #A8DCE8; border-radius: 20px; padding: 1rem 1.2rem;
  box-shadow: 0 12px 26px -20px rgba(23,65,79,.55); }
div[data-testid="stMetricValue"] { font-weight: 900; color: #17414F; }

/* ---------- controles ---------- */
.stButton > button, .stDownloadButton > button, .stLinkButton > a { border-radius: 14px !important; font-weight: 600 !important;
  border: 2px solid #A8DCE8 !important; background: #FFFFFF !important; color: #17414F !important; }
.stButton > button:hover, .stLinkButton > a:hover { border-color: #50B6CF !important; }
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"], .stFormSubmitButton > button {
  background: #17414F !important; color: #FFFFFF !important; border: none !important;
  box-shadow: 0 10px 20px -12px rgba(23,65,79,.9); }
.stButton > button[kind="primary"] *, .stDownloadButton > button[kind="primary"] *, .stFormSubmitButton > button * { color: #FFFFFF !important; }
.stButton > button[kind="primary"]:hover, .stFormSubmitButton > button:hover { background: #2A6F84 !important; }
.stTextInput input, .stTextArea textarea, .stDateInput input, .stNumberInput input {
  border-radius: 12px !important; background: #FFFFFF !important; color: #17414F !important; }
[data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="base-input"] { border-radius: 12px !important;
  border-color: #A8DCE8 !important; background: #FFFFFF !important; }
[data-testid="stForm"] { background: #FFFFFF; border: 2px solid #A8DCE8; border-radius: 22px; padding: 1.4rem; }
iframe { border-radius: 20px; }

/* opciones como botones (sin desplegables) */
[data-testid="stPills"] button, [data-testid="stButtonGroup"] button {
  background: #FFFFFF !important; border: 2px solid #A8DCE8 !important; color: #17414F !important;
  border-radius: 999px !important; font-weight: 600 !important; }
[data-testid="stPills"] button[kind*="Active"], [data-testid="stButtonGroup"] button[kind*="Active"],
[data-testid="stPills"] button[aria-checked="true"], [data-testid="stButtonGroup"] button[aria-checked="true"] {
  background: #17414F !important; border-color: #17414F !important; }
[data-testid="stPills"] button[kind*="Active"] *, [data-testid="stButtonGroup"] button[kind*="Active"] *,
[data-testid="stPills"] button[aria-checked="true"] *, [data-testid="stButtonGroup"] button[aria-checked="true"] * {
  color: #FFFFFF !important; }

/* pestañas como interruptor redondeado */
.stTabs [role="tablist"], .stTabs div:has(> [data-testid="stTab"]) { gap: .3rem !important; background: #D9F0F2;
  padding: .35rem !important; border-radius: 999px; width: fit-content !important; max-width: 100%;
  margin-bottom: 1rem; border: none !important; box-shadow: none !important; }
.stTabs div:has(> div > [data-testid="stTab"]) { border: none !important; box-shadow: none !important; }
.stTabs div:has(> [data-testid="stTab"]) > div:not([data-testid="stTab"]) { display: none !important; }
.stTabs [data-testid="stTab"] { background: transparent !important; border: none !important; border-radius: 999px !important;
  padding: .55rem 1.3rem !important; height: auto !important; margin: 0 !important; cursor: pointer; }
.stTabs [data-testid="stTab"]::after, .stTabs [data-testid="stTab"]::before { display: none !important; }
.stTabs [data-testid="stTab"] p { font-weight: 600 !important; color: #17414F !important; font-size: .92rem; margin: 0; }
.stTabs [data-testid="stTab"][aria-selected="true"] { background: #FFFFFF !important;
  box-shadow: 0 6px 14px -8px rgba(23,65,79,.6); }
.stTabs [data-testid="stTab"][aria-selected="true"] p { font-weight: 900 !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ---------- ticket digital ---------- */
.ticket { display: flex; gap: 1.6rem; align-items: center; background: #FFFFFF; border-radius: 26px; padding: 1.6rem;
  border: 3px dashed #50B6CF; box-shadow: 0 22px 46px -24px rgba(23,65,79,.55); animation: subir .5s ease both; }
.ticket img { width: 170px; border-radius: 14px; }
.ticket .codigo { font-weight: 900; font-size: 2.2rem; color: #17414F; letter-spacing: .04em; }
.ticket .estado { display: inline-block; background: #F5D98D; color: #17414F; border-radius: 999px; padding: .2rem .8rem;
  font-size: .78rem; font-weight: 700; }
.ticket .estado.ok { background: #50B6CF; color: #17414F; }
.ticket p { margin: .35rem 0 0 0; font-size: .92rem; }

/* ---------- personaje guía ---------- */
.retrato { display: flex; justify-content: center; align-items: flex-end; height: 280px; border-radius: 28px; overflow: hidden;
  background: radial-gradient(circle at 50% 35%, #FFFFFF 0%, #D9F0F2 45%, #A8DCE8 100%); }
.retrato img { width: 80% !important; margin: 0 auto; animation: flotar 6s ease-in-out infinite; }
.guia { position: fixed; right: 26px; bottom: 26px; z-index: 999; display: flex; align-items: flex-end; gap: .7rem;
  animation: subir .8s ease 1s both; text-decoration: none !important; }
.guia .globo { max-width: 270px; background: #FFFFFF; color: #17414F; border-radius: 20px 20px 6px 20px; padding: .85rem 1rem;
  font-size: .88rem; line-height: 1.45; font-weight: 500; box-shadow: 0 16px 34px -14px rgba(23,65,79,.55);
  border: 2px solid #50B6CF; }
.guia .globo b { font-weight: 900; display: block; margin-bottom: .15rem; color: #2A6F84; }
.guia .cara { width: 88px; height: 88px; border-radius: 50%; overflow: hidden; flex-shrink: 0; border: 4px solid #FFFFFF;
  box-shadow: 0 0 0 4px #E5B94F, 0 16px 30px -12px rgba(23,65,79,.7); animation: flotar 4s ease-in-out infinite;
  background: radial-gradient(circle at 50% 35%, #FFFFFF, #A8DCE8); }
.guia .cara img { width: 100%; display: block; }

/* ---------- chat estilo mensajes del celular ---------- */
.chat { display: flex; flex-direction: column; gap: .45rem; padding: 1.2rem; min-height: 360px; background: #FFFFFF;
  border-radius: 26px; border: 2px solid #A8DCE8; box-shadow: 0 18px 40px -24px rgba(23,65,79,.5); }
.chat .hora { text-align: center; color: #2A6F84; font-size: .72rem; font-weight: 600; margin: .2rem 0 .6rem; }
.chat .fila { display: flex; align-items: flex-end; gap: .45rem; animation: subir .3s ease both; }
.chat .fila.yo { justify-content: flex-end; }
.chat .mini { width: 34px; height: 34px; border-radius: 50%; overflow: hidden; flex-shrink: 0;
  background: radial-gradient(circle at 50% 35%, #FFFFFF, #A8DCE8); }
.chat .mini img { width: 100%; }
.chat .burbuja { max-width: 72%; padding: .62rem .95rem; font-size: .95rem; line-height: 1.45; border-radius: 20px; }
.chat .ella .burbuja { background: #E9E9EB; color: #1C1C1E; border-bottom-left-radius: 6px; }
.chat .yo .burbuja { background: #17414F; color: #FFFFFF; border-bottom-right-radius: 6px; }
.chat .fuente { font-size: .7rem; color: #2A6F84; margin: -.1rem 0 .3rem 2.4rem; }
.chat .vacio { margin: auto; text-align: center; color: #2A6F84; }
[data-testid="stChatInput"] { border-radius: 999px !important; border: 2px solid #50B6CF !important; background: #FFFFFF !important; }

/* ---------- paneles, barras, ranking, tablas ---------- */
.panel { background: #FFFFFF; border-radius: 22px; padding: 1.3rem 1.4rem; border: 2px solid #D9F0F2;
  box-shadow: 0 16px 34px -24px rgba(23,65,79,.6); animation: subir .5s ease both; }
.barra { margin: .2rem 0 1rem 0; }
.barra-top { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: .35rem; gap: 1rem; }
.barra-etq { font-weight: 700; color: #17414F; font-size: .95rem; }
.barra-val { font-weight: 900; color: #17414F; font-size: .95rem; white-space: nowrap; }
.barra-pista { background: #D9F0F2; border-radius: 999px; height: 14px; overflow: hidden; flex: 1; }
.barra-pista.grande { height: 26px; }
.barra-relleno { height: 100%; border-radius: 999px; animation: crecer 1s cubic-bezier(.2,.8,.2,1) both; }
@keyframes crecer { from { width: 0 !important; } }
.barra-det { font-size: .8rem; color: #2A6F84; margin-top: .25rem; }
.rk { display: flex; gap: .9rem; align-items: center; margin-bottom: .9rem; }
.rk-pos { width: 2.3rem; height: 2.3rem; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-weight: 900; flex-shrink: 0; }
.rk-cuerpo { flex: 1; }
.cmp-fila { display: flex; align-items: center; gap: .9rem; margin: .6rem 0; }
.cmp-etq { width: 110px; font-weight: 700; color: #17414F; }
.cmp-val { width: 70px; text-align: right; font-weight: 900; color: #17414F; }
.cmp-msg { margin-top: .8rem; padding: .7rem 1rem; background: #FFF4D6; border-radius: 14px; color: #17414F; font-weight: 600; }
.vacio-panel { color: #2A6F84; text-align: center; }
.tabla { overflow: auto; border-radius: 18px; border: 2px solid #D9F0F2; background: #FFFFFF;
  box-shadow: 0 14px 30px -24px rgba(23,65,79,.6); }
.tabla table { width: 100%; border-collapse: collapse; font-size: .9rem; }
.tabla th { position: sticky; top: 0; background: #17414F; color: #FFFFFF !important; text-align: left; padding: .8rem .95rem;
  font-weight: 700; }
.tabla td { padding: .7rem .95rem; color: #17414F; border-bottom: 1px solid #D9F0F2; }
.tabla tr:nth-child(even) td { background: #F6FBFC; }
.tabla td.num { text-align: right; font-weight: 700; }
.lt-item { display: flex; gap: .9rem; position: relative; padding-bottom: .9rem; }
.lt-item:not(:last-child)::before { content: ""; position: absolute; left: 7px; top: 18px; bottom: 0; width: 2px; background: #D9F0F2; }
.lt-punto { width: 16px; height: 16px; border-radius: 50%; margin-top: .25rem; flex-shrink: 0; box-shadow: 0 0 0 4px #FFFFFF, 0 0 0 5px #D9F0F2; }
.lt-caja { flex: 1; }
.lt-fecha { font-weight: 900; color: #17414F; font-size: .9rem; }
.lt-txt { font-size: .86rem; color: #17414F; margin: .15rem 0 .3rem 0; }
.lt-est { font-size: .72rem; font-weight: 700; padding: .15rem .6rem; border-radius: 999px; }
.lt-est.ok { background: #D9F0F2; color: #17414F; } .lt-est.no { background: #FFF4D6; color: #7A5600; }
.mat { background: #FFFFFF; border-radius: 22px; padding: 1.1rem .8rem .9rem; text-align: center; border: 2px solid #D9F0F2;
  box-shadow: 0 14px 30px -24px rgba(23,65,79,.6); }
.mat svg { display: block; margin: 0 auto .5rem auto; }
.mat-nom { font-weight: 900; color: #17414F; }
.mat-pts { font-size: .78rem; color: #2A6F84; }

/* ---------- inicio ---------- */
.video-portada { position: relative; overflow: hidden; border-radius: 30px; margin-bottom: 1.4rem; min-height: 500px;
  display: flex; align-items: flex-end; box-shadow: 0 30px 60px -30px rgba(23,65,79,.8); }
.video-portada video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.video-portada .velo { position: absolute; inset: 0;
  background: linear-gradient(0deg, rgba(23,65,79,.96) 0%, rgba(23,65,79,.82) 28%, rgba(42,111,132,.35) 62%, rgba(80,182,207,0) 100%); }
.video-portada .contenido { position: relative; padding: 2.6rem; max-width: 50rem; }
.video-portada h1 { color: #FFFFFF !important; font-size: 3.3rem; line-height: 1.04; margin: .5rem 0 0 0; }
.video-portada p { color: #FFFFFF !important; font-size: 1.1rem; line-height: 1.6; }
.video-portada .lema-vid { color: #FFFFFF; font-weight: 500; font-size: 1rem; letter-spacing: .02em; }
.perfil { position: relative; border-radius: 26px; overflow: hidden; height: 350px; display: flex; flex-direction: column;
  justify-content: flex-end; padding: 1.4rem; box-shadow: 0 20px 40px -24px rgba(23,65,79,.75); transition: transform .25s ease; }
.perfil:hover { transform: translateY(-6px); }
.perfil .fig { position: absolute; inset: 0; display: flex; justify-content: center; align-items: flex-start; padding-top: 1.2rem; }
.perfil .fig img { height: 175px !important; width: auto !important; }
.perfil .fig svg { width: 170px; height: 170px; }
.perfil::after { content: ""; position: absolute; inset: 0; background: linear-gradient(0deg, rgba(23,65,79,.97) 0%, rgba(23,65,79,.75) 30%, rgba(23,65,79,0) 50%); }
.perfil .txt { position: relative; z-index: 1; }
.perfil .ptit { color: #FFFFFF !important; font-weight: 900; font-size: 1.55rem !important; margin: 0 !important; padding: 0 !important; line-height: 1.15; }
.perfil span { color: #FFFFFF; font-size: .88rem; display: block; margin-top: .3rem; line-height: 1.4; }
.perfil .ir { display: inline-block; margin-top: .7rem; background: #E5B94F; color: #17414F; font-weight: 900;
  font-size: .8rem; padding: .3rem .8rem; border-radius: 999px; }
[class*="st-key-perfil-"] { position: relative; }
[class*="st-key-perfil-"] [data-testid="stPageLink"] { position: absolute; inset: 0; z-index: 5; }
[class*="st-key-perfil-"] [data-testid="stPageLink"] a { position: absolute; inset: 0; opacity: 0; }
[class*="st-key-perfil-"] [data-testid="stElementContainer"]:has([data-testid="stPageLink"]) { position: absolute; inset: 0; z-index: 5;
  margin: 0; width: 100% !important; height: 100% !important; }
[class*="st-key-perfil-"] [data-testid="stPageLink"], [class*="st-key-perfil-"] [data-testid="stPageLink"] a {
  width: 100% !important; height: 100% !important; max-width: none !important; }
.historia { display: grid; grid-template-columns: .9fr 1.4fr; gap: 2.2rem; align-items: center; background: #FFFFFF;
  border-radius: 30px; padding: 2rem; border: 2px solid #A8DCE8; box-shadow: 0 20px 44px -28px rgba(23,65,79,.6); }
.historia figure { margin: 0; }
.historia figure img { width: 100% !important; border-radius: 24px; display: block; }
.historia figcaption { font-size: .75rem; color: #2A6F84; margin-top: .45rem; text-align: center; }
.historia blockquote, .historia blockquote * { color: #17414F !important; opacity: 1 !important; }
.historia blockquote { margin: 0; font-size: 1.12rem; line-height: 1.6; color: #17414F; font-weight: 500; border: none;
  padding: 0 0 0 1.2rem; border-left: 6px solid #E5B94F; }
.historia .firma { margin-top: 1rem; color: #17414F; font-size: .9rem; }
.historia .firma b { font-weight: 900; }
.reflexion { font-size: 1.02rem; line-height: 1.7; margin: 1.4rem 0 0 0; max-width: 60rem; }
.idea-fuerza { margin: 1.2rem 0 0 0; background: #17414F; border-radius: 26px; padding: 1.8rem 2rem; position: relative;
  overflow: hidden; box-shadow: 0 22px 44px -26px rgba(23,65,79,.9); }
.idea-fuerza::before { content: ""; position: absolute; width: 240px; height: 240px; right: -70px; top: -90px; border-radius: 50%;
  background: #50B6CF; opacity: .3; }
.idea-fuerza p { position: relative; color: #FFFFFF !important; font-size: 1.28rem; line-height: 1.55; font-weight: 700; margin: 0; }
.idea-fuerza p b { color: #F5D98D; font-weight: 900; }
.mosaico { border-radius: 30px; padding: 3.2rem 2rem; margin: 1rem 0;
  background-color: #50B6CF;
  background-image: radial-gradient(circle at 20px 20px, #17414F 9px, transparent 10px),
                    radial-gradient(circle at 20px 20px, #A8DCE8 19px, transparent 20px);
  background-size: 56px 56px; }
.mosaico .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.4rem; max-width: 1080px; margin: 0 auto; }
.mosaico .c { background: #FFFFFF; padding: 1.7rem 1.6rem 1.6rem; border-bottom: 14px solid #17414F; }
.mosaico .c h3 { font-size: 1.7rem; margin: 0 0 .7rem 0; }
.mosaico .c p { font-size: .98rem; line-height: 1.65; margin: 0; }
.valores { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
.valor { background: #FFFFFF; border-radius: 22px; padding: 1.3rem; border: 2px solid #A8DCE8; display: flex; gap: 1rem;
  align-items: flex-start; box-shadow: 0 12px 26px -22px rgba(23,65,79,.6); }
.valor .ic { flex-shrink: 0; width: 3.2rem; height: 3.2rem; border-radius: 16px; display: flex; align-items: center;
  justify-content: center; }
.valor b { display: block; color: #17414F; font-weight: 900; font-size: 1.05rem; margin-bottom: .2rem; }
.valor span { font-size: .9rem; line-height: 1.5; color: #17414F; }
.franja { background: #17414F; border-radius: 28px; padding: 1rem 1.2rem; margin: 1rem 0 .4rem 0;
  display: grid; grid-template-columns: repeat(4, 1fr); box-shadow: 0 24px 50px -28px rgba(23,65,79,.8); }
.cifra { text-align: center; padding: 1.3rem .8rem; }
.cifra .n { font-size: 2.6rem; font-weight: 900; color: #F5D98D; line-height: 1; }
.cifra .t { color: #FFFFFF; font-size: .9rem; margin-top: .45rem; }
.actor { background: #FFFFFF; border-radius: 18px; padding: 1rem 1.1rem; border: 2px solid #D9F0F2; border-left: 8px solid #50B6CF;
  height: 100%; box-shadow: 0 12px 26px -22px rgba(23,65,79,.6); }
.actor.estado { border-left-color: #17414F; } .actor.academia { border-left-color: #E5B94F; }
.actor .tipo { font-size: .7rem; font-weight: 900; letter-spacing: .12em; text-transform: uppercase; color: #2A6F84; }
.actor .nom { font-weight: 900; color: #17414F; margin: .2rem 0; }
.actor .txt { font-size: .86rem; color: #17414F; line-height: 1.5; }
.founder { display: grid; grid-template-columns: 180px 1fr; gap: 1.6rem; align-items: center; background: #FFFFFF;
  border-radius: 26px; padding: 1.5rem; border: 2px solid #A8DCE8; }
.founder img { width: 180px !important; border-radius: 50%; border: 6px solid #D9F0F2; }
.founder h3 { margin: 0 0 .4rem 0; }
.founder p { margin: .3rem 0; line-height: 1.6; }
.noticia { background: #FFFFFF; border-radius: 22px; overflow: hidden; border: 2px solid #A8DCE8; height: 100%;
  box-shadow: 0 14px 30px -22px rgba(23,65,79,.6); display: flex; flex-direction: column; }
.noticia .img { height: 130px; display: flex; align-items: center; justify-content: center; }
.noticia .cuerpo { padding: 1.1rem 1.2rem 1.2rem; }
.noticia .medio { font-size: .72rem; font-weight: 900; letter-spacing: .1em; text-transform: uppercase; color: #2A6F84; }
.noticia .tit { font-weight: 900; color: #17414F; margin: .35rem 0; line-height: 1.35; }
.noticia .txt { font-size: .86rem; line-height: 1.5; color: #17414F !important; font-weight: 500 !important; }
.noticia .tit { color: #17414F !important; }
.identidad { display: flex; gap: .9rem; align-items: center; background: #FFFFFF; border: 2px solid #50B6CF; border-radius: 18px;
  padding: .8rem 1rem; margin: .4rem 0 1rem 0; }
.identidad .av { width: 52px; height: 52px; border-radius: 50%; overflow: hidden; flex-shrink: 0;
  background: radial-gradient(circle at 50% 35%, #FFFFFF, #A8DCE8); }
.identidad .av img { width: 100%; }
.identidad b { color: #17414F; font-weight: 900; display: block; }
.identidad span { font-size: .85rem; color: #2A6F84; }
</style>
"""


def aplicar() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def _b64(nombre: str) -> str:
    return base64.b64encode((ASSETS / nombre).read_bytes()).decode()


def imagen(nombre: str, alt: str, ancho: str = "100%", radio: str = "22px") -> str:
    """Una imagen de assets/ incrustada en HTML."""
    tipo = {"svg": "svg+xml", "png": "png"}.get(nombre.rsplit(".", 1)[-1], "jpeg")
    return (f'<img src="data:image/{tipo};base64,{_b64(nombre)}" alt="{alt}" '
            f'style="width:{ancho};border-radius:{radio};display:block">')


def portada(eyebrow: str, titulo: str, texto: str) -> None:
    """Encabezado de cada sección, en azul petróleo con texto blanco."""
    st.markdown(f'<div class="portada"><div><div class="eyebrow">{eyebrow}</div><h1>{titulo}</h1><p>{texto}</p>'
                f'</div></div>', unsafe_allow_html=True)


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


def qr(texto: str) -> str:
    """Código QR del ticket digital, como imagen PNG en base64."""
    import io
    import qrcode
    img = qrcode.QRCode(box_size=8, border=2)
    img.add_data(texto)
    img.make(fit=True)
    buf = io.BytesIO()
    img.make_image(fill_color="#17414F", back_color="white").save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def ticket(codigo: str, detalle: str, validado: bool = False) -> None:
    estado = '<span class="estado ok">Validado</span>' if validado else '<span class="estado">Pendiente de recojo</span>'
    st.markdown(f'''<div class="ticket"><img src="data:image/png;base64,{qr(codigo)}" alt="Código QR del ticket {codigo}">
        <div>{estado}<div class="codigo">{codigo}</div>{detalle}</div></div>''', unsafe_allow_html=True)


def logo() -> str:
    return (f'<div class="marca-logo">{imagen("logo.svg", "Logo de Minka", "42px", "0")}'
            f'<div><div class="nombre">minka</div><div class="lema">{LEMA}</div></div></div>')


def video_portada(eyebrow: str, titulo: str, texto: str) -> bool:
    """Portada con video de fondo (app/static/portada.mp4), servido como archivo estático de Streamlit."""
    if not (ASSETS.parent / "static" / "portada.mp4").exists():
        return False
    st.markdown(f'''<div class="video-portada"><video autoplay muted loop playsinline poster="app/static/portada.jpg">
        <source src="app/static/portada.mp4" type="video/mp4"></video><div class="velo"></div>
        <div class="contenido"><span class="eyebrow">{eyebrow}</span><h1>{titulo}</h1>
        <p>{texto}</p></div></div>''', unsafe_allow_html=True)
    return True
