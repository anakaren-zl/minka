"""ReciclaGov. Cada recojo de reciclaje, registrado y premiado.

Modelo mixto. El reciclador registra cada recojo, el vecino gana por reciclar, la municipalidad
administra su Bono Verde sin papel y la empresa obtiene material reciclado trazable.

    streamlit run app/streamlit_app.py
"""
import json
import math
import sys
from pathlib import Path

import folium
import pandas as pd
import streamlit as st
from shapely.geometry import Point, shape
from streamlit_folium import st_folium

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "app"))

import estilo  # noqa: E402
from ai.asistente import responder  # noqa: E402
from ai.extraer import a_tabla, extraer  # noqa: E402
from backend import minam  # noqa: E402
from backend.bono import con_puntos, indicadores, padron_beneficiarios, resumen_viviendas  # noqa: E402
from backend.reglas import MATERIALES, ReglasBono  # noqa: E402
from mapas import mapa_satelital  # noqa: E402

DATA = RAIZ / "data"
DISTRITO = "150118"  # Lurigancho (Chosica), distrito piloto
P = estilo.PALETA
MESES = {"2026-09": "Septiembre 2026", "2026-10": "Octubre 2026", "2026-11": "Noviembre 2026"}

st.set_page_config(page_title="ReciclaGov", page_icon="♻️", layout="wide")
estilo.aplicar()


# ───────────────────────────────────────────────────────── datos
@st.cache_data
def cargar():
    padron = pd.read_csv(DATA / "padron_sintetico.csv")
    entregas = pd.read_csv(DATA / "entregas_sinteticas.csv")
    munis = pd.read_csv(DATA / "municipalidades_bono.csv", dtype={"ubigeo": str})
    mapa = json.loads((DATA / "lima_distritos.geojson").read_text(encoding="utf-8"))
    return padron, entregas, munis, mapa


padron, entregas_base, munis, mapa_lima = cargar()
st.session_state.setdefault("nuevas", [])
st.session_state.setdefault("chat", [])


def entregas_todas() -> pd.DataFrame:
    if not st.session_state.nuevas:
        return entregas_base
    return pd.concat([entregas_base, pd.DataFrame(st.session_state.nuevas)], ignore_index=True)


etiqueta = {r.codigo: f"{r.codigo}  ·  {r.direccion}" for r in padron[padron.inscrito].itertuples()}


def km(lat1, lon1, lat2, lon2) -> float:
    """Distancia en línea recta (haversine)."""
    p1, p2, dl = math.radians(lat1), math.radians(lat2), math.radians(lon2 - lon1)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(a))


