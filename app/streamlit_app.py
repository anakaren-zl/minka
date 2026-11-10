"""ReciclaGov: el Bono Verde municipal, sin papel.

Tres vistas para tres actores:
- Reciclador: registra cada recojo escribiendo como habla; la IA lo estructura.
- Vecino: ve sus EcoPuntos, cuánto le falta para el bono y cómo va frente a su sector.
- Municipalidad: tablero con mapa, reglas de la ordenanza y padrón de beneficiarios listo.

    streamlit run app/streamlit_app.py
"""
import json
import sys
from pathlib import Path

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from ai.extraer import a_tabla, extraer  # noqa: E402
from backend import minam  # noqa: E402
from backend.bono import indicadores, padron_beneficiarios, resumen_viviendas  # noqa: E402
from backend.reglas import MATERIALES, ReglasBono  # noqa: E402

DATA = RAIZ / "data"
DISTRITO = "150118"  # Lurigancho (Chosica), distrito piloto
VERDE, AZUL, ARENA = "#2E7D5B", "#1F4E79", "#E9B44C"

st.set_page_config(page_title="ReciclaGov", page_icon="♻️", layout="wide")

# ───────────────────────────────────────────────────────── estilo
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;900&display=swap');
html, body, [class*="css"], .stMarkdown, .stText, button, input, textarea { font-family: 'Montserrat', sans-serif; }
h1, h2, h3 { font-family: 'Montserrat', sans-serif; font-weight: 900 !important; color: #1F4E79; }
.hero { background: linear-gradient(120deg, #1F4E79 0%, #2E7D5B 100%); color: white;
        padding: 1.6rem 2rem; border-radius: 18px; margin-bottom: 1.2rem; }
.hero h1 { color: white; margin: 0; font-size: 2.6rem; }
.hero p { margin: .3rem 0 0 0; font-weight: 400; font-size: 1.05rem; opacity: .95; }
.chip { display: inline-block; padding: .15rem .7rem; border-radius: 999px; font-size: .8rem;
        font-weight: 600; background: #E9B44C; color: #1F4E79; margin-right: .4rem; }
div[data-testid="stMetricValue"] { font-weight: 900; color: #2E7D5B; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>♻️ ReciclaGov</h1>
  <p>Digitalizamos el Bono Verde para que las municipalidades verifiquen y premien con descuentos
  en arbitrios a los vecinos que reciclan, sin padrones ni tickets en papel.</p>
</div>
""", unsafe_allow_html=True)


# ───────────────────────────────────────────────────────── datos
@st.cache_data
def cargar():
    padron = pd.read_csv(DATA / "padron_sintetico.csv")
    entregas = pd.read_csv(DATA / "entregas_sinteticas.csv")
    mapa = json.loads((DATA / "lima_distritos.geojson").read_text(encoding="utf-8"))
    return padron, entregas, mapa


padron, entregas_base, mapa_lima = cargar()
if "nuevas" not in st.session_state:
    st.session_state.nuevas = []  # entregas registradas en esta sesión de la demo


def entregas_todas() -> pd.DataFrame:
    if not st.session_state.nuevas:
        return entregas_base
    return pd.concat([entregas_base, pd.DataFrame(st.session_state.nuevas)], ignore_index=True)


etiqueta = {r.codigo: f"{r.codigo} · {r.direccion}" for r in padron[padron.inscrito].itertuples()}

tab_rec, tab_vec, tab_mun, tab_info = st.tabs(
    ["🚲 Reciclador", "🏠 Vecino", "🏛️ Municipalidad", "ℹ️ Cómo funciona"])

# ───────────────────────────────────────────────────────── reciclador
with tab_rec:
    st.subheader("Registrar un recojo")
    st.caption("Escribe la entrega como la dirías en voz alta. La IA la convierte en un registro verificable "
               "que reemplaza al ticket en papel.")
    c1, c2 = st.columns([1, 1])
    with c1:
        vivienda = st.selectbox("Vivienda", list(etiqueta), format_func=etiqueta.get, key="viv_rec")
        fecha = st.date_input("Fecha del recojo", value=pd.Timestamp("2026-11-09"))
        nota = st.text_area("¿Qué entregó el vecino?", height=110,
                            value="3 kilos de cartón, 12 botellas de plástico y 5 latas, todo limpio y separado")
        procesar = st.button("Registrar recojo", type="primary", width="stretch")
    with c2:
        if procesar and nota.strip():
            with st.spinner("Estructurando la entrega..."):
                entrega, motor = extraer(nota)
            filas = a_tabla(entrega)
            if not filas:
                st.warning("No encontré materiales en la nota. Prueba con algo como «2 kilos de cartón y 8 botellas».")
            else:
                id_entrega = f"N-{len(st.session_state.nuevas) + 1:04d}"
                for f in filas:
                    st.session_state.nuevas.append({
                        "id_entrega": id_entrega, "fecha": fecha.isoformat(), "codigo": vivienda,
                        "reciclador": "REC-01", "material": f["material"], "kg": f["kg"],
                        "bien_segregado": entrega.bien_segregado, "fuente": "registrado en la app"})
                st.markdown(f"<span class='chip'>{'🤖 Gemini' if motor == 'gemini' else '⚙️ Reglas'}</span>"
                            f"<span class='chip'>{id_entrega}</span>", unsafe_allow_html=True)
                tabla = pd.DataFrame(filas).drop(columns="material")
                st.dataframe(tabla, hide_index=True, width="stretch")
                total = int(tabla.EcoPuntos.sum()) if entrega.bien_segregado else 0
                k1, k2 = st.columns(2)
                k1.metric("kg recuperados", f"{tabla.kg.sum():.1f}")
                k2.metric("EcoPuntos", total)
                if entrega.bien_segregado:
                    st.success("Entrega válida: cuenta para el Bono Verde del vecino.")
                else:
                    st.error("Entrega mal segregada: queda registrada, pero no suma puntos.")
                if entrega.observacion:
                    st.caption(f"Observación: {entrega.observacion}")
        else:
            st.info("Aquí aparecerá el registro estructurado: materiales, kg y EcoPuntos.")

# ───────────────────────────────────────────────────────── vecino
reglas = ReglasBono()
with tab_vec:
    st.subheader("Mi Bono Verde")
    codigo = st.selectbox("Mi vivienda", list(etiqueta), format_func=etiqueta.get, key="viv_vec", index=4)
    mes = "2026-11" if any(n["codigo"] == codigo for n in st.session_state.nuevas) else "2026-10"
    mes = st.radio("Mes", ["2026-10", "2026-11"], index=["2026-10", "2026-11"].index(mes), horizontal=True,
                   format_func={"2026-10": "Octubre 2026", "2026-11": "Noviembre 2026"}.get)
    res = resumen_viviendas(padron, entregas_todas(), mes, reglas)
    yo = res[res.codigo == codigo].iloc[0]
    sector = res[(res.sector == yo.sector) & res.inscrito]

    m1, m2, m3 = st.columns(3)
    m1.metric("EcoPuntos del mes", int(yo.puntos))
    m2.metric("Entregas válidas", f"{int(yo.entregas_validas)} de {reglas.entregas_minimas}")
    m3.metric("Descuento en arbitrios", f"S/ {yo.arbitrio_limpieza * reglas.descuento:.2f}",
              "ganado" if yo.cumple else "aún no", delta_color="normal" if yo.cumple else "off")
    st.progress(min(yo.entregas_validas / reglas.entregas_minimas, 1.0),
                text="¡Ganaste tu Bono Verde este mes! 🎉" if yo.cumple else
                f"Te faltan {int(reglas.entregas_minimas - yo.entregas_validas)} entregas para tu descuento")

    st.markdown(f"#### Tu sector: {yo.sector}")
    promedio = sector.kg.mean()
    st.write(f"Este mes reciclaste **{yo.kg:.1f} kg**. El promedio de las viviendas inscritas de {yo.sector} "
             f"es **{promedio:.1f} kg**, y **{int(sector.cumple.sum())} de {len(sector)}** ya ganaron su bono.")
    st.bar_chart(pd.DataFrame({"kg": [yo.kg, promedio]}, index=["Mi vivienda", f"Promedio de {yo.sector}"]),
                 color=VERDE, horizontal=True, height=180)

# ───────────────────────────────────────────────────────── municipalidad
with tab_mun:
    st.subheader("Tablero de la Municipalidad de Lurigancho-Chosica (piloto)")
    cfg1, cfg2, cfg3 = st.columns(3)
    mes_m = cfg1.selectbox("Periodo", ["2026-10", "2026-09", "2026-11"],
                           format_func={"2026-09": "Septiembre 2026", "2026-10": "Octubre 2026",
                                        "2026-11": "Noviembre 2026"}.get)
    reglas_m = ReglasBono(
        entregas_minimas=cfg2.slider("Entregas mínimas al mes (ordenanza)", 1, 5, 4),
        descuento=cfg3.slider("Descuento en limpieza pública (%)", 5, 30, 15) / 100,
    )
    res_m = resumen_viviendas(padron, entregas_todas(), mes_m, reglas_m)
    ind = indicadores(res_m)

    k = st.columns(5)
    k[0].metric("Viviendas inscritas", ind["inscritas"])
    k[1].metric("Participaron en el mes", ind["participan"])
    k[2].metric("Ganan el bono", ind["beneficiarias"])
    k[3].metric("Toneladas recuperadas", f"{ind['kg'] / 1000:.2f}")
    k[4].metric("Descuento a otorgar", f"S/ {ind['descuento_total']:,.0f}")

    izq, der = st.columns([3, 2])
    with izq:
        st.markdown("#### Viviendas del programa")
        m = folium.Map(location=[-11.975, -76.83], zoom_start=12, tiles="OpenStreetMap")
        lur = [f for f in mapa_lima["features"] if f["properties"]["IDDIST"] == DISTRITO]
        folium.GeoJson({"type": "FeatureCollection", "features": lur},
                       style_function=lambda _: {"color": AZUL, "weight": 2, "fillOpacity": 0.04}).add_to(m)
        for r in res_m[res_m.inscrito].itertuples():
            color = VERDE if r.cumple else (ARENA if r.entregas > 0 else "#B0B7C3")
            folium.CircleMarker([r.lat, r.lon], radius=5, color=color, fill=True, fill_opacity=0.9,
                                tooltip=f"{r.codigo} · {r.sector} · {int(r.entregas_validas)} entregas válidas").add_to(m)
        st_folium(m, height=420, use_container_width=True, returned_objects=[])
        st.caption("🟢 gana el bono · 🟡 participa pero aún no cumple · ⚪ inscrita sin entregas")
    with der:
        st.markdown("#### ¿Qué se recicla?")
        mat = entregas_todas().assign(mes=lambda d: d.fecha.astype(str).str[:7])
        mat = mat[mat.mes == mes_m].groupby("material").kg.sum().rename(index=lambda x: MATERIALES[x]["nombre"])
        st.bar_chart(mat.sort_values(), color=VERDE, horizontal=True, height=220)
        st.markdown("#### Participación por sector")
        sec = res_m[res_m.inscrito].groupby("sector").agg(inscritas=("codigo", "size"), con_bono=("cumple", "sum"))
        st.bar_chart(sec, color=[AZUL, VERDE], stack=False, height=220)

    st.markdown("#### Padrón de beneficiarios para el área de rentas")
    st.caption("Este archivo reemplaza el cruce manual de tickets, firmas y padrones en papel.")
    benef = padron_beneficiarios(res_m)
    st.dataframe(benef, hide_index=True, width="stretch", height=260)
    st.download_button("⬇️ Descargar padrón (CSV)", benef.to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"padron_bono_verde_{mes_m}.csv", mime="text/csv", type="primary")

    st.markdown("#### El distrito en los datos abiertos del MINAM")
    contexto = minam.cargar(DATA)
    if contexto is None:
        st.info("Coloca el CSV de generación de residuos del MINAM en data/ para ver el contexto distrital.")
    else:
        minam.mostrar(contexto, mapa_lima, DISTRITO, ind["kg"])

# ───────────────────────────────────────────────────────── información
with tab_info:
    st.subheader("Cómo funciona")
    st.markdown("""
1. **El reciclador** registra cada recojo desde su celular, escribiendo como habla. Un LLM (Gemini, con
   salidas estructuradas) lo convierte en materiales, kg y una marca de si la entrega vino bien segregada.
2. **El vecino** ve sus EcoPuntos, cuántas entregas le faltan para el bono y cómo va frente a su sector.
3. **La municipalidad** fija las reglas de su ordenanza, ve el mapa del programa y descarga el padrón de
   beneficiarios que hoy se arma a mano.

**Base legal.** Artículo 70 del Decreto Legislativo N.° 1278, modificado por el D. L. N.° 1501: las
municipalidades pueden otorgar descuentos en arbitrios a quienes segregan en la fuente.

**Datos.** Las viviendas y entregas son **sintéticas** (no hay datos personales reales). El mapa distrital
es el del curso y el contexto distrital viene de los datos abiertos del MINAM.
""")
