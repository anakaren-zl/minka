"""ReciclaGov. Cada recojo de reciclaje, registrado y premiado.

Modelo mixto. El reciclador registra cada recojo, el vecino gana por reciclar, la municipalidad
administra su Bono Verde sin papel y la empresa obtiene sus envases de vuelta con trazabilidad.

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

import componentes as ui  # noqa: E402
import estilo  # noqa: E402
import recicla  # noqa: E402
from ai.asistente import responder  # noqa: E402
from backend import minam  # noqa: E402
from backend.bono import con_puntos, indicadores, padron_beneficiarios, resumen_viviendas  # noqa: E402
from backend.reglas import EMPRESAS, MATERIALES, SIN_MARCA, ReglasBono  # noqa: E402
from mapas import mapa_satelital  # noqa: E402

DATA = RAIZ / "data"
DISTRITO = "150118"  # Lurigancho (Chosica), distrito piloto
P = estilo.PALETA
MESES = {"2026-09": "Septiembre", "2026-10": "Octubre", "2026-11": "Noviembre"}

st.set_page_config(page_title="ReciclaGov", page_icon=str(RAIZ / "app" / "assets" / "logo.svg"), layout="wide")
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
recicla.iniciar(padron)


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


def elegir_mes(clave: str, por_defecto: str = "2026-10") -> str:
    mes = st.segmented_control("Mes", list(MESES), format_func=MESES.get, default=por_defecto, key=clave)
    return mes or por_defecto


# ───────────────────────────────────────────────────────── inicio
def inicio():
    titulo = "Reciclar en casa <em class='resalte'>ahora sí cuenta</em>"
    texto = ("Conectamos a vecinos, recicladores, municipalidades y empresas para que cada botella, lata o caja que "
             "se separa en casa quede registrada, premiada y de vuelta en la economía.")
    if not estilo.video_portada("Bono Verde digital", titulo, texto):
        estilo.portada("Bono Verde digital", titulo, texto, personaje=True)
    a, b, _ = st.columns([1.1, 1.3, 3])
    with a, st.container(key="cta-recicla"):
        st.page_link(PAG["recicla"], label="Recicla ahora", icon=":material/recycling:")
    with b, st.container(key="cta-muni"):
        st.page_link(PAG["muni"], label="¿Mi distrito premia?", icon=":material/location_on:")
    estilo.cinta(["<b>8</b> municipalidades con incentivo verificado en normas publicadas",
                  "<b>Art. 70</b> del D. L. 1278 permite descontar arbitrios a quien recicla",
                  "<b>20 %</b> de descuento en Villa El Salvador y Villa María del Triunfo",
                  "<b>15 %</b> en Lurigancho-Chosica desde 2024",
                  "<b>15 %</b> de PET reciclado exige la Ley 30884 en las botellas",
                  "<b>229 %</b> más reciclaje con incentivos digitales en Shanghái"])
    estilo.guia("vera", "Hola, vecino reciclador. Si necesitas ayuda, aquí estoy.")

    estilo.seccion("Nuestra historia", "Empezó con una bolsa de botellas")
    st.markdown(f'''<div class="historia"><div class="foto">{estilo.imagen("vera.png", "Vera", radio="0")}</div><div>
        <blockquote>«Separaba mis botellas todas las semanas y se las daba al reciclador. Un día me dijeron que con los
        tickets tenía descuento en mis arbitrios, pero los tickets se perdían y nadie sabía cuántos tenía.»</blockquote>
        <div class="firma">Vera, vecina de Carapongo · personaje de ReciclaGov inspirado en las conversaciones con usuarios</div>
        <p>La historia de Vera resume lo que encontramos al investigar. El Perú ya tiene un incentivo que premia a quien
        recicla, pero se administra con papel, cada municipalidad lo hace a su manera y casi ningún vecino lo conoce.
        ReciclaGov nace para que ese esfuerzo diario quede registrado y valga.</p></div></div>''', unsafe_allow_html=True)

    estilo.seccion("Lo que nos mueve", "Misión, visión y valores")
    estilo.fila_tarjetas([
        estilo.tarjeta("Misión", "Hacer que reciclar en casa sea fácil, visible y premiado, conectando a vecinos, "
                       "recicladores formalizados, municipalidades y empresas en un solo registro confiable.", numero="01"),
        estilo.tarjeta("Visión", "Un Perú donde cada envase que sale al mercado vuelve a la economía y donde el trabajo de "
                       "los recicladores es reconocido, medido y bien pagado.", numero="02"),
    ])
    st.write("")
    valores = [("T", "Transparencia", "Cada kilo se registra con fecha, lugar y marca."),
               ("D", "Dignidad", "El reciclador formalizado valida cada recojo y su trabajo queda registrado."),
               ("C", "Corresponsabilidad", "Estado, empresas y vecinos comparten el costo y el beneficio."),
               ("E", "Evidencia", "Decidimos con datos, no con supuestos.")]
    cols = st.columns(4)
    for c, (ic, t, x) in zip(cols, valores):
        c.markdown(f'<div class="valor"><div class="ic">{ic}</div><div><b style="color:#234257;font-weight:900">{t}</b>'
                   f'<br><span style="font-size:.86rem">{x}</span></div></div>', unsafe_allow_html=True)

    estilo.seccion("Diagnóstico", "El problema que resolvemos")
    estilo.fila_tarjetas([
        estilo.tarjeta("Un incentivo que ya existe", "La ley permite a las municipalidades descontar arbitrios a quienes "
                       "segregan. Villa El Salvador, Lurigancho-Chosica y Sechura ya lo aplican.", numero="Art. 70"),
        estilo.tarjeta("Pero todo se hace en papel", "Tickets semanales, padrones casa por casa, firmas y cruces manuales "
                       "con rentas. En Villa María del Triunfo se necesitan 12 tickets para el descuento.", numero="12"),
        estilo.tarjeta("Y nadie tiene los datos", "Un especialista del MINAM nos confirmó que el ministerio no sabe qué "
                       "municipalidades aplican el bono ni cómo les va.", numero="0"),
    ])

    estilo.seccion("Una sola herramienta, cuatro actores", "Cómo funciona")
    estilo.fila_tarjetas([
        estilo.tarjeta("El vecino recicla", "Marca lo que separó, elige el día del recojo y recibe un ticket digital con QR.",
                       paso="1"),
        estilo.tarjeta("El reciclador valida", "Escanea el ticket, pesa lo que recibe y confirma. Su trabajo queda "
                       "registrado.", paso="2"),
        estilo.tarjeta("La municipalidad premia", "Descarga el padrón de beneficiarios listo para rentas, sin papeles.",
                       paso="3"),
        estilo.tarjeta("La empresa recupera", "Recibe los kilos de sus marcas con su origen y financia los premios.",
                       paso="4"),
    ])

    res = resumen_viviendas(padron, entregas_todas(), "2026-10", ReglasBono())
    ind = indicadores(res)
    st.markdown(f'''<div class="franja">
        <div class="cifra"><div class="n">{ind["participan"]}</div><div class="t">hogares reciclaron en octubre</div></div>
        <div class="cifra"><div class="n">{ind["kg"] / 1000:.1f} t</div><div class="t">recuperadas en un mes</div></div>
        <div class="cifra"><div class="n">{ind["beneficiarias"]}</div><div class="t">hogares ganaron su Bono Verde</div></div>
        <div class="cifra"><div class="n">3</div><div class="t">recicladores formalizados</div></div></div>
        <p class="nota" style="text-align:center;margin-top:-1.2rem">Piloto demostrativo en Lurigancho-Chosica con datos
        sintéticos.</p>''', unsafe_allow_html=True)

    estilo.seccion("Evidencia", "Por qué funciona")
    estilo.fila_tarjetas([
        estilo.tarjeta("El dinero motiva más", "En dos experimentos en China, el incentivo monetario fue el más "
                       "efectivo para reciclar (Lu y Wang, 2022).", numero="1.º"),
        estilo.tarjeta("Ver al vecino también", "Saber cuántos vecinos ya reciclan refuerza el efecto del incentivo "
                       "(Lu y Wang, 2022).", numero="+"),
        estilo.tarjeta("Lo digital multiplica", "Un sistema digital de incentivos en Shanghái aumentó la recolección "
                       "en 229 % en una comunidad piloto (Zhou et al., 2021).", numero="229 %"),
    ])

    estilo.seccion("Con quiénes trabajamos", "Un ecosistema que ya existe")
    st.markdown('<p class="nota">Actores con los que ReciclaGov se articula. Ninguno es todavía un aliado formal.</p>',
                unsafe_allow_html=True)
    actores = [
        ("estado", "Estado", "Ministerio del Ambiente", "Ente rector. Dicta la norma, capacita a las municipalidades y "
         "publica datos abiertos de residuos."),
        ("estado", "Estado", "Municipalidades con Bono Verde", "Villa El Salvador, Los Olivos, San Juan de Lurigancho, "
         "Villa María del Triunfo, Lurigancho-Chosica, Huacho, Barranca y Sechura."),
        ("estado", "Estado", "Recicladores formalizados", "Reconocidos por la Ley 29419. Validan cada recojo y son el "
         "corazón operativo del sistema."),
        ("empresa", "Empresas", "Productores de envases", "Backus, Arca Continental Lindley, Grupo AJE, CBC, Gloria, "
         "Nestlé, Laive y Alicorp, entre otros."),
        ("empresa", "Empresas", "Retail", "Supermercados Peruanos, Cencosud y Tambo, como canales para canjear EcoPuntos."),
        ("academia", "Academia", "Q-Lab PUCP", "Diplomatura de Ciencia de Datos para las Ciencias Sociales y la Gestión "
         "Pública, donde nace el proyecto."),
    ]
    for fila in [actores[:3], actores[3:]]:
        cols = st.columns(3)
        for c, (cl, tipo, nom, txt) in zip(cols, fila):
            c.markdown(f'<div class="actor {cl}"><div class="tipo">{tipo}</div><div class="nom">{nom}</div>'
                       f'<div class="txt">{txt}</div></div>', unsafe_allow_html=True)
        st.write("")

    estilo.seccion("Quién está detrás", "Una founder entre el Estado y la sociedad")
    st.markdown(estilo.tarjeta("Ana Karen Zamalloa Lima", "Comunicadora para el desarrollo por la PUCP, especialista en "
                               "gestión pública y en ciencia de datos para el análisis social. Ha trabajado con el Estado, "
                               "la cooperación internacional y la sociedad civil, y diseñó proyectos de diálogo con "
                               "funcionarios de gobiernos subnacionales."), unsafe_allow_html=True)


# ───────────────────────────────────────────────────────── tu municipalidad
def tu_municipalidad():
    estilo.portada("Encuentra tu municipalidad", "¿Tu distrito <em class='resalte'>premia el reciclaje</em>?",
                   "Toca tu distrito en el mapa o escribe su nombre. Te mostramos si tiene un incentivo vigente, qué "
                   "norma lo respalda y cuál es el programa más cercano.")
    estilo.guia("ciclo", "Toca tu distrito en el mapa y te cuento si premian el reciclaje.")
    nombres = {f["properties"]["NOMBDIST"].title(): f["properties"] for f in mapa_lima["features"]}
    izq, der = st.columns([3, 2], gap="large")
    with izq:
        m = mapa_satelital([-12.03, -76.95], 10)
        folium.GeoJson(mapa_lima, name="Distritos",
                       style_function=lambda _: {"color": "#FFFFFF", "weight": 1.2, "fillOpacity": 0.05},
                       highlight_function=lambda _: {"fillColor": P["hoja"], "fillOpacity": 0.45},
                       tooltip=folium.GeoJsonTooltip(["NOMBDIST"], labels=False)).add_to(m)
        for r in munis.itertuples():
            folium.CircleMarker([r.lat, r.lon], radius=9, color="#FFFFFF", weight=3, fill=True,
                                fill_color="#F2A541", fill_opacity=1,
                                tooltip=f"{r.municipalidad}  ·  {r.incentivo}").add_to(m)
        clic = st_folium(m, height=520, use_container_width=True, returned_objects=["last_clicked"])
    elegido = None
    if clic and clic.get("last_clicked"):
        punto = Point(clic["last_clicked"]["lng"], clic["last_clicked"]["lat"])
        elegido = next((f["properties"] for f in mapa_lima["features"] if shape(f["geometry"]).contains(punto)), None)
    with der:
        buscado = st.text_input("O escribe tu distrito", placeholder="Por ejemplo, Los Olivos")
        if buscado.strip():
            clave = buscado.strip().lower()
            elegido = next((v for k, v in nombres.items() if k.lower().startswith(clave)), None) or elegido
            if not elegido:
                st.warning("No encontré ese distrito en Lima Metropolitana o el Callao.")
        if not elegido:
            st.markdown('<div class="banda">Los puntos naranjas marcan las municipalidades con un incentivo por '
                        'reciclar que encontramos en normas publicadas.</div>', unsafe_allow_html=True)
            return
        fila = munis[munis.ubigeo == elegido["IDDIST"]]
        poligono = next(shape(f["geometry"]) for f in mapa_lima["features"] if f["properties"]["IDDIST"] == elegido["IDDIST"])
        st.markdown(f"### {elegido['NOMBDIST'].title()}")
        if len(fila):
            r = fila.iloc[0]
            st.markdown(f'<span class="etiqueta">{r.incentivo}</span><span class="etiqueta sol">{r.estado}</span>',
                        unsafe_allow_html=True)
            st.markdown(estilo.tarjeta(r.descuento, f"{r.como_se_gana}. Norma {r.norma} ({r.anio})."),
                        unsafe_allow_html=True)
            st.link_button("Ver la norma", r.fuente)
        else:
            st.markdown('<span class="etiqueta sol">Sin incentivo registrado</span>', unsafe_allow_html=True)
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
    estilo.portada("Para vecinos", "Mi <em class='resalte'>Bono Verde</em>",
                   "Revisa tus EcoPuntos, cuánto te falta para tu descuento y cómo va tu barrio.")
    estilo.guia("vera", "Con cuatro entregas al mes ganas tu descuento. ¿Te ayudo a separar mejor?")
    reglas = ReglasBono()
    c1, c2 = st.columns([1.3, 1])
    with c1:
        codigo = recicla.elegir_vivienda(etiqueta, "vec")
    with c2:
        nuevo = any(n["codigo"] == codigo for n in st.session_state.nuevas)
        mes = elegir_mes("mes_vec", "2026-11" if nuevo else "2026-10")
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
    st.markdown(f'<div class="banda"><b>{round(participan * 10)} de cada 10</b> hogares de {yo.sector} ya reciclaron '
                f'este mes. {"Tú eres parte de ellos." if yo.entregas > 0 else "Súmate esta semana."}</div>',
                unsafe_allow_html=True)

    izq, der = st.columns(2, gap="large")
    with izq:
        st.markdown("#### Tú y tu barrio")
        st.markdown(ui.comparar(float(yo.kg), float(sector.kg.mean()), yo.sector), unsafe_allow_html=True)
    with der:
        st.markdown("#### Mis entregas del mes")
        mias = con_puntos(entregas_todas())
        mias = mias[(mias.codigo == codigo) & (mias.mes == mes)]
        lista = []
        for (fecha, _), g in mias.groupby(["fecha", "id_entrega"]):
            mats = ", ".join(sorted({MATERIALES[m]["nombre"].lower() for m in g.material}))
            lista.append({"fecha": pd.Timestamp(fecha).strftime("%d/%m/%Y"), "kg": g.kg.sum(),
                          "puntos": int(g.puntos.sum()), "detalle": mats,
                          "valida": bool(g.bien_segregado.all() and g.kg.sum() >= reglas.kg_minimos)})
        st.markdown(ui.linea_tiempo(lista), unsafe_allow_html=True)


# ───────────────────────────────────────────────────────── municipalidad
def municipalidad():
    estilo.portada("Para municipalidades", "Tablero de <em class='resalte'>Lurigancho-Chosica</em>",
                   "Piloto con datos sintéticos. Ajusta las reglas de tu ordenanza, mira el avance en el mapa y "
                   "descarga el padrón de beneficiarios para el área de rentas.")
    estilo.guia("ciclo", "El padrón ya está listo para rentas. Sin tickets ni firmas.")
    c1, c2, c3 = st.columns([1.2, 1, 1])
    with c1:
        mes = elegir_mes("mes_mun")
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
                       style_function=lambda _: {"color": "#FFFFFF", "weight": 2.5, "fillOpacity": 0}).add_to(m)
        for r in res[res.inscrito].itertuples():
            color = "#6DBE45" if r.cumple else ("#F2A541" if r.entregas > 0 else "#FFFFFF")
            folium.CircleMarker([r.lat, r.lon], radius=6, color=P["noche"], weight=1.5, fill=True, fill_color=color,
                                fill_opacity=1, tooltip=f"{r.codigo}  ·  {r.sector}  ·  {int(r.entregas_validas)} "
                                                        f"entregas válidas").add_to(m)
        st_folium(m, height=440, use_container_width=True, returned_objects=[])
        st.markdown('<p class="nota">Verde, gana el bono. Naranja, participa pero aún no cumple. Blanco, inscrita sin '
                    'entregas.</p>', unsafe_allow_html=True)
    with der:
        st.markdown("#### Qué se recicla")
        mat = con_puntos(entregas_todas())
        mat = mat[mat.mes == mes].groupby("material").kg.sum().sort_values(ascending=False)
        st.markdown(ui.barras([(MATERIALES[k]["nombre"], v, "") for k, v in mat.items()],
                              destacar=MATERIALES[mat.index[0]]["nombre"] if len(mat) else None), unsafe_allow_html=True)
    st.markdown("#### Participación por sector")
    sec = res[res.inscrito].groupby("sector").agg(inscritas=("codigo", "size"), con_bono=("cumple", "sum"))
    sec["pct"] = sec.con_bono / sec.inscritas * 100
    st.markdown(ui.barras([(s, r.pct, f"{int(r.con_bono)} de {int(r.inscritas)} viviendas inscritas ganan el bono")
                           for s, r in sec.sort_values("pct", ascending=False).iterrows()], unidad="%"),
                unsafe_allow_html=True)

    estilo.seccion("Listo para rentas", "Padrón de beneficiarios")
    st.markdown('<p class="nota">Este archivo reemplaza el cruce manual de tickets, firmas y padrones en papel.</p>',
                unsafe_allow_html=True)
    benef = padron_beneficiarios(res)
    st.markdown(ui.tabla(benef, alto=320), unsafe_allow_html=True)
    st.write("")
    st.download_button("Descargar padrón en CSV", benef.to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"padron-bono-verde-{mes}.csv", mime="text/csv", type="primary")

    contexto = minam.cargar(DATA)
    if contexto is not None:
        st.markdown("#### El distrito en los datos abiertos del MINAM")
        minam.mostrar(contexto, mapa_lima, DISTRITO, ind["kg"])


# ───────────────────────────────────────────────────────── empresa
INVIERTEN = [
    ("Coca-Cola Perú y Arca Continental Lindley", "Mantienen 25 % de PET reciclado en sus botellas y se comprometieron "
     "con el MINAM a aliarse con gobiernos locales para programas de segregación. Ya usaron QR en una campaña con Tambo.",
     "https://www.revistaeconomia.com/minam-y-produce-reconocen-a-las-primeras-empresas-que-cumplieron-al-100-con-el-acuerdo-de-produccion-limpia-en-materia-de-residuos-solidos/"),
    ("Grupo AJE", "Cielo Alcalina usa botellas 100 % recicladas y anunció una planta de reciclaje de PET en Huaral "
     "de 900 toneladas al mes, que necesitará abastecimiento verificable.",
     "https://www.corresponsables.com/per/actualidad/grupo-aje-minam-ylinea-1-del-metro-de-lima-instalan-13-puntos-de-reciclaje-de-botellas-pet-en-las-principales-estaciones/"),
    ("Backus", "Más del 85 % de sus productos usa envases retornables o reciclados y tiene programas con recicladores "
     "para latas y vidrio.", "https://peru21.pe/colab21/heroes-del-reciclaje-por-una-cultura-empresarial-sostenible"),
    ("SMI (San Miguel Industrias)", "Opera la planta de reciclaje de PET más grande del Perú y compra botellas a "
     "recicladores formales.", "https://www.revistaeconomia.com/?p=59624"),
    ("Supermercados Peruanos", "Su movimiento Recicla Consciente reúne a más de 30 empresas, el MINAM y municipalidades. "
     "Sería un canal para canjear EcoPuntos.", "https://www.revistaeconomia.com/recicla-consciente-el-movimiento-de-supermercados-peruanos-que-acerca-a-mas-personas-al-reciclaje/"),
    ("Ministerio del Ambiente", "Como ente rector, firma Acuerdos de Producción Limpia con empresas que incluyen alianzas "
     "con gobiernos locales para la segregación en la fuente.", "https://www.revistaeconomia.com/minam-y-produce-reconocen-a-las-primeras-empresas-que-cumplieron-al-100-con-el-acuerdo-de-produccion-limpia-en-materia-de-residuos-solidos/"),
]


def empresa():
    estilo.portada("Para empresas", "Tus envases, <em class='resalte'>de vuelta y verificados</em>",
                   "Solo cuentan los envases de tus marcas. Mira cuántos kilos se recuperaron, en qué sectores conviene "
                   "invertir y descarga el certificado de trazabilidad para tus metas de material reciclado.")
    estilo.guia("vera", "Cada kilo que ves aquí lo separó un vecino y lo validó un reciclador.")
    nombre = st.pills("Empresa", list(EMPRESAS), default=list(EMPRESAS)[0], key="emp") or list(EMPRESAS)[0]
    mes = elegir_mes("mes_emp")
    marcas = EMPRESAS[nombre]
    st.markdown("Marcas que cuentan para tu indicador  " + " ".join(f'<span class="etiqueta clara">{m}</span>' for m in marcas),
                unsafe_allow_html=True)

    todo = con_puntos(entregas_todas()).merge(padron[["codigo", "sector"]], on="codigo")
    todo["marca"] = todo["marca"].fillna(SIN_MARCA)
    del_mes = todo[(todo.mes == mes) & todo.bien_segregado]
    e = del_mes[del_mes.marca.isin(marcas)]
    ajenas = del_mes[del_mes.material.isin(e.material.unique()) & ~del_mes.marca.isin(marcas)]

    k = st.columns(4)
    k[0].metric("Kilos de tus marcas", f"{e.kg.sum():,.1f}")
    k[1].metric("Hogares que los devolvieron", f"{e.codigo.nunique()}")
    k[2].metric("Recojos verificados", f"{e.id_entrega.nunique()}")
    k[3].metric("Kilos de otras marcas", f"{ajenas.kg.sum():,.1f}", "no suman a tu indicador", delta_color="off")

    estilo.seccion("Dónde invertir", "Sectores que más devuelven tus envases")
    inscritas = padron[padron.inscrito].groupby("sector").codigo.size()
    rank = (e.groupby("sector").agg(kg=("kg", "sum"), hogares=("codigo", "nunique"))
            .reindex(inscritas.index, fill_value=0).assign(inscritas=inscritas).reset_index())
    rank["por_hogar"] = (rank.kg / rank.inscritas).round(3)
    rank["detalle"] = [f"{int(h)} de {int(i)} hogares inscritos devolvieron envases de tus marcas"
                       for h, i in zip(rank.hogares, rank.inscritas)]
    rank = rank.sort_values("por_hogar", ascending=False)
    izq, der = st.columns([3, 2], gap="large")
    with izq:
        st.markdown(ui.ranking(rank, "sector", "por_hogar", "detalle", "kg por hogar"), unsafe_allow_html=True)
    with der:
        mejor = rank.iloc[0].sector
        st.markdown(estilo.tarjeta(f"Empieza por {mejor}", "Es el sector que más envases de tus marcas devuelve por "
                                   "hogar. Una campaña ahí rinde más por cada sol invertido.", numero="1.º"),
                    unsafe_allow_html=True)

    estilo.seccion("Para tus reportes", "Certificado de trazabilidad")
    st.markdown('<p class="nota">Totales por distrito, sector, material y marca. Nunca incluye nombres ni direcciones.</p>',
                unsafe_allow_html=True)
    cert = (e.assign(Distrito="Lurigancho-Chosica", Material=e.material.map(lambda x: MATERIALES[x]["nombre"]))
            .groupby(["Distrito", "sector", "Material", "marca"])
            .agg(Recojos=("id_entrega", "nunique"), Hogares=("codigo", "nunique"), Kilos=("kg", "sum")).reset_index()
            .rename(columns={"sector": "Sector", "marca": "Marca"}))
    cert["Kilos"] = cert.Kilos.round(2)
    st.markdown(ui.tabla(cert, alto=340), unsafe_allow_html=True)
    st.write("")
    st.download_button("Descargar certificado en CSV", cert.to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"certificado-trazabilidad-{mes}.csv", mime="text/csv", type="primary")

    estilo.seccion("Mercado y Estado", "Quiénes ya invierten en reciclaje en el Perú")
    st.markdown('<p class="nota">Información pública sobre clientes potenciales y actores públicos. No existe alianza con '
                'ninguno de ellos.</p>', unsafe_allow_html=True)
    for fila in [INVIERTEN[:3], INVIERTEN[3:]]:
        estilo.fila_tarjetas([estilo.tarjeta(n, f'{t} <a href="{u}" target="_blank">Fuente</a>') for n, t, u in fila])
        st.write("")


# ───────────────────────────────────────────────────────── asistente
def asistente():
    estilo.portada("Asistente", "Pregúntale a <em class='resalte'>Vera</em>",
                   "Vera resuelve tus dudas sobre el Bono Verde con lo que dicen las ordenanzas, la ley y la guía "
                   "de ReciclaGov. Si algo no está en la guía, te lo dice.")
    izq, der = st.columns([1, 2.4], gap="large")
    with izq:
        estilo.retrato("vera", "Vera, vecina guía de ReciclaGov")
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
PAG = {
    "inicio": st.Page(inicio, title="Inicio", default=True, url_path="inicio"),
    "muni": st.Page(tu_municipalidad, title="Tu municipalidad", url_path="municipalidad-cercana"),
    "vecino": st.Page(vecino, title="Mi Bono Verde", url_path="vecino"),
    "reciclador": st.Page(lambda: recicla.reciclador(etiqueta), title="Reciclador", url_path="reciclador"),
    "municipalidad": st.Page(municipalidad, title="Municipalidad", url_path="municipalidad"),
    "empresa": st.Page(empresa, title="Empresa", url_path="empresa"),
    "vera": st.Page(asistente, title="Pregúntale a Vera", url_path="asistente"),
    "recicla": st.Page(lambda: recicla.recicla_ahora(etiqueta, padron), title="Recicla ahora", url_path="recicla-ahora"),
}
actual = st.navigation(list(PAG.values()), position="hidden")


def barra() -> None:
    """Barra superior de lado a lado. Logo, secciones al centro y las dos acciones principales a la derecha."""
    with st.container(key="barra"):
        cols = st.columns([1.6, .75, 1.25, 1.2, 1, 1.2, .95, 1.75, 1.55], vertical_alignment="center")
        cols[0].markdown(estilo.logo(), unsafe_allow_html=True)
        for c, k in zip(cols[1:7], ["inicio", "muni", "vecino", "reciclador", "municipalidad", "empresa"]):
            c.page_link(PAG[k])
        with cols[7], st.container(key="nav-vera"):
            st.page_link(PAG["vera"], icon=":material/chat_bubble:")
        with cols[8], st.container(key="nav-recicla"):
            st.page_link(PAG["recicla"], icon=":material/recycling:")


barra()
actual.run()
estilo.pie()
