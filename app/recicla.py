"""El corazón de Minka: pasar del ticket de papel al ticket digital.

1. El vecino, en «Recicla ahora», ingresa con su código de contribuyente, dice qué separó y saca su bolsa
   la noche anterior al día de ruta de su sector, identificada con el adhesivo QR de su vivienda.
2. El reciclador recoge las bolsas en su ruta de madrugada. En el centro de acopio, el encargado de pesaje
   de la asociación escanea el adhesivo o el ticket, pesa lo que llegó y lo valida con un solo celular.
3. Solo la entrega validada suma al Bono Verde, al padrón municipal y al certificado de la empresa.

Las solicitudes y entregas de la demo viven en st.session_state.
"""
from datetime import date, timedelta

import pandas as pd
import streamlit as st

import componentes as ui
import estilo
from ai.extraer import a_tabla, extraer
from backend.reglas import MATERIAL_MARCAS, MATERIALES, SIN_MARCA

# material: (unidad sugerida, paso del contador, ejemplo para el vecino)
FORMULARIO = {
    "plastico_pet": ("unidades", 1.0, "Botellas de gaseosa, agua o yogur"),
    "metal": ("unidades", 1.0, "Latas de cerveza, gaseosa o conservas"),
    "papel_carton": ("kg", 0.5, "Cajas, periódicos y cuadernos viejos"),
    "vidrio": ("unidades", 1.0, "Botellas y frascos de vidrio"),
    "tetrapak": ("unidades", 1.0, "Cajas de leche o de jugo"),
    "plastico_otro": ("kg", 0.5, "Baldes, envases de champú o de detergente"),
}
TURNOS = ["La noche anterior, en la puerta de mi casa", "En mano, de 8 a 12 horas"]
RUTA = (1, 4)  # días de ruta del sector en la demo, martes y viernes
BONO_KG = 0.05  # bono por kilo validado de envases de marcas clientes, financiado por las empresas
CUENTA_VERA = "C-159376"  # cuenta de prueba, vivienda sintética de Carapongo
RECICLADOR = ("Don Ciclo", "Reciclador formalizado · Carné REC-01 · Asociación de recicladores de Lurigancho-Chosica")


def proximo_dia_ruta(desde: date | None = None) -> date:
    """Siguiente martes o viernes, los días de ruta del sector en la demo."""
    dia = (desde or date.today()) + timedelta(days=1)
    while dia.weekday() not in RUTA:
        dia += timedelta(days=1)
    return dia


def iniciar(padron: pd.DataFrame) -> None:
    """Dos solicitudes de ejemplo, para que el reciclador no empiece con la lista vacía."""
    if "solicitudes" in st.session_state:
        return
    hoy = date.today().isoformat()
    inscritas = padron[padron.inscrito].codigo.tolist()
    st.session_state.solicitudes = [
        {"id": "T-0101", "codigo": inscritas[10], "fecha": hoy, "turno": TURNOS[0], "estado": "pendiente",
         "lineas": [{"material": "papel_carton", "kg": 2.5, "marca": SIN_MARCA},
                    {"material": "plastico_pet", "kg": 0.36, "marca": "San Luis"}]},
        {"id": "T-0102", "codigo": inscritas[25], "fecha": hoy, "turno": TURNOS[1], "estado": "pendiente",
         "lineas": [{"material": "vidrio", "kg": 1.4, "marca": "Cusqueña"},
                    {"material": "metal", "kg": 0.15, "marca": "Cristal"}]},
    ]