# ───────────────────────────────────────────────────────── inicio
def inicio():
    estilo.portada("Bono Verde digital", "Reciclar en casa <em class='resalte'>ahora sí cuenta</em>",
                   "ReciclaGov registra cada recojo de reciclaje para que los vecinos ganen por separar sus "
                   "residuos, las municipalidades administren su Bono Verde sin papel y las empresas cuenten "
                   "con material reciclado trazable.", personaje=True)

    estilo.cinta(["<b>8</b> municipalidades con incentivo verificado en normas publicadas",
                  "<b>Art. 70</b> del D. L. 1278 permite descontar arbitrios a quien recicla",
                  "<b>20 %</b> de descuento en Villa El Salvador y Villa María del Triunfo",
                  "<b>15 %</b> en Lurigancho-Chosica desde 2024",
                  "<b>15 %</b> de PET reciclado exige la Ley 30884 en las botellas",
                  "<b>229 %</b> más reciclaje con incentivos digitales en Shanghái"])
    estilo.guia("vera", "Hola, vecino reciclador. Si necesitas ayuda, aquí estoy.")
    estilo.seccion("Diagnóstico", "El problema")
    estilo.fila_tarjetas([
        estilo.tarjeta("Un incentivo que ya existe", "La ley permite a las municipalidades descontar arbitrios "
                       "a quienes segregan, y distritos como Villa El Salvador, Lurigancho-Chosica o Sechura ya lo "
                       "aplican.", numero="Art. 70"),
        estilo.tarjeta("Pero todo se hace en papel", "Tickets semanales, padrones casa por casa, firmas y cruces "
                       "manuales con rentas cada dos meses. Cada municipalidad lo hace a su manera.", numero="12"),
        estilo.tarjeta("Y nadie tiene los datos", "Según un especialista del MINAM, el ministerio no sabe qué "
                       "municipalidades aplican el bono ni cómo les va.", numero="0"),
    ])
    st.markdown('<p class="nota">En Villa María del Triunfo se necesitan 12 tickets físicos para el descuento '
                'trimestral (Decreto de Alcaldía 010-2016-MVMT).</p>', unsafe_allow_html=True)

    estilo.seccion("Una sola herramienta, cuatro actores", "Cómo funciona")
    estilo.fila_tarjetas([
        estilo.tarjeta("El reciclador registra", "Escribe o dicta lo que recogió en cada casa. La inteligencia "
                       "artificial lo convierte en materiales y kilos.", paso="1"),
        estilo.tarjeta("El vecino gana", "Acumula EcoPuntos, ve cuánto le falta para su descuento y cómo va "
                       "frente a su barrio.", paso="2"),
        estilo.tarjeta("La municipalidad aplica", "Descarga el padrón de beneficiarios listo para el área de "
                       "rentas, sin cruzar papeles.", paso="3"),
        estilo.tarjeta("La empresa certifica", "Recibe kilos de PET y otros materiales verificados por distrito, "
                       "y con eso financia los premios.", paso="4"),
    ])

    estilo.seccion("Evidencia", "Por qué funciona")
    estilo.fila_tarjetas([
        estilo.tarjeta("El dinero motiva más", "En dos experimentos en China, el incentivo monetario fue el más "
                       "efectivo para reciclar (Lu y Wang, 2022).", numero="1.º"),
        estilo.tarjeta("Ver al vecino también", "Saber cuántos vecinos ya reciclan refuerza el efecto del incentivo "
                       "(Lu y Wang, 2022).", numero="+"),
        estilo.tarjeta("Lo digital multiplica", "Un sistema digital de incentivos en Shanghái aumentó la "
                       "recolección en 229 % en una comunidad piloto (Zhou et al., 2021).", numero="229 %"),
    ])


# ───────────────────────────────────────────────────────── tu municipalidad
def tu_municipalidad():
    estilo.portada("Encuentra tu municipalidad", "¿Tu distrito premia el reciclaje?",
                   "Haz clic en el mapa sobre tu distrito o elígelo en la lista. Te mostramos si tiene un "
                   "incentivo vigente, qué norma lo respalda y cuál es el programa más cercano.")
    estilo.guia("ciclo", "Toca tu distrito en el mapa y te cuento si premian el reciclaje.")
    nombres = sorted({f["properties"]["NOMBDIST"].title() for f in mapa_lima["features"]})
    izq, der = st.columns([3, 2], gap="large")
    with izq:
        m = mapa_satelital([-12.03, -76.95], 10)
        folium.GeoJson(mapa_lima, name="Distritos",
                       style_function=lambda _: {"color": P["hoja"], "weight": 1.2, "fillOpacity": 0.05},
                       highlight_function=lambda _: {"fillColor": P["hoja"], "fillOpacity": 0.35},
                       tooltip=folium.GeoJsonTooltip(["NOMBDIST"], labels=False)).add_to(m)
        for r in munis.itertuples():
            folium.CircleMarker([r.lat, r.lon], radius=8, color="#FFFFFF", weight=2, fill=True,
                                fill_color=P["hoja"], fill_opacity=1,
                                tooltip=f"{r.municipalidad}  ·  {r.incentivo}").add_to(m)
        clic = st_folium(m, height=520, use_container_width=True, returned_objects=["last_clicked"])
    elegido = None
    if clic and clic.get("last_clicked"):
        punto = Point(clic["last_clicked"]["lng"], clic["last_clicked"]["lat"])
        elegido = next((f["properties"] for f in mapa_lima["features"] if shape(f["geometry"]).contains(punto)), None)
    with der:
        lista = st.selectbox("O elige tu distrito", ["Elige un distrito"] + nombres,
                             index=0 if not elegido else nombres.index(elegido["NOMBDIST"].title()) + 1)
        if lista != "Elige un distrito":
            elegido = next(f["properties"] for f in mapa_lima["features"] if f["properties"]["NOMBDIST"].title() == lista)
        if not elegido:
            st.markdown('<div class="banda">Los puntos verdes marcan las municipalidades con un incentivo por '
                        'reciclar que encontramos en normas publicadas.</div>', unsafe_allow_html=True)
            return
        fila = munis[munis.ubigeo == elegido["IDDIST"]]
        poligono = next(shape(f["geometry"]) for f in mapa_lima["features"] if f["properties"]["IDDIST"] == elegido["IDDIST"])
        st.markdown(f"### {elegido['NOMBDIST'].title()}")
        if len(fila):
            r = fila.iloc[0]
            st.markdown(f'<span class="etiqueta">{r.incentivo}</span><span class="etiqueta">{r.estado}</span>',
                        unsafe_allow_html=True)
            st.markdown(estilo.tarjeta(r.descuento, f"{r.como_se_gana}. Norma {r.norma} ({r.anio})."),
                        unsafe_allow_html=True)
            st.link_button("Ver la norma", r.fuente)
        else:
            st.markdown('<span class="etiqueta alerta">Sin incentivo registrado</span>', unsafe_allow_html=True)
            st.write("No encontramos una ordenanza publicada que dé descuento en arbitrios por reciclar en este "
                     "distrito. Eso no significa que no exista, así que vale la pena preguntar.")
        c = poligono.centroid
        cercanas = munis.assign(km=[km(c.y, c.x, a, b) for a, b in zip(munis.lat, munis.lon)])
        cercanas = cercanas[cercanas.ubigeo != elegido["IDDIST"]].nsmallest(1, "km").iloc[0]
        st.markdown(f'<div class="banda">El programa más cercano es <b>{cercanas.incentivo}</b> de '
                    f'{cercanas.municipalidad}, a unos {cercanas.km:.0f} km.</div>', unsafe_allow_html=True)
        st.markdown('<p class="nota">Base legal general. Artículo 70 del Decreto Legislativo 1278, modificado '
                    'por el Decreto Legislativo 1501.</p>', unsafe_allow_html=True)


