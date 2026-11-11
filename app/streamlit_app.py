"""Minka. Juntos, cada aporte cuenta.

Plataforma que conecta a vecinos, recicladores formalizados, municipalidades y empresas. El vecino
genera un ticket digital, el reciclador lo valida, la municipalidad administra su Bono Verde sin
papel y la empresa recupera sus envases con trazabilidad por marca.

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
from backend.reglas import EMPRESAS, MATERIALES, MATERIALES_EMPRESA, SIN_MARCA, ReglasBono  # noqa: E402
from mapas import mapa_satelital  # noqa: E402

DATA = RAIZ / "data"
DISTRITO = "150118"  # Lurigancho (Chosica), distrito piloto
P = estilo.PALETA
MESES = {"2026-09": "Septiembre", "2026-10": "Octubre", "2026-11": "Noviembre"}

st.set_page_config(page_title="Minka · Juntos, cada aporte cuenta", page_icon=":material/recycling:",
                   layout="wide")
estilo.aplicar()


# ───────────────────────────────────────────────────────── datos
@st.cache_data
def cargar():
    padron = pd.read_csv(DATA / "padron_sintetico.csv")
    entregas = pd.read_csv(DATA / "entregas_sinteticas.csv")
    munis = pd.read_csv(DATA / "municipalidades_bono.csv", dtype={"ubigeo": str})
    mapa = json.loads((DATA / "lima_distritos.geojson").read_text(encoding="utf-8"))
    return padron, entregas, munis, mapa


@st.cache_data
def cargar_minam():
    return minam.cargar(DATA)


padron, entregas_base, munis, mapa_lima = cargar()
datos_minam = cargar_minam()
st.session_state.setdefault("nuevas", [])
st.session_state.setdefault("chat", [])
st.session_state.setdefault("contactos", [])
recicla.iniciar(padron)
direccion = dict(zip(padron.codigo, padron.direccion))


def entregas_todas() -> pd.DataFrame:
    if not st.session_state.nuevas:
        return entregas_base
    return pd.concat([entregas_base, pd.DataFrame(st.session_state.nuevas)], ignore_index=True)


def km(lat1, lon1, lat2, lon2) -> float:
    """Distancia en línea recta (haversine)."""
    p1, p2, dl = math.radians(lat1), math.radians(lat2), math.radians(lon2 - lon1)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(a))


def elegir_mes(clave: str, por_defecto: str = "2026-10") -> str:
    mes = st.segmented_control("Mes que quieres revisar", list(MESES), format_func=MESES.get, default=por_defecto, key=clave)
    return mes or por_defecto


def t(x: float) -> str:
    """Toneladas con separador de miles."""
    return f"{x:,.0f}"


# ───────────────────────────────────────────────────────── inicio
VALORES = [
    ("transparencia", "Transparencia", "Generamos confianza y hacemos visible el recorrido de los materiales.", P["pino"]),
    ("colaboracion", "Colaboración", "Creemos en el trabajo conjunto entre ciudadanos, recicladores, empresas y municipalidades.", P["musgo"]),
    ("equidad", "Equidad", "Promovemos una cadena de reciclaje más justa e inclusiva.", P["chispa"]),
    ("sostenibilidad", "Sostenibilidad", "Asumimos el compromiso de cuidar nuestros recursos.", P["salvia"]),
    ("innovacion", "Innovación", "Ponemos la tecnología al servicio del cambio.", P["pino"]),
    ("reconocimiento", "Reconocimiento", "Visibilizamos y valoramos el aporte de cada persona que hace posible el reciclaje.", P["musgo"]),
]
PERFILES = [
    ("vecino", "Soy vecino", "Separo en casa y quiero mi Bono Verde.", "recicla", "vera.png", P["musgo"]),
    ("reciclador", "Soy reciclador", "Recojo y valido las entregas de mi sector.", "reciclador", "ciclo.png", P["chispa"]),
    ("muni", "Soy municipalidad", "Administro el Bono Verde y el padrón para rentas.", "municipalidad", None, P["salvia"]),
    ("empresa", "Soy empresa", "Quiero recuperar los envases de mis marcas.", "empresa", None, P["pino"]),
]


def inicio():
    if not estilo.video_portada(estilo.LEMA, "Reciclar en casa ahora sí cuenta",
                                "Minka conecta a vecinos, recicladores, municipalidades y empresas para que cada botella, "
                                "lata o caja que separas quede registrada, reconocida y de vuelta en la economía."):
        estilo.portada(estilo.LEMA, "Reciclar en casa ahora sí cuenta", "")
    a, b, _ = st.columns([1.1, 1.3, 3])
    with a, st.container(key="cta-recicla"):
        st.page_link(PAG["recicla"], label="Recicla ahora", icon=":material/recycling:")
    with b, st.container(key="cta-muni"):
        st.page_link(PAG["muni"], label="¿Mi distrito premia?", icon=":material/location_on:")
    estilo.guia("vera", "Hola, vecino reciclador. Si necesitas ayuda, aquí estoy.")

    estilo.seccion("Bienvenido a Minka", "¿Con qué perfil te identificas?",
                   "Elige tu perfil y te llevamos directo a lo que necesitas.")
    cols = st.columns(4, gap="medium")
    for c, (clave, titulo, texto, destino, img, color) in zip(cols, PERFILES):
        figura = (estilo.imagen(img, titulo, radio="0") if img else ui.dibujo(clave, color, 170, fondo=False))
        with c, st.container(key=f"perfil-{clave}"):
            st.markdown(f'<div class="perfil" style="background:{color}"><div class="fig">{figura}</div>'
                        f'<div class="txt"><div class="ptit">{titulo}</div><span>{texto}</span><div class="ir">Entrar</div></div></div>',
                        unsafe_allow_html=True)
            st.page_link(PAG[destino], label=titulo)

    estilo.seccion("Nuestra historia", "Todo empezó con una vecina como Vera")
    st.markdown(f'''<div class="historia"><figure>{estilo.imagen("vera_foto.jpg", "Retrato de Vera", radio="24px")}
        <figcaption>Imagen generada con inteligencia artificial</figcaption></figure><div>
        <blockquote>«En mi casa siempre separamos las botellas, los cartones y los plásticos. Se los entregamos al
        reciclador que pasa por el barrio, pero nunca sabemos qué pasa después con esos materiales. Una vecina me contó
        que podía obtener beneficios en mis arbitrios por participar en el programa de reciclaje de la municipalidad. Sin
        embargo, no sabía cómo registrar mis entregas ni cómo hacer seguimiento a lo que reciclaba».</blockquote>
        <div class="firma"><b>Vera, vecina de Carapongo</b> · Personaje de Minka inspirado en conversaciones con usuarios</div>
        </div></div>
        <p class="reflexion">La experiencia de Vera refleja un desafío que involucra a distintos actores. Los ciudadanos
        necesitan que se reconozcan sus aportes, los recicladores y las empresas necesitan visibilizar y dar seguimiento a
        los materiales recuperados y valorizados, y las municipalidades necesitan mecanismos para gestionar, monitorear e
        incentivar la participación.</p>
        <div class="idea-fuerza"><p><b>Minka nace para conectar a estos actores en un mismo espacio digital</b>, facilitar
        el seguimiento de los materiales reciclables y reconocer el aporte de cada participante. Porque reciclar es un
        esfuerzo colectivo y <b>cada contribución cuenta</b>.</p></div>''', unsafe_allow_html=True)

    estilo.seccion("Lo que nos mueve", "Misión y visión")
    st.markdown('''<div class="mosaico"><div class="grid">
        <div class="c"><h3>Nuestra misión</h3><p>Conectar a ciudadanos, recicladores formalizados, municipalidades y
        empresas para facilitar, reconocer y hacer seguimiento al reciclaje, mediante un sistema digital que registre y
        visibilice el aporte de cada actor en la cadena de aprovechamiento de residuos.</p></div>
        <div class="c"><h3>Nuestra visión</h3><p>Un Perú donde cada material tenga una nueva oportunidad, las comunidades
        se unan y quienes hacen posible el reciclaje reciban el reconocimiento que merecen.</p></div>
        <div class="c"><h3>¿Por qué Minka?</h3><p>La minka es una tradición andina de trabajo colectivo, en la que la
        comunidad se une para lograr algo que beneficia a todos. Reciclar funciona igual, porque nadie lo logra solo.</p>
        </div></div></div>''', unsafe_allow_html=True)

    estilo.seccion("En qué creemos", "Nuestros valores")
    st.markdown('<div class="valores">' + "".join(
        f'<div class="valor"><div class="ic" style="background:{c}">{ui.dibujo(k, c, 40, fondo=False)}</div>'
        f'<div><b>{n}</b><span>{x}</span></div></div>' for k, n, x, c in VALORES) + '</div>', unsafe_allow_html=True)

    estilo.seccion("Diagnóstico", "El problema que resolvemos",
                   "En el Perú, la ley ya permite premiar a quien recicla. Sin embargo, el beneficio casi no se usa, "
                   "porque se gestiona en papel y nadie lleva la cuenta.")
    estilo.fila_tarjetas([
        estilo.tarjeta("El premio ya existe", "El artículo 70 del Decreto Legislativo 1278 permite a las municipalidades "
                       "descontar arbitrios a los vecinos que separan sus residuos.", numero="8", unidad="municipalidades "
                       "con este descuento en sus normas, según nuestra revisión"),
        estilo.tarjeta("Pero casi nadie lo conoce", "Villa María del Triunfo aprobó su bono en 2016. Aun así, la vecina que "
                       "entrevistamos no sabía cómo funciona y en su casa no se recicla.", numero="2016",
                       unidad="año en que nació un bono que hoy sus vecinos desconocen"),
        estilo.tarjeta("Todo se hace en papel", "El vecino junta tickets físicos que se pierden y la municipalidad arma "
                       "padrones a mano antes de aplicar el descuento.", numero="4", unidad="tickets de papel al mes para "
                       "ganar el bono en Villa María del Triunfo"),
        estilo.tarjeta("Y nadie tiene los datos", "Un especialista del MINAM nos confirmó que las municipalidades no "
                       "reportan cuántos vecinos participan.", numero="0", unidad="reportes que recibe el MINAM sobre "
                       "quién aplica el bono"),
    ])

    estilo.seccion("Una sola herramienta, cuatro actores", "Cómo funciona Minka")
    estilo.fila_tarjetas([
        estilo.tarjeta("El vecino separa", "Marca lo que separó, elige el día del recojo y recibe un ticket digital con QR.", paso="1"),
        estilo.tarjeta("El reciclador valida", "Escanea el ticket, pesa lo que recibe y confirma. Su trabajo queda registrado.", paso="2"),
        estilo.tarjeta("La municipalidad premia", "Descarga el padrón de beneficiarios listo para rentas, sin papeles.", paso="3"),
        estilo.tarjeta("La empresa recupera", "Recibe los kilos de sus marcas con su origen y financia los premios.", paso="4"),
    ])

    res = resumen_viviendas(padron, entregas_todas(), "2026-10", ReglasBono())
    ind = indicadores(res)
    st.markdown(f'''<div class="franja">
        <div class="cifra"><div class="n">{ind["participan"]}</div><div class="t">hogares reciclaron en octubre</div></div>
        <div class="cifra"><div class="n">{ind["kg"] / 1000:.1f} t</div><div class="t">recuperadas en un mes</div></div>
        <div class="cifra"><div class="n">{ind["beneficiarias"]}</div><div class="t">hogares ganaron su Bono Verde</div></div>
        <div class="cifra"><div class="n">3</div><div class="t">recicladores formalizados</div></div></div>
        <p class="nota" style="text-align:center">Piloto demostrativo en Lurigancho-Chosica con viviendas sintéticas.</p>''',
                unsafe_allow_html=True)

    estilo.seccion("Evidencia", "Por qué funciona")
    estilo.fila_tarjetas([
        estilo.tarjeta("El dinero motiva más", "En dos experimentos en China, el incentivo monetario fue el más efectivo "
                       "para reciclar (Lu y Wang, 2022).", numero="1.º", unidad="incentivo más efectivo"),
        estilo.tarjeta("Ver al vecino también", "Saber cuántos vecinos ya reciclan refuerza el efecto del incentivo "
                       "(Lu y Wang, 2022).", numero="+", unidad="efecto de las normas sociales"),
        estilo.tarjeta("Lo digital multiplica", "Un sistema digital de incentivos en Shanghái aumentó la recolección en una "
                       "comunidad piloto (Zhou et al., 2021).", numero="229 %", unidad="más reciclables recolectados"),
    ])

    estilo.seccion("Con quiénes trabajamos", "Un ecosistema que ya existe",
                   "Actores con los que Minka se articula. Ninguno es todavía un aliado formal.")
    actores = [
        ("estado", "Estado", "Ministerio del Ambiente", "Ente rector. Dicta la norma, capacita a las municipalidades y "
         "publica datos abiertos de residuos."),
        ("estado", "Estado", "Municipalidades con Bono Verde", "Villa El Salvador, Los Olivos, San Juan de Lurigancho, "
         "Villa María del Triunfo, Lurigancho-Chosica, Huacho, Barranca y Sechura."),
        ("estado", "Estado", "Recicladores formalizados", "Reconocidos por la Ley 29419. Validan cada recojo y son el "
         "corazón operativo del sistema."),
        ("empresa", "Empresas", "Productores de envases", "Backus, Arca Continental Lindley, Grupo AJE, CBC, Gloria, "
         "Nestlé, Laive y Alicorp, entre otros."),
        ("empresa", "Empresas", "Supermercados", "Supermercados Peruanos, Cencosud y Tambo, como posibles canales para "
         "canjear EcoPuntos."),
        ("academia", "Academia", "Q-Lab PUCP", "Diplomatura de Ciencia de Datos para las Ciencias Sociales y la Gestión "
         "Pública, donde nace el proyecto."),
    ]
    for fila in [actores[:3], actores[3:]]:
        cols = st.columns(3)
        for c, (cl, tipo, nom, txt) in zip(cols, fila):
            c.markdown(f'<div class="actor {cl}"><div class="tipo">{tipo}</div><div class="nom">{nom}</div>'
                       f'<div class="txt">{txt}</div></div>', unsafe_allow_html=True)
        st.write("")

    estilo.seccion("Quién está detrás", "La founder")
    st.markdown(f'''<div class="founder">{estilo.imagen("founder.jpg", "Ana Karen Zamalloa Lima", "180px", "50%")}<div>
        <h3>Ana Karen Zamalloa Lima</h3>
        <p>Comunicadora para el desarrollo y especialista en Gestión Pública por la PUCP, predocente del curso Medio Ambiente
        y Sostenibilidad, con experiencia en proyectos vinculados al medio ambiente, el desarrollo sostenible y la gestión
        pública.</p>
        <p class="rol">Dirige el producto, el diseño y la relación con municipalidades y empresas, en tanto que Claude Code
        actúa como su socio técnico en la ingeniería del software.</p></div></div>''', unsafe_allow_html=True)


# ───────────────────────────────────────────────────────── tu municipalidad
EN_MEDIOS = [
    ("El Peruano", "2024", "Lurigancho-Chosica da 15 % de descuento a quienes participan en el Programa Recicla",
     "La Ordenanza 353-MDL premia en el arbitrio de limpieza pública a los contribuyentes empadronados en el programa "
     "de segregación del distrito.", "https://busquedas.elperuano.pe/dispositivo/NL/2304145-1", "n1.jpg"),
    ("gob.pe", "2025", "Sechura aprueba su Bono Verde para quienes reciclan",
     "La Ordenanza 005-2025-MPS otorga el incentivo a los contribuyentes que participan en el Programa Recicla de la "
     "provincia.", "https://www.gob.pe/institucion/munisechura/normas-legales/6594200-005-2025-mps", "n2.jpg"),
    ("El Popular", "2016", "San Juan de Lurigancho lanza el Ecobono",
     "El distrito anunció un 10 % de descuento en limpieza pública para los vecinos que entreguen sus reciclables cada "
     "semana a recicladores autorizados.",
     "https://elpopular.pe/actualidad-y-policiales/2016-06-06-san-juan-de-lurigancho-dara-incentivo-tributario-vecinos-que-reciclen",
     "n3.jpg"),
    ("Infobae", "2025", "Los recicladores formales del Perú superan los S/ 3.8 millones en ventas",
     "Según el MINAM, más de 84,000 viviendas fueron registradas como beneficiarias del servicio de reciclaje en las "
     "ciudades del programa.",
     "https://www.infobae.com/peru/2025/10/23/recicladores-formales-del-peru-obtuvieron-ingresos-superiores-a-s-38-millones-por-venta-de-residuos-valorizables/",
     "n4.jpg"),
]


def tu_municipalidad():
    estilo.portada("Encuentra tu municipalidad", "¿Tu distrito <em class='resalte'>premia el reciclaje</em>?",
                   "Averigua si tu municipalidad da un descuento en arbitrios a quienes reciclan, qué norma lo respalda "
                   "y cuántos residuos genera tu distrito según el MINAM.", fondo="contenedores.jpg")
    estilo.guia("ciclo", "Toca tu distrito en el mapa y te cuento si premian el reciclaje.")
    estilo.como_usar([
        ("Busca tu distrito", "Escribe su nombre en el buscador de la derecha, por ejemplo Los Olivos."),
        ("O tócalo en el mapa", "Haz clic sobre tu distrito. Los puntos verdes tienen un incentivo vigente."),
        ("Revisa el resultado", "Verás si hay descuento, cuánto es, la norma y cuánto recicla tu distrito."),
    ])
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
                                fill_color=P["chispa"], fill_opacity=1,
                                tooltip=f"{r.municipalidad}  ·  {r.incentivo}").add_to(m)
        clic = st_folium(m, height=520, use_container_width=True, returned_objects=["last_clicked"])
    elegido = None
    if clic and clic.get("last_clicked"):
        punto = Point(clic["last_clicked"]["lng"], clic["last_clicked"]["lat"])
        elegido = next((f["properties"] for f in mapa_lima["features"] if shape(f["geometry"]).contains(punto)), None)
    with der:
        buscado = st.text_input("Escribe el nombre de tu distrito", placeholder="Por ejemplo, Los Olivos")
        if buscado.strip():
            clave = buscado.strip().lower()
            elegido = next((v for k, v in nombres.items() if k.lower().startswith(clave)), None) or elegido
            if not elegido:
                st.warning("No encontramos ese distrito en Lima Metropolitana ni en el Callao. Revisa cómo está escrito.")
        if not elegido:
            st.markdown('<div class="banda">Aún no elegiste un distrito. Escribe su nombre arriba o tócalo en el mapa. '
                        'Los <b>puntos verdes</b> son municipalidades con un incentivo por reciclar.</div>',
                        unsafe_allow_html=True)
        else:
            fila = munis[munis.ubigeo == elegido["IDDIST"]]
            poligono = next(shape(f["geometry"]) for f in mapa_lima["features"]
                            if f["properties"]["IDDIST"] == elegido["IDDIST"])
            st.markdown(f"### {minam.nombre(elegido['NOMBDIST'])}")
            if len(fila):
                r = fila.iloc[0]
                st.markdown(f'<span class="etiqueta">Sí premia el reciclaje</span><span class="etiqueta sol">{r.incentivo}</span>',
                            unsafe_allow_html=True)
                st.markdown(estilo.tarjeta(r.descuento, f"<b>¿Cómo se gana?</b> {r.como_se_gana}. Norma {r.norma} "
                                           f"({r.anio}). {r.estado}."), unsafe_allow_html=True)
                st.write("")
                st.link_button("Ver la norma", r.fuente)
            else:
                st.markdown('<span class="etiqueta sol">Sin incentivo registrado</span>', unsafe_allow_html=True)
                st.write("No encontramos una ordenanza publicada que dé descuento en arbitrios por reciclar en este "
                         "distrito. Eso no significa que no exista, así que vale la pena preguntar en tu municipalidad.")
            c = poligono.centroid
            cercanas = munis.assign(km=[km(c.y, c.x, a, b) for a, b in zip(munis.lat, munis.lon)])
            cercanas = cercanas[cercanas.ubigeo != elegido["IDDIST"]].nsmallest(1, "km").iloc[0]
            st.markdown(f'<div class="banda">El programa más cercano es <b>{cercanas.incentivo}</b> de '
                        f'{cercanas.municipalidad}, a unos {cercanas.km:.0f} km.</div>', unsafe_allow_html=True)
            if datos_minam:
                pf = minam.perfil(datos_minam[0], elegido["IDDIST"])
                if pf:
                    st.markdown(estilo.tarjeta(
                        "Lo que genera tu distrito", f"Según el MINAM, en {pf['anio']} los hogares de "
                        f"{minam.nombre(elegido['NOMBDIST'])} generaron {t(pf['total'])} toneladas de residuos. De ellas, "
                        f"{t(pf['reciclables'])} toneladas eran reciclables y hoy podrían volver a la economía.",
                        numero=f"{pf['reciclables'] / pf['total'] * 100:.0f} %", unidad="de la basura de los hogares es "
                        "reciclable"), unsafe_allow_html=True)

    estilo.seccion("Tu muni en los medios", "Municipalidades que ya premian el reciclaje",
                   "Noticias y normas publicadas sobre distritos que aplican este beneficio. Toca cada tarjeta para leer "
                   "la fuente completa.")
    cols = st.columns(4, gap="medium")
    for c, (medio, anio, titulo, texto, url, foto) in zip(cols, EN_MEDIOS):
        fondo_img = (f"linear-gradient(0deg, rgba(30,77,58,.55), rgba(62,142,99,.25)), "
                     f"url('app/static/fondos/{foto}') center/cover")
        c.markdown(f'''<a href="{url}" target="_blank" style="text-decoration:none"><div class="noticia">
            <div class="img" style="background:{fondo_img};height:150px;align-items:flex-end;justify-content:flex-start;
            padding:.8rem"><span class="etiqueta" style="margin:0">{medio}</span></div>
            <div class="cuerpo"><div class="medio">{medio} · {anio}</div><div class="tit">{titulo}</div>
            <div class="txt">{texto}</div><div class="medio" style="margin-top:.6rem">Leer en la fuente</div></div>
            </div></a>''', unsafe_allow_html=True)
    st.markdown('<p class="nota">Base legal general. Artículo 70 del Decreto Legislativo 1278, modificado por el Decreto '
                'Legislativo 1501.</p>', unsafe_allow_html=True)


# ───────────────────────────────────────────────────────── vecino
PREMIOS = [  # premios de ejemplo, que en la versión final financian las empresas aliadas
    (300, "Vale de S/ 10", "Para tus compras en supermercados aliados."),
    (600, "Pack de limpieza ecológica", "Productos para el hogar con envases reciclados."),
    (1000, "Sorteo del mes", "Una entrada al sorteo de una bicicleta entre los vecinos del distrito."),
    (1500, "Vecino destacado", "Reconocimiento público de tu municipalidad como vecino que más recicla."),
]


def que_puedo_ganar(yo, ahorro: float, acumulados: int, mes: str, faltan: int) -> None:
    """Los dos beneficios del vecino, el descuento en arbitrios y los premios por EcoPuntos."""
    estilo.seccion("Tus beneficios", "¿Qué puedo ganar?",
                   "Reciclar con Minka te da dos tipos de beneficios. El descuento en arbitrios lo aplica tu "
                   "municipalidad cada mes, mientras que los EcoPuntos se acumulan y se canjean por premios.")
    izq, der = st.columns([1, 1.6], gap="large")
    with izq:
        estado = (f"Ya lo ganaste en {MESES[mes].lower()}." if yo.cumple else
                  f"Te {'falta' if faltan == 1 else 'faltan'} {faltan} {'recojo' if faltan == 1 else 'recojos'} "
                  f"en {MESES[mes].lower()} para ganarlo.")
        st.markdown(f'<div class="premio-arb"><div class="et">1. Descuento en arbitrios</div>'
                    f'<div class="v">S/ {ahorro:.2f}</div><div class="ex">al mes en tu arbitrio de limpieza pública, '
                    f'por cumplir cuatro recojos bien separados.</div><div class="estado">{estado}</div>'
                    f'<div class="ex" style="margin-top:.8rem">En un año puedes ahorrar hasta <b>S/ {ahorro * 12:.2f}</b>.'
                    f'</div></div>', unsafe_allow_html=True)
    with der:
        filas = []
        for pts, nombre, detalle in PREMIOS:
            avance = min(acumulados / pts, 1)
            listo = acumulados >= pts
            filas.append(
                f'<div class="premio{" listo" if listo else ""}"><div class="pt">{pts:,}<span>pts</span></div>'
                f'<div class="cuerpo"><div class="barra-top"><span class="barra-etq">{nombre}</span>'
                f'<span class="barra-val">{"¡Ya puedes canjearlo!" if listo else f"Te faltan {pts - acumulados:,} pts"}'
                f'</span></div><div class="barra-pista"><div class="barra-relleno" style="width:{avance * 100:.0f}%;'
                f'background:{P["chispa"] if listo else P["musgo"]}"></div></div><div class="barra-det">{detalle}</div>'
                f'</div></div>')
        st.markdown(f'<div class="panel"><div class="et-premios">2. Premios por tus EcoPuntos · llevas '
                    f'<b>{acumulados:,} EcoPuntos</b> acumulados</div>{"".join(filas)}</div>'
                    f'<p class="nota">Premios de ejemplo. En la versión final los financian las empresas que pagan por la '
                    f'trazabilidad de sus envases.</p>', unsafe_allow_html=True)


def vecino():
    estilo.portada("Para vecinos", "Mi <em class='resalte'>Bono Verde</em>",
                   "Revisa cuántos puntos llevas, cuánto te falta para tu descuento en arbitrios y cómo va tu barrio.", fondo="separar.jpg")
    estilo.guia("vera", "Con cuatro entregas al mes ganas tu descuento. ¿Te ayudo a separar mejor?")
    estilo.como_usar([
        ("Ingresa", "Escribe tu código de contribuyente. En la demostración ya está el de Vera."),
        ("Elige el mes", "Toca el mes que quieres revisar."),
        ("Revisa tu avance", "Cada recojo bien separado suma. Con cuatro al mes, ganas tu descuento."),
        ("Mira tus premios", "Tus EcoPuntos se acumulan y se canjean por premios."),
    ])
    reglas = ReglasBono()
    codigo = recicla.ingresar(padron, "vec")
    nuevo = any(n["codigo"] == codigo for n in st.session_state.nuevas)
    mes = elegir_mes("mes_vec", "2026-11" if nuevo else "2026-10")
    res = resumen_viviendas(padron, entregas_todas(), mes, reglas)
    yo = res[res.codigo == codigo].iloc[0]
    sector = res[(res.sector == yo.sector) & res.inscrito]
    barrio = res[res.sector == yo.sector]
    ahorro = yo.arbitrio_limpieza * reglas.descuento
    faltan = int(max(reglas.entregas_minimas - yo.entregas_validas, 0))

    st.markdown(f'<div class="banda" style="font-size:1.15rem">' + (
        f"<b>¡Felicitaciones! Ganaste tu Bono Verde de {MESES[mes].lower()}.</b> Tendrás S/ {ahorro:.2f} de descuento en "
        f"tu arbitrio de limpieza pública." if yo.cumple else
        f"<b>Te {'falta' if faltan == 1 else 'faltan'} {faltan} {'recojo bien separado' if faltan == 1 else 'recojos bien separados'}</b> en {MESES[mes].lower()} para ganar S/ {ahorro:.2f} de "
        f"descuento en tu arbitrio de limpieza pública.") + '</div>', unsafe_allow_html=True)
    estilo.metricas([
        ("Recojos válidos", f"{int(yo.entregas_validas)} de {reglas.entregas_minimas}",
         "Entregas bien separadas de al menos medio kilo. Necesitas cuatro al mes."),
        ("EcoPuntos del mes", f"{int(yo.puntos)}", "Puntos que ganas por cada kilo. Las latas y botellas valen más."),
        ("Kilos reciclados", f"{yo.kg:.1f} kg", "Todo lo que el reciclador pesó y validó este mes."),
        ("Tu descuento", f"S/ {ahorro:.2f}", "Es el 15 % de tu arbitrio de limpieza pública, como manda la ordenanza."),
    ], destacar=3 if yo.cumple else None)
    st.write("")
    st.progress(min(yo.entregas_validas / reglas.entregas_minimas, 1.0),
                text="Avance hacia tu Bono Verde del mes")
    acumulados = int(con_puntos(entregas_todas()).query("codigo == @codigo").puntos.sum())
    que_puedo_ganar(yo, ahorro, acumulados, mes, faltan)
    participan = (barrio.entregas > 0).mean()
    st.write("")
    st.markdown(f'<div class="banda"><b>{round(participan * 10)} de cada 10</b> hogares de {yo.sector} ya reciclaron '
                f'este mes. {"Tú eres parte de ellos." if yo.entregas > 0 else "Súmate esta semana."}</div>',
                unsafe_allow_html=True)

    izq, der = st.columns(2, gap="large")
    with izq:
        st.markdown("#### ¿Cuánto reciclo comparado con mi barrio?")
        st.markdown(ui.comparar(float(yo.kg), float(sector.kg.mean()), yo.sector), unsafe_allow_html=True)
        st.markdown('<p class="nota">La barra de tu barrio muestra el promedio de kilos de las viviendas inscritas de tu '
                    'sector.</p>', unsafe_allow_html=True)
    with der:
        st.markdown("#### Mis recojos del mes")
        mias = con_puntos(entregas_todas())
        mias = mias[(mias.codigo == codigo) & (mias.mes == mes)]
        lista = []
        for (fecha, _), g in mias.groupby(["fecha", "id_entrega"]):
            mats = ", ".join(sorted({recicla.minuscula(MATERIALES[m]["nombre"]) for m in g.material}))
            lista.append({"fecha": pd.Timestamp(fecha).strftime("%d/%m/%Y"), "kg": g.kg.sum(),
                          "puntos": int(g.puntos.sum()), "detalle": mats,
                          "valida": bool(g.bien_segregado.all() and g.kg.sum() >= reglas.kg_minimos)})
        st.markdown(ui.linea_tiempo(lista), unsafe_allow_html=True)
        st.markdown('<p class="nota">«Válida» significa que el recojo cuenta para tu bono. «No suma» aparece cuando vino '
                    'mezclado o pesó menos de medio kilo.</p>', unsafe_allow_html=True)


# ───────────────────────────────────────────────────────── municipalidad
def municipalidad():
    estilo.portada("Para municipalidades", "Tablero de <em class='resalte'>Lurigancho-Chosica</em>",
                   "Revisa cuántos vecinos reciclan, quiénes ganan el Bono Verde y descarga el padrón listo para el área "
                   "de rentas. Las viviendas son sintéticas y los datos del distrito provienen del MINAM.", fondo="pacas.jpg")
    estilo.guia("ciclo", "El padrón ya está listo para rentas. Sin tickets ni firmas.")
    estilo.como_usar([
        ("Elige el mes", "Toca el mes que quieres revisar."),
        ("Ajusta tu ordenanza", "Mueve las reglas, como el número de recojos o el porcentaje de descuento."),
        ("Mira el avance", "El mapa muestra qué viviendas ganan el bono y cuáles aún no."),
        ("Descarga el padrón", "Baja la lista de beneficiarios y envíala a rentas."),
    ])
    c1, c2, c3 = st.columns([1.2, 1, 1])
    with c1:
        mes = elegir_mes("mes_mun")
    reglas = ReglasBono(entregas_minimas=c2.slider("Recojos válidos al mes para ganar el bono", 1, 5, 4),
                        descuento=c3.slider("Descuento en limpieza pública (%)", 5, 30, 15) / 100)
    res = resumen_viviendas(padron, entregas_todas(), mes, reglas)
    ind = indicadores(res)
    estilo.metricas([
        ("Viviendas inscritas", f"{ind['inscritas']}", "Hogares empadronados en el programa de segregación."),
        ("Participaron", f"{ind['participan']}", "Entregaron al menos una vez en el mes."),
        ("Ganan el bono", f"{ind['beneficiarias']}", f"Cumplieron {reglas.entregas_minimas} recojos válidos."),
        ("Toneladas recuperadas", f"{ind['kg'] / 1000:.2f}", "Reciclables que no fueron al relleno sanitario."),
        ("Descuento a otorgar", f"S/ {ind['descuento_total']:,.0f}", "Lo que rentas descontará en total este mes."),
    ])

    izq, der = st.columns([3, 2], gap="large")
    with izq:
        st.markdown("#### ¿Dónde están las viviendas del programa?")
        m = mapa_satelital([-11.975, -76.83], 12)
        lur = [f for f in mapa_lima["features"] if f["properties"]["IDDIST"] == DISTRITO]
        folium.GeoJson({"type": "FeatureCollection", "features": lur},
                       style_function=lambda _: {"color": "#FFFFFF", "weight": 2.5, "fillOpacity": 0}).add_to(m)
        for r in res[res.inscrito].itertuples():
            color = P["chispa"] if r.cumple else (P["brote"] if r.entregas > 0 else "#FFFFFF")
            folium.CircleMarker([r.lat, r.lon], radius=6, color=P["pino"], weight=1.5, fill=True, fill_color=color,
                                fill_opacity=1, tooltip=f"{r.direccion}  ·  {int(r.entregas_validas)} recojos "
                                                        f"válidos").add_to(m)
        st_folium(m, height=440, use_container_width=True, returned_objects=[])
        st.markdown('<p class="nota"><b>Verde intenso</b>, gana el bono. <b>Verde claro</b>, participa pero aún no cumple. '
                    '<b>Blanco</b>, inscrita sin entregas en el mes.</p>', unsafe_allow_html=True)
    with der:
        st.markdown("#### ¿Qué se recicla más?")
        mat = con_puntos(entregas_todas())
        mat = mat[mat.mes == mes].groupby("material").kg.sum().sort_values(ascending=False)
        st.markdown(ui.barras([(MATERIALES[k]["nombre"], v, "") for k, v in mat.items()],
                              destacar=MATERIALES[mat.index[0]]["nombre"] if len(mat) else None), unsafe_allow_html=True)
    st.markdown("#### ¿Qué sectores participan más?")
    sec = res[res.inscrito].groupby("sector").agg(inscritas=("codigo", "size"), con_bono=("cumple", "sum"))
    sec["pct"] = sec.con_bono / sec.inscritas * 100
    st.markdown(ui.barras([(s, r.pct, f"{int(r.con_bono)} de {int(r.inscritas)} viviendas inscritas ganan el bono")
                           for s, r in sec.sort_values("pct", ascending=False).iterrows()], unidad="%"),
                unsafe_allow_html=True)

    estilo.seccion("Listo para rentas", "Padrón de beneficiarios",
                   "Esta lista reemplaza el cruce manual de tickets, firmas y padrones en papel. Cada fila es un "
                   "contribuyente que cumplió las reglas del mes y el monto que se le descuenta.")
    benef = padron_beneficiarios(res)
    sector_de = dict(zip(padron.contribuyente, padron.sector))
    vista = pd.DataFrame({
        "Contribuyente": benef["Código de contribuyente"],
        "Dirección": benef["Dirección"],
        "Sector": benef["Código de contribuyente"].map(sector_de),
        "Recojos válidos": benef["Entregas válidas"].astype(int).astype(str) + f" de {reglas.entregas_minimas}",
        "Kilos reciclados": benef["kg reciclados"].map(lambda x: f"{x:.1f} kg"),
        "Descuento": benef["Descuento (S/)"].map(lambda x: f"S/ {x:.2f}"),
    })
    filtro = st.text_input("Busca por dirección, sector o código de contribuyente", placeholder="Por ejemplo, Carapongo")
    if filtro.strip():
        f = filtro.strip().lower()
        vista = vista[vista.apply(lambda r: f in " ".join(r.astype(str)).lower(), axis=1)]
    st.markdown(f'<p class="nota">{len(vista)} {"beneficiario" if len(vista) == 1 else "beneficiarios"} en '
                f'{MESES[mes].lower()}.</p>', unsafe_allow_html=True)
    st.markdown(ui.tabla(vista, alto=340), unsafe_allow_html=True)
    st.write("")
    st.download_button("Descargar padrón para rentas (CSV)", benef.to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"padron-bono-verde-{mes}.csv", mime="text/csv", type="primary")

    if datos_minam:
        comp, gen = datos_minam
        pf = minam.perfil(comp, DISTRITO)
        estilo.seccion("Datos reales del MINAM", f"¿Cuánta basura genera {pf['distrito'].replace('Lurigancho', 'Lurigancho-Chosica')}?",
                       f"Según los datos abiertos del Ministerio del Ambiente, en {pf['anio']} los hogares del distrito "
                       f"generaron {t(pf['total'])} toneladas de residuos. {pf['reciclables'] / pf['total'] * 100:.0f} de cada "
                       f"100 toneladas eran reciclables y podrían volver a la economía en lugar de ir al relleno sanitario.")
        estilo.metricas([
            ("Residuos de los hogares", f"{t(pf['total'])} t", f"Toneladas generadas en todo {pf['anio']}."),
            ("Reciclables", f"{t(pf['reciclables'])} t", "Papel, cartón, plásticos, vidrio, metales y Tetra Pak."),
            ("Por persona", f"{pf['kg_hab_dia']:.2f} kg", "Basura que genera cada habitante al día."),
            ("Recuperado por el piloto", f"{ind['kg'] / 1000:.2f} t", "Lo que registró Minka en el mes, con datos sintéticos."),
        ], destacar=1)
        st.write("")
        izq, der = st.columns([3, 2], gap="large")
        with izq:
            st.markdown("#### ¿Qué materiales reciclables hay en esa basura?")
            st.markdown(ui.barras([(g, v, f"{v / pf['total'] * 100:.1f} % de todos los residuos del hogar")
                                   for g, v in sorted(pf["por_grupo"].items(), key=lambda x: -x[1])], unidad="t"),
                        unsafe_allow_html=True)
        with der:
            st.markdown("#### ¿Crece la basura cada año?")
            s = minam.serie(gen, DISTRITO)
            st.markdown(ui.barras([(str(int(r.anio)), r.toneladas, "") for r in s.itertuples()], unidad="t",
                                  destacar=str(int(s.anio.max()))), unsafe_allow_html=True)
            st.markdown(f'<p class="nota">Toneladas de residuos domiciliarios por año, según la Plataforma Nacional de '
                        f'Datos Abiertos del MINAM (corte del 12/12/2024).</p>', unsafe_allow_html=True)


# ───────────────────────────────────────────────────────── empresa
INVIERTEN = [
    ("Coca-Cola Perú y Arca Continental Lindley", "botella", "Mantienen 25 % de PET reciclado en sus botellas y se "
     "comprometieron con el MINAM a aliarse con gobiernos locales para programas de segregación.",
     "https://www.revistaeconomia.com/minam-y-produce-reconocen-a-las-primeras-empresas-que-cumplieron-al-100-con-el-acuerdo-de-produccion-limpia-en-materia-de-residuos-solidos/"),
    ("Grupo AJE", "planta", "Cielo Alcalina usa botellas 100 % recicladas y la empresa instaló puntos de reciclaje de "
     "botellas PET en estaciones del Metro de Lima.",
     "https://www.corresponsables.com/per/actualidad/grupo-aje-minam-ylinea-1-del-metro-de-lima-instalan-13-puntos-de-reciclaje-de-botellas-pet-en-las-principales-estaciones/"),
    ("Backus", "lata", "Más del 85 % de sus productos usa envases retornables o reciclados y tiene programas con "
     "recicladores para latas y vidrio.", "https://peru21.pe/colab21/heroes-del-reciclaje-por-una-cultura-empresarial-sostenible"),
    ("SMI (San Miguel Industrias)", "planta", "Opera la planta de reciclaje de PET más grande del Perú y compra botellas "
     "a recicladores formales.", "https://www.revistaeconomia.com/?p=59624"),
    ("Supermercados Peruanos", "carrito", "Su movimiento Recicla Consciente reúne a más de 30 empresas, el MINAM y "
     "municipalidades. Podría ser un canal para canjear EcoPuntos.",
     "https://www.revistaeconomia.com/recicla-consciente-el-movimiento-de-supermercados-peruanos-que-acerca-a-mas-personas-al-reciclaje/"),
    ("Ministerio del Ambiente", "muni", "Como ente rector, firma Acuerdos de Producción Limpia con empresas que incluyen "
     "alianzas con gobiernos locales para la segregación en la fuente.",
     "https://www.revistaeconomia.com/minam-y-produce-reconocen-a-las-primeras-empresas-que-cumplieron-al-100-con-el-acuerdo-de-produccion-limpia-en-materia-de-residuos-solidos/"),
]


def empresa():
    estilo.portada("Para empresas", "Tus envases, <em class='resalte'>de vuelta y verificados</em>",
                   "Solo cuentan los envases de tus marcas. Mira cuántos kilos se recuperaron, en qué distritos y sectores "
                   "conviene invertir y descarga el certificado de trazabilidad para tus metas de material reciclado.", fondo="fardos.jpg")
    estilo.guia("vera", "Cada kilo que ves aquí lo separó un vecino y lo validó un reciclador.")
    estilo.como_usar([
        ("Elige tu empresa", "Toca el nombre de tu empresa. Verás las marcas que cuentan para tu indicador."),
        ("Revisa lo recuperado", "Kilos de tus marcas que los vecinos devolvieron y los recicladores validaron."),
        ("Decide dónde invertir", "Compara distritos con datos reales del MINAM y los sectores del piloto."),
        ("Descarga tu certificado", "Un archivo sin datos personales para tus reportes de sostenibilidad."),
    ])
    nombre = st.pills("Tu empresa", list(EMPRESAS), default=list(EMPRESAS)[0], key="emp") or list(EMPRESAS)[0]
    mes = elegir_mes("mes_emp")
    marcas = EMPRESAS[nombre]
    st.markdown("<b>Marcas que cuentan para tu indicador</b><br>" + " ".join(
        f'<span class="etiqueta clara">{m}</span>' for m in marcas), unsafe_allow_html=True)

    todo = con_puntos(entregas_todas()).merge(padron[["codigo", "sector"]], on="codigo")
    todo["marca"] = todo["marca"].fillna(SIN_MARCA)
    del_mes = todo[(todo.mes == mes) & todo.bien_segregado]
    e = del_mes[del_mes.marca.isin(marcas)]
    ajenas = del_mes[del_mes.material.isin(e.material.unique()) & ~del_mes.marca.isin(marcas)]
    st.write("")
    estilo.metricas([
        ("Kilos de tus marcas", f"{e.kg.sum():,.1f} kg", "Envases de tus marcas validados por un reciclador."),
        ("Hogares que los devolvieron", f"{e.codigo.nunique()}", "Viviendas distintas que entregaron tus envases."),
        ("Recojos verificados", f"{e.id_entrega.nunique()}", "Cada recojo tiene fecha, sector y reciclador."),
        ("Kilos de otras marcas", f"{ajenas.kg.sum():,.1f} kg", "Del mismo material, pero no suman a tu indicador."),
    ], destacar=0)

    if datos_minam:
        comp = datos_minam[0]
        grupos = sorted({minam.DE_MATERIAL[m] for m in MATERIALES_EMPRESA[nombre]})
        pot = minam.potencial(comp, grupos)
        estilo.seccion("Dónde invertir en Lima", "Distritos con más envases de tu tipo",
                       f"Según los datos abiertos del MINAM ({minam.anio_reciente(comp)}), estos distritos generan más "
                       f"toneladas al año de {minam.en_texto(grupos)}, que son los materiales de tus marcas. "
                       f"Son los lugares donde una campaña de reciclaje puede recuperar más.")
        st.markdown(ui.ranking(pot, "distrito", "toneladas", "detalle", "t al año"), unsafe_allow_html=True)

    estilo.seccion("Dentro del piloto", "Sectores de Lurigancho-Chosica que más devuelven tus envases",
                   "Kilos de tus marcas por cada hogar inscrito en el sector. Mientras más alto, más rinde cada sol "
                   "invertido en una campaña.")
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
                                   "hogar. Una campaña ahí rinde más por cada sol invertido.", numero="1.º",
                                   unidad="sector recomendado"), unsafe_allow_html=True)

    estilo.seccion("Para tus reportes", "Certificado de trazabilidad",
                   "Resume cuántos kilos de cada marca se recuperaron, en qué sector y en cuántos recojos. Nunca incluye "
                   "nombres ni direcciones de los vecinos.")
    cert = (e.assign(Distrito="Lurigancho-Chosica", Material=e.material.map(lambda x: MATERIALES[x]["nombre"]))
            .groupby(["Distrito", "sector", "Material", "marca"])
            .agg(Recojos=("id_entrega", "nunique"), Hogares=("codigo", "nunique"), Kilos=("kg", "sum")).reset_index()
            .rename(columns={"sector": "Sector", "marca": "Marca"}))
    cert["Kilos"] = cert.Kilos.round(2)
    st.markdown(ui.tabla(cert, alto=340), unsafe_allow_html=True)
    st.write("")
    st.download_button("Descargar certificado (CSV)", cert.to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"certificado-trazabilidad-{mes}.csv", mime="text/csv", type="primary")

    estilo.seccion("Mercado y Estado", "¿Quiénes ya invierten en reciclaje en el Perú?",
                   "Información pública sobre clientes potenciales y actores públicos. No existe alianza con ninguno de "
                   "ellos.")
    colores = [P["musgo"], P["chispa"], P["salvia"], P["pino"], P["musgo"], P["chispa"]]
    for fila in [list(zip(INVIERTEN[:3], colores[:3])), list(zip(INVIERTEN[3:], colores[3:]))]:
        cols = st.columns(3, gap="medium")
        for c, ((n, dib, txt, url), color) in zip(cols, fila):
            c.markdown(f'''<div class="noticia"><div class="img" style="background:{color}">
                {ui.dibujo(dib, color, 84, fondo=False)}</div><div class="cuerpo"><div class="tit">{n}</div>
                <div class="txt">{txt}</div><a href="{url}" target="_blank" class="medio"
                style="display:inline-block;margin-top:.6rem">Ver la fuente</a></div></div>''', unsafe_allow_html=True)
        st.write("")


# ───────────────────────────────────────────────────────── únete
PLANES = {
    "Municipal": {"para": "Municipalidades", "desc": "Para gobiernos locales con un Bono Verde o un programa de segregación.",
                  "mensual": ("S/ 0", "para siempre"), "anual": ("S/ 0", "para siempre"),
                  "nota": "Gratis, porque las empresas financian el sistema.",
                  "incluye": ["Ticket digital con QR para todos tus vecinos", "Validación por recicladores formalizados",
                              "Tablero del distrito con datos del MINAM", "Padrón de beneficiarios listo para rentas",
                              "Capacitación para tu equipo"],
                  "pago": "Un especialista te contacta para configurar tu ordenanza."},
    "Trazabilidad": {"para": "Empresas", "desc": "Para empresas que quieren empezar y pagar solo por lo que se recupera.",
                     "mensual": ("S/ 150", "por tonelada"), "anual": ("S/ 150", "por tonelada"),
                     "nota": "Sin mensualidad. Pagas solo por los envases de tus marcas que se recuperan.",
                     "incluye": ["Kilos de tus marcas validados por recicladores", "Certificado mensual sin datos personales",
                                 "Tablero con tus indicadores", "Hasta 10 marcas"],
                     "pago": "Te registras y pagas en línea con tarjeta."},
    "Territorio": {"para": "Empresas", "desc": "Para equipos de sostenibilidad que planifican dónde invertir.",
                   "mensual": ("S/ 2,500", "al mes"), "anual": ("S/ 25,000", "al año"),
                   "nota": "Con el pago anual ahorras dos meses.",
                   "incluye": ["Todo lo del plan Trazabilidad", "Certificados ilimitados y marcas ilimitadas",
                               "Clasificación de distritos con datos reales del MINAM", "Campañas con municipalidades aliadas",
                               "Reportes para tus metas de material reciclado", "Especialista asignado"],
                   "pago": "Pagas en línea o coordinas con un especialista."},
}


def unete():
    estilo.portada("Únete a Minka", "Súmate a la <em class='resalte'>minka del reciclaje</em>",
                   "Elige tu perfil y tu plan. Los vecinos y recicladores se inscriben gratis, las municipalidades usan "
                   "Minka sin costo y las empresas pagan por la trazabilidad de sus envases.", fondo="mano.jpg")
    estilo.seccion("Planes", "Elige el plan para tu institución",
                   "Como en cualquier aplicación por suscripción, puedes ver cuánto pagas y a qué accedes antes de "
                   "registrarte. Los vecinos y los recicladores no pagan nada.")
    periodo = st.segmented_control("Forma de pago", ["Mensual", "Anual, con dos meses gratis"], default="Mensual",
                                   key="periodo") or "Mensual"
    clave = "anual" if periodo.startswith("Anual") else "mensual"
    tarjetas = []
    for nombre, pl in PLANES.items():
        precio, unidad = pl[clave]
        top = nombre == "Territorio"
        tarjetas.append(
            f'<div class="plan{" top" if top else ""}">' + ('<div class="cinta-plan">Recomendado</div>' if top else "") +
            f'<div class="para">{pl["para"]}</div><div class="nom">{nombre}</div><div class="desc">{pl["desc"]}</div>'
            f'<div class="precio">{precio} <small>{unidad}</small></div><div class="nota-precio">{pl["nota"]}</div>'
            f'<ul>{"".join(f"<li>{x}</li>" for x in pl["incluye"])}</ul><div class="como-pago">{pl["pago"]}</div></div>')
    st.markdown(f'<div class="planes">{"".join(tarjetas)}</div>', unsafe_allow_html=True)

    estilo.seccion("Así se identifica cada actor", "¿Cómo sabemos quién recicla y quién recoge?")
    estilo.fila_tarjetas([
        estilo.tarjeta("Vecino", "Entra con su código de contribuyente, que figura en su recibo de arbitrios. Así cada "
                       "recojo se suma a la vivienda correcta y la municipalidad aplica el descuento.", paso="1"),
        estilo.tarjeta("Reciclador", "Está registrado en su municipalidad, como manda la Ley 29419, y valida cada ticket "
                       "con su carné. Su código queda en cada recojo.", paso="2"),
        estilo.tarjeta("Municipalidad", "Usa una cuenta institucional para ver su tablero y descargar el padrón.", paso="3"),
        estilo.tarjeta("Empresa", "Usa una cuenta corporativa para ver los envases de sus marcas y descargar sus "
                       "certificados de trazabilidad.", paso="4"),
    ])

    estilo.seccion("Regístrate", "¿Con qué perfil te unes?")
    st.markdown('<p class="nota">Esta es una demostración. Los formularios no envían datos a ningún servidor y no se '
                'realiza ningún cobro.</p>', unsafe_allow_html=True)
    perfil = st.segmented_control("Elige tu perfil", ["Soy vecino", "Soy reciclador", "Soy municipalidad", "Soy empresa"],
                                  default="Soy vecino", key="perfil_unete") or "Soy vecino"
    resumen = None
    with st.form(f"form_{perfil}", clear_on_submit=False):
        if perfil == "Soy vecino":
            nombre = st.text_input("Nombre y apellido")
            c1, c2 = st.columns(2)
            distrito = c1.text_input("Distrito", placeholder="Por ejemplo, Lurigancho-Chosica")
            contrib = c2.text_input("Código de contribuyente", help="Está en tu recibo de arbitrios.")
            st.text_input("Dirección", placeholder="Por ejemplo, Mz. B Lt. 21, Carapongo")
            st.text_input("Celular para avisarte del recojo (opcional)")
            mensaje = (f"Gracias, {nombre or 'vecino'}. Enviaremos tu solicitud a la municipalidad de "
                       f"{distrito or 'tu distrito'}. Cuando te inscriban, entra a Recicla ahora con tu código "
                       f"{contrib or 'de contribuyente'}.")
        elif perfil == "Soy reciclador":
            nombre = st.text_input("Nombre y apellido")
            c1, c2 = st.columns(2)
            c1.text_input("Asociación de recicladores")
            muni = c2.text_input("Municipalidad donde estás registrado")
            st.text_input("Número de registro municipal o carné")
            mensaje = (f"Gracias, {nombre or 'compañero reciclador'}. La municipalidad de {muni or 'tu distrito'} "
                       "verificará tu registro y te enviaremos tu carné digital para validar tickets.")
        elif perfil == "Soy municipalidad":
            muni = st.text_input("Municipalidad")
            c1, c2 = st.columns(2)
            nombre = c1.text_input("Nombre de contacto")
            c2.text_input("Cargo", placeholder="Por ejemplo, subgerente de limpieza pública")
            st.text_input("Correo institucional")
            st.text_area("¿Tienen una ordenanza de Bono Verde o un programa de segregación?")
            mensaje = (f"Gracias, {nombre or 'equipo'}. Un especialista de Minka se pondrá en contacto contigo en las "
                       f"próximas 48 horas para activar el plan Municipal gratuito en {muni or 'tu municipalidad'}.")
        else:
            emp = st.text_input("Empresa")
            c1, c2 = st.columns(2)
            nombre = c1.text_input("Nombre de contacto")
            c2.text_input("Cargo", placeholder="Por ejemplo, coordinadora de sostenibilidad")
            st.text_input("Correo corporativo")
            c3, c4 = st.columns(2)
            with c3:
                plan = st.pills("Plan", ["Trazabilidad", "Territorio"], default="Territorio", key="plan") or "Territorio"
            with c4:
                via = st.pills("¿Cómo prefieres empezar?", ["Registrarme y pagar en línea", "Que un especialista me contacte"],
                               default="Registrarme y pagar en línea", key="via") or "Registrarme y pagar en línea"
            precio, unidad = PLANES[plan][clave]
            if via.startswith("Registrarme"):
                mensaje = (f"Listo, {nombre or 'equipo'}. Tu cuenta de {emp or 'tu empresa'} quedó creada con el plan {plan}.")
                resumen = (plan, f"{precio} {unidad}", periodo)
            else:
                mensaje = (f"Gracias, {nombre or 'equipo'}. Un especialista de Minka se pondrá en contacto contigo en las "
                           f"próximas 48 horas para preparar una propuesta del plan {plan} para {emp or 'tu empresa'}.")
        enviado = st.form_submit_button("Enviar", type="primary", width="stretch")
    if enviado:
        st.success(mensaje)
        if resumen:
            st.markdown(estilo.tarjeta(f"Resumen de tu suscripción · {resumen[0]}",
                        f"Monto {resumen[1]}" + (f", pago {resumen[2].split(',')[0].lower()}" if resumen[0] == "Territorio" else "")
                        + ". En la versión final, el pago con tarjeta se procesa en una pasarela segura, como Culqi o "
                        "Niubiz, y Minka nunca guarda los datos de la tarjeta. En esta demostración no se cobra nada."),
                        unsafe_allow_html=True)
            st.write("")
            st.page_link(PAG["empresa"], label="Ir a mi tablero de empresa", icon=":material/arrow_forward:")


# ───────────────────────────────────────────────────────── asistente
def asistente():
    estilo.portada("Asistente", "Pregúntale a <em class='resalte'>Vera</em>",
                   "Vera resuelve tus dudas sobre el Bono Verde y el reciclaje con lo que dicen las ordenanzas, la ley y "
                   "la guía de Minka. Si algo no está en la guía, te lo dice.", fondo="botellas.jpg")
    izq, der = st.columns([1, 2.4], gap="large")
    with izq:
        estilo.retrato("vera", "Vera, vecina guía de Minka")
        st.markdown("#### Preguntas frecuentes")
        for sugerida in ["¿Qué es el Bono Verde?", "¿Cuánto descuento me dan?", "¿Cómo separo bien mis residuos?",
                         "¿Cuál es mi código de contribuyente?", "Mi distrito no tiene Bono Verde",
                         "¿Quién paga los premios?", "¿Mis datos están protegidos?"]:
            if st.button(sugerida, width="stretch"):
                st.session_state.pendiente = sugerida
    with der:
        pregunta = st.session_state.pop("pendiente", None)
        if pregunta:
            texto, fuentes, _ = responder(pregunta)
            st.session_state.chat += [("user", pregunta, []), ("assistant", texto, fuentes)]
        estilo.chat(st.session_state.chat)
        escrita = st.chat_input("Escríbele a Vera, por ejemplo «Hola» o «¿Qué materiales reciben?»")
        if escrita:
            st.session_state.pendiente = escrita
            st.rerun()


# ───────────────────────────────────────────────────────── navegación
PAG = {
    "inicio": st.Page(inicio, title="Inicio", default=True, url_path="inicio"),
    "muni": st.Page(tu_municipalidad, title="Tu municipalidad", url_path="municipalidad-cercana"),
    "vecino": st.Page(vecino, title="Mi Bono Verde", url_path="vecino"),
    "reciclador": st.Page(lambda: recicla.reciclador(padron, direccion), title="Reciclador", url_path="reciclador"),
    "municipalidad": st.Page(municipalidad, title="Municipalidad", url_path="municipalidad"),
    "empresa": st.Page(empresa, title="Empresa", url_path="empresa"),
    "unete": st.Page(unete, title="Únete", url_path="unete"),
    "vera": st.Page(asistente, title="Pregúntale a Vera", url_path="asistente"),
    "recicla": st.Page(lambda: recicla.recicla_ahora(padron, direccion), title="Recicla ahora", url_path="recicla-ahora"),
}
actual = st.navigation(list(PAG.values()), position="hidden")


def barra() -> None:
    """Barra superior. Logo con su lema, secciones al centro y las dos acciones principales a la derecha."""
    with st.container(key="barra"):
        cols = st.columns([2.1, .8, 1.35, 1.25, 1.05, 1.25, 1, .75, 1.75, 1.55], vertical_alignment="center")
        cols[0].markdown(estilo.logo(), unsafe_allow_html=True)
        for c, k in zip(cols[1:8], ["inicio", "muni", "vecino", "reciclador", "municipalidad", "empresa", "unete"]):
            with c:
                st.page_link(PAG[k])
        with cols[8], st.container(key="nav-vera"):
            st.page_link(PAG["vera"], icon=":material/chat_bubble:")
        with cols[9], st.container(key="nav-recicla"):
            st.page_link(PAG["recicla"], icon=":material/recycling:")


barra()
actual.run()
estilo.pie()