def ingresar(padron: pd.DataFrame, clave: str) -> str:
    """El vecino entra con su código de contribuyente, que figura en su recibo de arbitrios."""
    inscritas = padron[padron.inscrito]
    por_contrib = dict(zip(inscritas.contribuyente, inscritas.codigo))
    izq, der = st.columns([1.3, 1], gap="large")
    with izq:
        etiqueta = "Código de contribuyente del vecino" if clave == "rr" else "Tu código de contribuyente"
        escrito = st.text_input(etiqueta, value=CUENTA_VERA, key=f"contrib_{clave}",
                                help="Es el número que aparece arriba en tu recibo de arbitrios o en tu cuponera.")
        escrito = escrito.strip().upper()
        if not escrito.startswith("C-") and escrito[:1].isdigit():
            escrito = "C-" + escrito
    if clave != "rr":
        der.markdown('<div class="banda" style="margin-top:1.7rem"><b>¿Dónde lo encuentro?</b> Arriba, en tu recibo de '
                     'arbitrios. En esta demostración ya está escrito el código de prueba de Vera.</div>',
                     unsafe_allow_html=True)
    codigo = por_contrib.get(escrito) or (escrito if escrito in set(inscritas.codigo) else None)
    if not codigo:
        st.warning("No encontramos ese código entre las viviendas inscritas. Mientras te inscribes desde la sección "
                   "Únete, usamos la cuenta de prueba de Vera.")
        codigo = por_contrib[CUENTA_VERA]
    fila = inscritas[inscritas.codigo == codigo].iloc[0]
    nombre = "Vera" if fila.contribuyente == CUENTA_VERA else "vecino inscrito"
    saludo = f"Vecino: {nombre}" if clave == "rr" else f"Hola, {nombre}"
    estilo.identidad("vera", saludo, f"{fila.direccion} · Contribuyente {fila.contribuyente}")
    return codigo