# ───────────────────────────────────────────────────────── vecino
def vecino():
    estilo.portada("Para vecinos", "Mi Bono Verde",
                   "Revisa tus EcoPuntos, cuánto te falta para tu descuento y cómo va tu barrio.")
    estilo.guia("vera", "Con cuatro entregas al mes ganas tu descuento. ¿Te ayudo a separar mejor?")
    reglas = ReglasBono()
    c1, c2 = st.columns([2, 1])
    codigo = c1.selectbox("Mi vivienda", list(etiqueta), format_func=etiqueta.get, index=4)
    nuevo = any(n["codigo"] == codigo for n in st.session_state.nuevas)
    mes = c2.selectbox("Mes", ["2026-10", "2026-11"], index=1 if nuevo else 0, format_func=MESES.get)
    res = resumen_viviendas(padron, entregas_todas(), mes, reglas)
    yo = res[res.codigo == codigo].iloc[0]
    sector = res[(res.sector == yo.sector) & res.inscrito]
    barrio = res[res.sector == yo.sector]

    m1, m2, m3 = st.columns(3)
    m1.metric("EcoPuntos del mes", f"{int(yo.puntos)}")
    m2.metric("Entregas válidas", f"{int(yo.entregas_validas)} de {reglas.entregas_minimas}")
    m3.metric("Descuento en limpieza pública", f"S/ {yo.arbitrio_limpieza * reglas.descuento:.2f}",
              "ganado" if yo.cumple else "en camino", delta_color="normal" if yo.cumple else "off")
    st.progress(min(yo.entregas_validas / reglas.entregas_minimas, 1.0),
                text="Ganaste tu Bono Verde este mes" if yo.cumple else
                f"Te faltan {int(reglas.entregas_minimas - yo.entregas_validas)} entregas para tu descuento")

    participan = (barrio.entregas > 0).mean()
    st.markdown(f'<div class="banda"><b>{round(participan * 10)} de cada 10</b> hogares de {yo.sector} '
                f'ya reciclaron este mes. {"Tú eres parte de ellos." if yo.entregas > 0 else "Súmate esta semana."}'
                f'</div>', unsafe_allow_html=True)
    izq, der = st.columns(2, gap="large")
    with izq:
        st.markdown("#### Tú y tu barrio")
        st.bar_chart(pd.DataFrame({"kg": [yo.kg, sector.kg.mean()]}, index=["Mi vivienda", f"Promedio de {yo.sector}"]),
                     color=P["rio"], horizontal=True, height=200)
    with der:
        st.markdown("#### Mis entregas del mes")
        mias = con_puntos(entregas_todas())
        mias = mias[(mias.codigo == codigo) & (mias.mes == mes)]
        if mias.empty:
            st.write("Aún no tienes entregas este mes.")
        else:
            t = mias.groupby(["fecha", "id_entrega"]).agg(kg=("kg", "sum"), puntos=("puntos", "sum")).reset_index()
            st.dataframe(t.rename(columns={"fecha": "Fecha", "id_entrega": "Entrega", "kg": "Kilos", "puntos": "EcoPuntos"}),
                         hide_index=True, width="stretch", height=200)


# ───────────────────────────────────────────────────────── reciclador
def reciclador():
    estilo.portada("Para recicladores", "Registra un recojo en segundos",
                   "Escribe la entrega como la dirías en voz alta. La inteligencia artificial la convierte en un "
                   "registro verificable que reemplaza al ticket en papel.")
    estilo.guia("ciclo", "Escribe como hablas, yo me encargo de ordenar los kilos.")
    izq, der = st.columns(2, gap="large")
    with izq:
        vivienda = st.selectbox("Vivienda", list(etiqueta), format_func=etiqueta.get, index=4)
        fecha = st.date_input("Fecha del recojo", value=pd.Timestamp("2026-11-09"), format="DD/MM/YYYY")
        nota = st.text_area("Lo que entregó el vecino", height=120,
                            value="3 kilos de cartón, 12 botellas de plástico y 5 latas, todo limpio y separado")
        procesar = st.button("Registrar recojo", type="primary", width="stretch")
    with der:
        if not (procesar and nota.strip()):
            st.markdown(estilo.tarjeta("Así queda el registro", "Materiales, kilos y EcoPuntos, con una marca de si "
                                       "la entrega vino bien separada. Prueba a escribir que vino mezclada."),
                        unsafe_allow_html=True)
            return
        with st.spinner("Leyendo la nota"):
            entrega, motor = extraer(nota)
        filas = a_tabla(entrega)
        if not filas:
            st.warning("No encontré materiales en la nota. Prueba con algo como 2 kilos de cartón y 8 botellas.")
            return
        id_entrega = f"N-{len(st.session_state.nuevas) + 1:04d}"
        for f in filas:
            st.session_state.nuevas.append({
                "id_entrega": id_entrega, "fecha": fecha.isoformat(), "codigo": vivienda, "reciclador": "REC-01",
                "material": f["material"], "kg": f["kg"], "bien_segregado": entrega.bien_segregado,
                "fuente": "registrado en la app"})
        motor_txt = "Leído por Gemini" if motor == "gemini" else "Leído por reglas de respaldo"
        st.markdown(f'<span class="etiqueta">{id_entrega}</span><span class="etiqueta">{motor_txt}</span>',
                    unsafe_allow_html=True)
        tabla = pd.DataFrame(filas).drop(columns="material").rename(columns={"kg": "Kilos"})
        st.dataframe(tabla, hide_index=True, width="stretch")
        k1, k2 = st.columns(2)
        k1.metric("Kilos recuperados", f"{tabla.Kilos.sum():.1f}")
        k2.metric("EcoPuntos", f"{int(tabla.EcoPuntos.sum()) if entrega.bien_segregado else 0}")
        if entrega.bien_segregado:
            st.success("Entrega válida. Ya cuenta para el Bono Verde del vecino.")
        else:
            st.error("Entrega mezclada. Queda registrada, pero no suma puntos.")