def leer_qr(imagen: bytes) -> str:
    """Lee el código QR de una foto del ticket con OpenCV. Devuelve el texto o una cadena vacía."""
    import cv2
    import numpy as np
    img = cv2.imdecode(np.frombuffer(imagen, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        return ""
    texto, _, _ = cv2.QRCodeDetector().detectAndDecode(img)
    return texto.strip()


def _kg(material: str, cantidad: float, unidad: str) -> float:
    return round(cantidad if unidad == "kg" else cantidad * MATERIALES[material]["kg_unidad"], 2)


def _puntos(lineas: list[dict]) -> int:
    return sum(round(MATERIALES[l["material"]]["puntos_kg"] * l["kg"]) for l in lineas)


def _resumen(lineas: list[dict]) -> str:
    def marca(l):
        return f" de {l['marca']}" if l.get("marca", SIN_MARCA) != SIN_MARCA else ""
    return ", ".join(f"{minuscula(MATERIALES[l['material']]['nombre'])}{marca(l)} ({l['kg']:g} kg)" for l in lineas)


def _modo(turno: str) -> str:
    if turno.startswith("La noche"):
        return "Bolsa en la puerta la noche anterior, el reciclador pasa desde las 5 de la mañana."
    return f"Entrega {turno[0].lower()}{turno[1:]}."


def minuscula(nombre: str) -> str:
    """Nombre del material en minúscula, sin perder las siglas (PET, Tetra Pak)."""
    return nombre.lower().replace("pet", "PET").replace("tetra pak", "Tetra Pak")


# ───────────────────────────────────────────────────────── vecino
def recicla_ahora(padron: pd.DataFrame, direccion: dict) -> None:
    estilo.portada("Recicla ahora", "Tu reciclaje, <em class='resalte'>en cuatro pasos</em>",
                   "Cuéntanos qué separaste y saca tu bolsa la noche anterior al día de ruta de tu sector. No necesitas "
                   "esperar al reciclador. Cuando tu bolsa se pese en el centro de acopio, sumará a tu Bono Verde.", fondo="tapa.jpg")
    estilo.guia("vera", "Enjuaga las botellas y las latas, y aplasta las cajas. Así tu entrega vale más.")
    estilo.como_usar([
        ("Ingresa", "Escribe tu código de contribuyente, que está en tu recibo de arbitrios."),
        ("Cuenta lo que separaste", "Marca cuántas botellas, latas o kilos tienes, o escríbelo con tus palabras."),
        ("Saca tu bolsa la noche anterior", "Tu reciclador pasa de madrugada por tu calle en los días de ruta."),
        ("Identifica tu bolsa", "Pega el adhesivo QR de tu vivienda. En el centro de acopio lo escanean y pesan."),
    ], "Así funciona")

    estilo.seccion("Paso 1", "Ingresa con tu código de contribuyente")
    codigo = ingresar(padron, "rv")

    estilo.seccion("Paso 2", "¿Qué separaste para reciclar?",
                   "Si no sabes el peso, no te preocupes. Cuenta las botellas o las latas y Minka calcula los kilos. "
                   "Indicar la marca ayuda a que las empresas financien los premios.")
    marcar, contar = st.tabs(["Marcar mis materiales", "Contarlo con mis palabras"])
    lineas = []
    with marcar:
        cols = st.columns(3, gap="medium")
        for i, (mat, (unidad, paso, ejemplo)) in enumerate(FORMULARIO.items()):
            with cols[i % 3]:
                st.markdown(ui.tarjeta_material(mat, MATERIALES[mat]["nombre"], MATERIALES[mat]["puntos_kg"])
                            .replace('</div></div>', f'</div><div class="mat-pts" style="margin-top:.3rem">{ejemplo}</div></div>', 1),
                            unsafe_allow_html=True)
                cantidad = st.number_input(f"¿Cuántas {unidad}?" if unidad == "unidades" else "¿Cuántos kilos?",
                                           0.0, 200.0, 0.0, paso, key=f"rv_{mat}", format="%g")
                if cantidad > 0:
                    marca = SIN_MARCA
                    if mat in MATERIAL_MARCAS:
                        marca = st.pills("¿De qué marca son la mayoría?", [SIN_MARCA] + MATERIAL_MARCAS[mat],
                                         default=SIN_MARCA, key=f"rv_marca_{mat}") or SIN_MARCA
                    lineas.append({"material": mat, "kg": _kg(mat, cantidad, unidad), "marca": marca})
                st.write("")
    with contar:
        nota = st.text_area("Escríbelo como se lo dirías a un vecino", key="rv_nota",
                            placeholder="Por ejemplo, tengo dos kilos de cartón, 10 botellas de San Luis y 5 latas de Cristal")
        if nota.strip():
            entrega, motor = extraer(nota)
            filas = a_tabla(entrega)
            if filas:
                st.caption("Esto entendimos de tu mensaje" + (" con ayuda de Gemini" if motor == "gemini" else ""))
                st.markdown(ui.tabla(pd.DataFrame(filas).drop(columns="material")), unsafe_allow_html=True)
                lineas = [{"material": f["material"], "kg": f["kg"],
                           "marca": SIN_MARCA if f["Marca"] == "Sin marca" else f["Marca"]} for f in filas]
            else:
                st.info("No reconocimos materiales en tu mensaje. Prueba con algo como «3 botellas y 2 latas».")

    estilo.seccion("Paso 3", "¿Cuándo pasa el reciclador por tu calle?",
                   "El reciclador formalizado de tu sector sigue una ruta fija y pasa de madrugada, desde las 5 de la "
                   "mañana. Saca tu bolsa la noche anterior y te enviaremos un recordatorio por WhatsApp esa tarde.")
    st.markdown('<div class="banda"><b>Tu ruta pasa los martes y los viernes.</b> Saca tu bolsa la noche del lunes '
                'o del jueves, cerrada y con el adhesivo de tu vivienda a la vista.</div>', unsafe_allow_html=True)
    st.write("")
    c1, c2 = st.columns(2)
    dia = c1.date_input("Día de ruta en que dejarás tu bolsa", value=proximo_dia_ruta(), min_value=date.today(),
                        format="DD/MM/YYYY", key="rv_dia")
    with c2:
        turno = st.pills("¿Cómo entregarás tu bolsa?", TURNOS, default=TURNOS[0], key="rv_turno") or TURNOS[0]
    limpio = st.checkbox("Confirmo que mis residuos están limpios, secos y separados", key="rv_ok")

    estilo.seccion("Paso 4", "Genera tu ticket digital")
    if lineas:
        st.markdown(f'<div class="banda">Vas a entregar {_resumen(lineas)}. Ganarás unos '
                    f'<b>{_puntos(lineas)} EcoPuntos</b> cuando el reciclador lo valide.</div>', unsafe_allow_html=True)
    if st.button("Generar mi ticket digital", type="primary", width="stretch", disabled=not (lineas and limpio)):
        nuevo = {"id": f"T-{len(st.session_state.solicitudes) + 201:04d}", "codigo": codigo, "fecha": dia.isoformat(),
                 "turno": turno, "estado": "pendiente", "lineas": lineas}
        st.session_state.solicitudes.append(nuevo)
        st.session_state.ultimo_ticket = nuevo["id"]
    if not (lineas and limpio):
        faltan = []
        if not lineas:
            faltan.append("agrega al menos un material en el paso 2")
        if not limpio:
            faltan.append("confirma que tus residuos están limpios en el paso 3")
        st.markdown(f'<p class="nota">Para generar tu ticket, {" y ".join(faltan)}.</p>', unsafe_allow_html=True)

    ultimo = next((t for t in st.session_state.solicitudes if t["id"] == st.session_state.get("ultimo_ticket")), None)
    if ultimo:
        st.write("")
        estilo.ticket(ultimo["id"], f"<p><b>{direccion[ultimo['codigo']]}</b></p><p>{_resumen(ultimo['lineas'])}</p>"
                      f"<p>Recojo el {pd.Timestamp(ultimo['fecha']):%d/%m/%Y}. {_modo(ultimo['turno'])}</p>"
                      f"<p class='nota'>No necesitas esperar al reciclador. En el centro de acopio escanearán tu adhesivo "
                      f"o este código y pesarán tu bolsa. Cuando se valide, revisa tus puntos en Mi Bono Verde.</p>",
                      validado=ultimo["estado"] == "validado")
        import base64
        st.write("")
        contrib = padron.set_index("codigo").contribuyente.get(ultimo["codigo"], ultimo["codigo"])
        b1, b2 = st.columns(2)
        b1.download_button("Descargar el adhesivo QR de mi vivienda", base64.b64decode(estilo.qr(contrib)),
                           file_name=f"adhesivo-{contrib}.png", mime="image/png", width="stretch",
                           help="Imprímelo una sola vez y pégalo en tu bolsa o en tu puerta. Si no tienes impresora, "
                                "la municipalidad te lo entrega al empadronarte.")
        b2.download_button("Descargar el código de este ticket", base64.b64decode(estilo.qr(ultimo["id"])),
                           file_name=f"ticket-{ultimo['id']}.png", mime="image/png", width="stretch")


# ───────────────────────────────────────────────────────── reciclador
def lo_que_ganas(entregas: pd.DataFrame | None) -> None:
    """El retorno real del reciclador, con el pago municipal como base y el bono de las empresas como alianza."""
    estilo.seccion("Tu retorno", "Lo que ganas con Minka",
                   "Minka no te da más trabajo, sino que te paga mejor por el que ya haces y lo hace visible. La "
                   "municipalidad te retribuye por el servicio y las empresas suman un bono por cada kilo de sus envases.")
    if entregas is not None and len(entregas):
        e = entregas[entregas.reciclador == "REC-01"].copy()
        e["mes"] = e.fecha.astype(str).str[:7]
        mes = sorted(e.mes.unique())[-2] if e.mes.nunique() > 1 else e.mes.max()
        e = e[e.mes == mes]
        kg = float(e.kg.sum())
        kg_marca = float(e[e.marca != SIN_MARCA].kg.sum())
        viviendas = e.codigo.nunique()
        nombre_mes = pd.Timestamp(mes + "-01").month_name(locale=None)
        meses = {"January": "enero", "February": "febrero", "March": "marzo", "April": "abril", "May": "mayo",
                 "June": "junio", "July": "julio", "August": "agosto", "September": "septiembre",
                 "October": "octubre", "November": "noviembre", "December": "diciembre"}
        estilo.metricas([
            ("Kilos validados", f"{kg:,.0f} kg", f"Todo lo que se pesó a tu nombre en {meses.get(nombre_mes, mes)}."),
            ("Kilos de marcas clientes", f"{kg_marca:,.0f} kg", "Envases de las empresas que pagan por su trazabilidad."),
            ("Bono de las empresas", f"S/ {kg_marca * BONO_KG:,.2f}", "S/ 0.05 por cada kilo de marcas clientes, "
             "además de lo que ganas al vender el material."),
            ("Viviendas de tu ruta", f"{viviendas}", "Hogares que te entregaron al menos una bolsa en el mes."),
        ], destacar=2)
        st.write("")
    estilo.fila_tarjetas([
        estilo.tarjeta("Pago por el servicio", "Tu municipalidad recibe fondos del Programa de Incentivos del MEF por "
                       "integrar recicladores formalizados. Tus registros son la prueba que necesita para pagarte.", paso="1"),
        estilo.tarjeta("Bono por kilo", "Las empresas aliadas te pagan S/ 0.05 por cada kilo de sus envases que "
                       "se valida a tu nombre.", paso="2"),
        estilo.tarjeta("Más material y más limpio", "Las bolsas llegan separadas y tu ruta queda asignada, lo cual te "
                       "protege frente a quienes venden el material de manera informal.", paso="3"),
        estilo.tarjeta("Tu historial te respalda", "Cada kilo queda registrado con tu carné y respalda tu acceso a "
                       "equipos de protección, capacitación y otros beneficios.", paso="4"),
    ])
    st.markdown('<p class="nota">Montos de ejemplo. El pago municipal depende del convenio de cada distrito y el bono, '
                'de las empresas clientes.</p>', unsafe_allow_html=True)


def reciclador(padron: pd.DataFrame, direccion: dict, entregas: pd.DataFrame | None = None) -> None:
    estilo.portada("Para recicladores y centros de acopio", "Valida cada bolsa <em class='resalte'>en segundos</em>",
                   "Recoge las bolsas en tu ruta de madrugada. En el centro de acopio, el encargado de pesaje de tu "
                   "asociación escanea el adhesivo de cada vivienda, pesa y valida con un solo celular. No necesitas "
                   "un celular propio.", fondo="vidrio.jpg")
    estilo.guia("ciclo", "Recojo de madrugada y en el acopio pesamos todo junto. Mi trabajo queda registrado.")
    estilo.identidad("ciclo", f"Ruta de {RECICLADOR[0]} · Centro de acopio de Carapongo", RECICLADOR[1])
    lo_que_ganas(entregas)
    estilo.seccion("En el centro de acopio", "Valida las bolsas del día")
    estilo.como_usar([
        ("Recoge en tu ruta", "Los vecinos dejan su bolsa la noche anterior con el adhesivo de su vivienda."),
        ("Escanea", "Escanea el adhesivo o el ticket con la cámara, sube una foto o escribe el código."),
        ("Pesa y corrige", "Escribe los kilos reales. Si vino mezclado, apaga «Vino bien separado»."),
        ("Valida", "Presiona Validar. El vecino suma puntos y tu trabajo queda registrado."),
    ])
    pendientes, rapido = st.tabs(["Bolsas con adhesivo o ticket", "Registro rápido sin ticket"])

    with pendientes:
        lista = [t for t in st.session_state.solicitudes if t["estado"] == "pendiente"]
        modo = st.segmented_control("¿Cómo quieres buscar la bolsa?", ["Escanear el QR con la cámara", "Subir una foto del QR",
                                    "Escribir el código"], default="Escribir el código", key="modo_qr") or "Escribir el código"
        buscado = ""
        if modo == "Escribir el código":
            buscado = st.text_input("Código del adhesivo o del ticket", placeholder="Por ejemplo, C-159376 o T-0101")
        else:
            if modo == "Escanear el QR con la cámara":
                foto = st.camera_input("Apunta la cámara al adhesivo de la bolsa o al ticket")
            else:
                foto = st.file_uploader("Sube la foto o la captura del código QR", type=["png", "jpg", "jpeg"])
            if foto is not None:
                buscado = leer_qr(foto.getvalue())
                if buscado:
                    st.markdown(f'<div class="qr-ok">Leímos el código <b>{buscado}</b>. Revisa los datos y valídalo abajo.</div>',
                                unsafe_allow_html=True)
                else:
                    st.warning("No pudimos leer el código. Acerca más la cámara, evita reflejos o escribe el código.")
        if buscado.strip():
            b = buscado.strip().upper()
            if not b.startswith(("C-", "T-")) and b[:1].isdigit():
                b = "C-" + b
            vivienda = dict(zip(padron.contribuyente, padron.codigo)).get(b)
            lista = [t for t in lista if t["id"].upper() == b or (vivienda and t["codigo"] == vivienda)]
        st.markdown(f'<p class="nota">{len(lista)} {"recojo pendiente" if len(lista) == 1 else "recojos pendientes"}.</p>', unsafe_allow_html=True)
        if not lista:
            st.info("No hay bolsas pendientes con ese código. Revisa que esté bien escrito.")
        for t in lista:
            with st.container(border=True):
                st.markdown(f'<span class="etiqueta">{t["id"]}</span><span class="etiqueta clara">'
                            f'{direccion[t["codigo"]]}</span>', unsafe_allow_html=True)
                st.markdown(f"Recojo el **{pd.Timestamp(t['fecha']):%d/%m/%Y}**. {_modo(t['turno'])} "
                            f"El vecino declaró {_resumen(t['lineas'])}.")
                cols = st.columns(len(t["lineas"]) + 1)
                reales = []
                for c, l in zip(cols, t["lineas"]):
                    etiq = MATERIALES[l["material"]]["nombre"] + (f" de {l['marca']}" if l.get("marca", SIN_MARCA) != SIN_MARCA else "")
                    kg = c.number_input(f"{etiq}, kilos pesados", 0.0, 200.0, float(l["kg"]), 0.1,
                                        key=f"peso_{t['id']}_{l['material']}_{l.get('marca')}", format="%g")
                    reales.append({"material": l["material"], "kg": kg, "marca": l.get("marca", SIN_MARCA)})
                bien = cols[-1].toggle("Vino bien separado", value=True, key=f"ok_{t['id']}")
                if st.button(f"Validar {t['id']}", type="primary", key=f"val_{t['id']}"):
                    for l in reales:
                        if l["kg"] > 0:
                            st.session_state.nuevas.append({
                                "id_entrega": t["id"], "fecha": t["fecha"], "codigo": t["codigo"], "reciclador": "REC-01",
                                "material": l["material"], "marca": l["marca"], "kg": l["kg"], "bien_segregado": bien,
                                "fuente": "ticket digital"})
                    t["estado"] = "validado"
                    st.toast(f"{t['id']} validado. Ya suma al Bono Verde del vecino.")
                    st.rerun()
        hechos = [t for t in st.session_state.solicitudes if t["estado"] == "validado"]
        if hechos:
            st.markdown("#### Validados hoy")
            st.markdown(ui.tabla(pd.DataFrame([{"Ticket": t["id"], "Dirección": direccion[t["codigo"]],
                                                "Entregó": _resumen(t["lineas"])} for t in hechos])),
                        unsafe_allow_html=True)

    with rapido:
        st.markdown('<p class="nota">Úsalo cuando el vecino no generó su ticket. Escribe su código de contribuyente y lo que '
                    'te entregó, y Minka lo convierte en un registro con materiales, marcas y kilos.</p>',
                    unsafe_allow_html=True)
        izq, der = st.columns(2, gap="large")
        with izq:
            vivienda = ingresar(padron, "rr")
            fecha = st.date_input("Fecha del recojo", value=date.today(), format="DD/MM/YYYY", key="rr_fecha")
            nota = st.text_area("¿Qué te entregó el vecino?", height=120, key="rr_nota",
                                value="3 kilos de cartón, 12 botellas de San Luis y 5 latas de Cristal, todo limpio y separado")
            procesar = st.button("Registrar recojo", type="primary", width="stretch")
        with der:
            if not (procesar and nota.strip()):
                st.markdown(estilo.tarjeta("Así queda el registro", "Materiales, kilos y EcoPuntos, con una marca que "
                                           "indica si la entrega vino bien separada. Prueba a escribir que vino mezclada."),
                            unsafe_allow_html=True)
                return
            entrega, motor = extraer(nota)
            filas = a_tabla(entrega)
            if not filas:
                st.warning("No encontramos materiales en la nota. Prueba con algo como «2 kilos de cartón y 8 botellas».")
                return
            id_entrega = f"R-{len(st.session_state.nuevas) + 1:04d}"
            for f in filas:
                st.session_state.nuevas.append({
                    "id_entrega": id_entrega, "fecha": fecha.isoformat(), "codigo": vivienda, "reciclador": "REC-01",
                    "material": f["material"], "kg": f["kg"], "bien_segregado": entrega.bien_segregado,
                    "marca": SIN_MARCA if f["Marca"] == "Sin marca" else f["Marca"], "fuente": "registro rápido"})
            motor_txt = "Leído con Gemini" if motor == "gemini" else "Leído con reglas de respaldo"
            st.markdown(f'<span class="etiqueta">{id_entrega}</span><span class="etiqueta clara">{motor_txt}</span>',
                        unsafe_allow_html=True)
            tabla = pd.DataFrame(filas).drop(columns="material").rename(columns={"kg": "Kilos"})
            st.markdown(ui.tabla(tabla), unsafe_allow_html=True)
            if entrega.bien_segregado:
                st.success("Entrega válida. Ya cuenta para el Bono Verde del vecino.")
            else:
                st.error("Entrega mezclada. Queda registrada, pero no suma puntos.")