# ───────────────────────────────────────────────────────── municipalidad
def municipalidad():
    estilo.portada("Para municipalidades", "Tablero de Lurigancho-Chosica",
                   "Piloto con datos sintéticos. Ajusta las reglas de tu ordenanza, mira el avance en el mapa y "
                   "descarga el padrón de beneficiarios para el área de rentas.")
    estilo.guia("ciclo", "El padrón ya está listo para rentas. Sin tickets ni firmas.")
    c1, c2, c3 = st.columns(3)
    mes = c1.selectbox("Periodo", ["2026-10", "2026-09", "2026-11"], format_func=MESES.get)
    reglas = ReglasBono(entregas_minimas=c2.slider("Entregas mínimas al mes", 1, 5, 4),
                        descuento=c3.slider("Descuento en limpieza pública (%)", 5, 30, 15) / 100)
    res = resumen_viviendas(padron, entregas_todas(), mes, reglas)
    ind = indicadores(res)
    k = st.columns(5)
    k[0].metric("Viviendas inscritas", ind["inscritas"])
    k[1].metric("Participaron", ind["participan"])
    k[2].metric("Ganan el bono", ind["beneficiarias"])
    k[3].metric("Toneladas recuperadas", f"{ind['kg'] / 1000:.2f}")
    k[4].metric("Descuento a otorgar", f"S/ {ind['descuento_total']:,.0f}")

    izq, der = st.columns([3, 2], gap="large")
    with izq:
        st.markdown("#### Viviendas del programa")
        m = mapa_satelital([-11.975, -76.83], 12)
        lur = [f for f in mapa_lima["features"] if f["properties"]["IDDIST"] == DISTRITO]
        folium.GeoJson({"type": "FeatureCollection", "features": lur},
                       style_function=lambda _: {"color": P["hoja"], "weight": 2.5, "fillOpacity": 0}).add_to(m)
        for r in res[res.inscrito].itertuples():
            color = P["hoja"] if r.cumple else (P["laguna"] if r.entregas > 0 else "#FFFFFF")
            folium.CircleMarker([r.lat, r.lon], radius=5, color=P["noche"], weight=1, fill=True, fill_color=color,
                                fill_opacity=1, tooltip=f"{r.codigo}  ·  {r.sector}  ·  {int(r.entregas_validas)} "
                                                        f"entregas válidas").add_to(m)
        st_folium(m, height=430, use_container_width=True, returned_objects=[])
        st.markdown('<p class="nota">Verde lima, gana el bono. Celeste, participa pero aún no cumple. Blanco, '
                    'inscrita sin entregas.</p>', unsafe_allow_html=True)
    with der:
        st.markdown("#### Qué se recicla")
        mat = con_puntos(entregas_todas())
        mat = mat[mat.mes == mes].groupby("material").kg.sum().rename(index=lambda x: MATERIALES[x]["nombre"])
        st.bar_chart(mat.sort_values(), color=P["rio"], horizontal=True, height=230)
        st.markdown("#### Participación por sector")
        sec = res[res.inscrito].groupby("sector").agg(Inscritas=("codigo", "size"), **{"Con bono": ("cumple", "sum")})
        st.bar_chart(sec, color=[P["noche"], P["hoja"]], stack=False, height=230)

    estilo.seccion("Listo para rentas", "Padrón de beneficiarios")
    st.markdown('<p class="nota">Este archivo reemplaza el cruce manual de tickets, firmas y padrones en papel.</p>',
                unsafe_allow_html=True)
    benef = padron_beneficiarios(res)
    st.dataframe(benef, hide_index=True, width="stretch", height=260)
    st.download_button("Descargar padrón en CSV", benef.to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"padron-bono-verde-{mes}.csv", mime="text/csv", type="primary")

    contexto = minam.cargar(DATA)
    if contexto is not None:
        st.markdown("#### El distrito en los datos abiertos del MINAM")
        minam.mostrar(contexto, mapa_lima, DISTRITO, ind["kg"])


# ───────────────────────────────────────────────────────── empresa
def empresa():
    estilo.portada("Para empresas", "Material reciclado con trazabilidad",
                   "Kilos recuperados y verificados, por material, distrito y mes. Sirven para tus reportes de "
                   "sostenibilidad y para demostrar el origen del PET reciclado que exige la Ley 30884.")
    estilo.guia("vera", "Cada kilo que ves aquí lo separó un vecino de verdad.")
    c1, c2 = st.columns([2, 1])
    nombres = {k: v["nombre"] for k, v in MATERIALES.items() if k != "organico"}
    elegidos = c1.multiselect("Materiales", list(nombres), default=["plastico_pet"], format_func=nombres.get)
    mes = c2.selectbox("Periodo", ["2026-10", "2026-09", "2026-11"], format_func=MESES.get, key="mes_emp")
    e = con_puntos(entregas_todas())
    e = e[(e.mes == mes) & e.material.isin(elegidos) & e.bien_segregado].merge(padron[["codigo", "sector"]], on="codigo")

    k = st.columns(4)
    k[0].metric("Kilos verificados", f"{e.kg.sum():,.1f}")
    k[1].metric("Recojos registrados", f"{e.id_entrega.nunique()}")
    k[2].metric("Hogares participantes", f"{e.codigo.nunique()}")
    k[3].metric("Recicladores formalizados", f"{e.reciclador.nunique()}")

    izq, der = st.columns([3, 2], gap="large")
    with izq:
        st.markdown("#### Kilos por semana")
        st.bar_chart(e.groupby("fecha").kg.sum(), color=P["rio"], height=260)
    with der:
        st.markdown("#### Cuánto costaría")
        precio = st.number_input("Precio por tonelada trazada (S/, supuesto)", 50, 1000, 300, step=50)
        premios = st.slider("Parte que financia premios a vecinos (%)", 0, 80, 40)
        total = e.kg.sum() / 1000 * precio
        st.markdown(estilo.tarjeta("Pago del mes", f"De este monto, S/ {total * premios / 100:,.0f} van a premios "
                                   f"para los vecinos y el resto sostiene la plataforma.", numero=f"S/ {total:,.0f}"),
                    unsafe_allow_html=True)

    estilo.seccion("Para tus reportes", "Certificado de trazabilidad")
    st.markdown('<p class="nota">Totales por distrito, sector y material. Nunca incluye nombres ni direcciones.</p>',
                unsafe_allow_html=True)
    cert = (e.assign(Distrito="Lurigancho-Chosica", Material=e.material.map(nombres))
            .groupby(["Distrito", "sector", "Material"])
            .agg(Recojos=("id_entrega", "nunique"), Hogares=("codigo", "nunique"), Kilos=("kg", "sum")).reset_index()
            .rename(columns={"sector": "Sector"}))
    cert["Kilos"] = cert.Kilos.round(1)
    st.dataframe(cert, hide_index=True, width="stretch")
    st.download_button("Descargar certificado en CSV", cert.to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"certificado-trazabilidad-{mes}.csv", mime="text/csv", type="primary")


# ───────────────────────────────────────────────────────── asistente
def asistente():
    estilo.portada("Asistente", "Pregúntale a <em class='resalte'>Vera</em>",
                   "Vera resuelve tus dudas sobre el Bono Verde con lo que dicen las ordenanzas, la ley y la guía "
                   "de ReciclaGov. Si algo no está en la guía, te lo dice.")
    izq, der = st.columns([1, 2.4], gap="large")
    with izq:
        st.markdown(estilo.imagen("vera.jpg", "Vera, vecina guía de ReciclaGov"), unsafe_allow_html=True)
        st.markdown("#### Preguntas frecuentes")
        for sugerida in ["¿Cuánto descuento me dan?", "¿Cómo separo bien mis residuos?",
                         "Mi distrito no tiene Bono Verde", "¿Quién paga los premios?", "¿Mis datos están protegidos?"]:
            if st.button(sugerida, width="stretch"):
                st.session_state.pendiente = sugerida
    with der:
        pregunta = st.session_state.pop("pendiente", None)
        if pregunta:
            texto, fuentes, _ = responder(pregunta)
            st.session_state.chat += [("user", pregunta, []), ("assistant", texto, fuentes)]
        estilo.chat(st.session_state.chat)
        escrita = st.chat_input("Escribe tu duda sobre el Bono Verde")
        if escrita:
            st.session_state.pendiente = escrita
            st.rerun()


# ───────────────────────────────────────────────────────── navegación
paginas = [
    st.Page(inicio, title="Inicio", default=True, url_path="inicio"),
    st.Page(tu_municipalidad, title="Tu municipalidad", url_path="municipalidad-cercana"),
    st.Page(vecino, title="Vecino", url_path="vecino"),
    st.Page(reciclador, title="Reciclador", url_path="reciclador"),
    st.Page(municipalidad, title="Municipalidad", url_path="municipalidad"),
    st.Page(empresa, title="Empresa", url_path="empresa"),
    st.Page(asistente, title="Pregúntale a Vera", url_path="asistente"),
]
st.navigation(paginas, position="top").run()
estilo.pie()
