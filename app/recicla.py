"""El corazón de ReciclaGov: pasar del ticket de papel al ticket digital.

1. El vecino, en «Recicla ahora», dice qué va a reciclar y cuándo, y recibe un ticket con QR.
2. El reciclador, en su vista, busca el ticket (o lo escanea), pesa lo que recibe y lo valida.
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

# material: (unidad sugerida, paso del contador, ícono)
FORMULARIO = {
    "papel_carton": ("kg", 0.5, ":material/inventory_2:"),
    "plastico_pet": ("unidades", 1.0, ":material/water_bottle:"),
    "metal": ("unidades", 1.0, ":material/recycling:"),
    "vidrio": ("unidades", 1.0, ":material/wine_bar:"),
    "tetrapak": ("unidades", 1.0, ":material/local_drink:"),
    "plastico_otro": ("kg", 0.5, ":material/shopping_bag:"),
}
TURNOS = ["Mañana (de 8 a 12 horas)", "Tarde (de 14 a 18 horas)"]


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


def elegir_vivienda(etiqueta: dict, clave: str) -> str:
    """Código de vivienda escrito, como en el recibo de arbitrios, en lugar de una lista desplegable."""
    codigos = list(etiqueta)
    escrito = st.text_input("Código de mi vivienda", value=codigos[4], key=f"viv_{clave}",
                            help="Está en tu recibo de arbitrios. En esta demo van de V-0001 a V-0160.").strip().upper()
    if escrito not in etiqueta:
        st.warning(f"No encontré {escrito} entre las viviendas inscritas. Uso {codigos[4]} para la demo.")
        escrito = codigos[4]
    st.markdown(f'<span class="etiqueta">{etiqueta[escrito].split("·")[1].strip()}</span>', unsafe_allow_html=True)
    return escrito


def _kg(material: str, cantidad: float, unidad: str) -> float:
    return round(cantidad if unidad == "kg" else cantidad * MATERIALES[material]["kg_unidad"], 2)


def _puntos(lineas: list[dict]) -> int:
    return sum(round(MATERIALES[l["material"]]["puntos_kg"] * l["kg"]) for l in lineas)


def _resumen(lineas: list[dict]) -> str:
    def marca(l):
        return f" de {l['marca']}" if l.get("marca", SIN_MARCA) != SIN_MARCA else ""
    return ", ".join(f"{MATERIALES[l['material']]['nombre'].lower()}{marca(l)} {l['kg']:g} kg" for l in lineas)


# ───────────────────────────────────────────────────────── vecino
def recicla_ahora(etiqueta: dict, padron: pd.DataFrame) -> None:
    estilo.portada("Recicla ahora", "Tu reciclaje, <em class='resalte'>en tres pasos</em>",
                   "Cuéntanos qué separaste y cuándo podemos pasar. Recibirás un ticket digital con código QR que "
                   "reemplaza al ticket de papel. Cuando el reciclador lo valide, sumará a tu Bono Verde.")
    estilo.guia("vera", "Enjuaga botellas y latas, y aplasta las cajas. Así tu entrega vale más.")

    estilo.seccion("Paso 1", "¿Quién recicla?")
    codigo = elegir_vivienda(etiqueta, "rv")

    estilo.seccion("Paso 2", "¿Qué separaste?")
    marcar, contar = st.tabs(["Marcar materiales", "Contarlo con mis palabras"])
    lineas = []
    with marcar:
        cols = st.columns(3, gap="medium")
        for i, (mat, (unidad, paso, _)) in enumerate(FORMULARIO.items()):
            with cols[i % 3]:
                st.markdown(ui.tarjeta_material(mat, MATERIALES[mat]["nombre"], MATERIALES[mat]["puntos_kg"]),
                            unsafe_allow_html=True)
                cantidad = st.number_input(f"Cantidad en {unidad}", 0.0, 200.0, 0.0, paso, key=f"rv_{mat}", format="%g")
                if cantidad > 0:
                    marca = SIN_MARCA
                    if mat in MATERIAL_MARCAS:
                        marca = st.pills("¿De qué marca?", [SIN_MARCA] + MATERIAL_MARCAS[mat], default=SIN_MARCA,
                                         key=f"rv_marca_{mat}") or SIN_MARCA
                    lineas.append({"material": mat, "kg": _kg(mat, cantidad, unidad), "marca": marca})
                st.write("")
    with contar:
        nota = st.text_area("Escríbelo como lo dirías", key="rv_nota",
                            placeholder="Por ejemplo, tengo dos kilos de cartón, 10 botellas de San Luis y 5 latas de Cristal")
        if nota.strip():
            entrega, motor = extraer(nota)
            filas = a_tabla(entrega)
            if filas:
                st.caption("Esto entendí de tu mensaje" + (" con Gemini" if motor == "gemini" else ""))
                st.markdown(ui.tabla(pd.DataFrame(filas).drop(columns="material")), unsafe_allow_html=True)
                lineas = [{"material": f["material"], "kg": f["kg"],
                           "marca": SIN_MARCA if f["Marca"] == "Sin marca" else f["Marca"]} for f in filas]

    estilo.seccion("Paso 3", "¿Cuándo pasamos?")
    c1, c2 = st.columns(2)
    dia = c1.date_input("Día del recojo", value=date.today() + timedelta(days=1), min_value=date.today(),
                        format="DD/MM/YYYY", key="rv_dia")
    with c2:
        turno = st.pills("Turno", TURNOS, default=TURNOS[0], key="rv_turno") or TURNOS[0]
    limpio = st.checkbox("Confirmo que mis residuos están limpios, secos y separados", key="rv_ok")

    if lineas:
        st.markdown(f'<div class="banda">Vas a entregar {_resumen(lineas)}. Ganarás unos '
                    f'<b>{_puntos(lineas)} EcoPuntos</b> cuando el reciclador lo valide.</div>', unsafe_allow_html=True)
    if st.button("Generar mi ticket digital", type="primary", width="stretch", disabled=not (lineas and limpio)):
        nuevo = {"id": f"T-{len(st.session_state.solicitudes) + 201:04d}", "codigo": codigo, "fecha": dia.isoformat(),
                 "turno": turno, "estado": "pendiente", "lineas": lineas}
        st.session_state.solicitudes.append(nuevo)
        st.session_state.ultimo_ticket = nuevo["id"]
    if not (lineas and limpio):
        st.markdown('<p class="nota">Agrega al menos un material y confirma que está separado para generar tu ticket.</p>',
                    unsafe_allow_html=True)

    ultimo = next((t for t in st.session_state.solicitudes if t["id"] == st.session_state.get("ultimo_ticket")), None)
    if ultimo:
        estilo.seccion("Listo", "Tu ticket digital")
        estilo.ticket(ultimo["id"], f"<p><b>{etiqueta[ultimo['codigo']]}</b></p><p>{_resumen(ultimo['lineas'])}</p>"
                      f"<p>Recojo el {pd.Timestamp(ultimo['fecha']):%d/%m/%Y}, turno {ultimo['turno'].lower()}.</p>"
                      f"<p class='nota'>Muéstrale este código al reciclador. Ya no necesitas tickets de papel.</p>",
                      validado=ultimo["estado"] == "validado")


# ───────────────────────────────────────────────────────── reciclador
def reciclador(etiqueta: dict) -> None:
    estilo.portada("Para recicladores", "Valida cada recojo <em class='resalte'>en segundos</em>",
                   "Busca el ticket del vecino o escanea su código QR, pesa lo que recibes y confírmalo. "
                   "Si el vecino no tiene ticket, regístralo escribiendo o dictando lo que te entregó.")
    estilo.guia("ciclo", "Pesa, confirma y listo. Tu trabajo queda registrado con tu código.")
    st.markdown('''<div class="pasos-guia">
      <div class="p"><span class="n">1</span><b>Pide el ticket</b><span>El vecino te muestra su código QR o te dice su
      código, por ejemplo T-0101.</span></div>
      <div class="p"><span class="n">2</span><b>Búscalo</b><span>Escanéalo con la cámara o escribe el código en el
      buscador de abajo.</span></div>
      <div class="p"><span class="n">3</span><b>Pesa y corrige</b><span>Pon los kilos reales que recibiste. Si vino
      mezclado, apaga «Bien separado».</span></div>
      <div class="p"><span class="n">4</span><b>Valida</b><span>Presiona Validar. El vecino suma puntos y tu trabajo
      queda registrado.</span></div></div>''', unsafe_allow_html=True)
    pendientes, rapido = st.tabs(["Recojos con ticket", "Registro rápido sin ticket"])

    with pendientes:
        lista = [t for t in st.session_state.solicitudes if t["estado"] == "pendiente"]
        buscado = st.text_input("Código del ticket", placeholder="Escanea el QR o escribe el código, por ejemplo T-0101")
        if buscado.strip():
            lista = [t for t in lista if t["id"].lower() == buscado.strip().lower()]
        if not lista:
            st.info("No hay recojos pendientes con ese código.")
        for t in lista:
            with st.container(border=True):
                st.markdown(f"#### {t['id']}  ·  {etiqueta[t['codigo']]}")
                st.caption(f"Recojo el {pd.Timestamp(t['fecha']):%d/%m/%Y}, turno {t['turno'].lower()}. "
                           f"El vecino declaró {_resumen(t['lineas'])}.")
                cols = st.columns(len(t["lineas"]) + 1)
                reales = []
                for c, l in zip(cols, t["lineas"]):
                    etiq = MATERIALES[l["material"]]["nombre"] + (f" de {l['marca']}" if l.get("marca", SIN_MARCA) != SIN_MARCA else "")
                    kg = c.number_input(f"{etiq} (kg pesados)", 0.0, 200.0, float(l["kg"]), 0.1,
                                        key=f"peso_{t['id']}_{l['material']}_{l.get('marca')}", format="%g")
                    reales.append({"material": l["material"], "kg": kg, "marca": l.get("marca", SIN_MARCA)})
                bien = cols[-1].toggle("Bien separado", value=True, key=f"ok_{t['id']}")
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
            st.markdown(ui.tabla(pd.DataFrame([{"Ticket": t["id"], "Vivienda": t["codigo"], "Entregó": _resumen(t["lineas"])}
                                               for t in hechos])), unsafe_allow_html=True)

    with rapido:
        izq, der = st.columns(2, gap="large")
        with izq:
            vivienda = elegir_vivienda(etiqueta, "rr")
            fecha = st.date_input("Fecha del recojo", value=date.today(), format="DD/MM/YYYY", key="rr_fecha")
            nota = st.text_area("Lo que entregó el vecino", height=120, key="rr_nota",
                                value="3 kilos de cartón, 12 botellas de San Luis y 5 latas de Cristal, todo limpio y separado")
            procesar = st.button("Registrar recojo", type="primary", width="stretch")
        with der:
            if not (procesar and nota.strip()):
                st.markdown(estilo.tarjeta("Así queda el registro", "Materiales, kilos y EcoPuntos, con una marca de si "
                                           "la entrega vino bien separada. Prueba a escribir que vino mezclada."),
                            unsafe_allow_html=True)
                return
            entrega, motor = extraer(nota)
            filas = a_tabla(entrega)
            if not filas:
                st.warning("No encontré materiales en la nota. Prueba con algo como 2 kilos de cartón y 8 botellas.")
                return
            id_entrega = f"R-{len(st.session_state.nuevas) + 1:04d}"
            for f in filas:
                st.session_state.nuevas.append({
                    "id_entrega": id_entrega, "fecha": fecha.isoformat(), "codigo": vivienda, "reciclador": "REC-01",
                    "material": f["material"], "kg": f["kg"], "bien_segregado": entrega.bien_segregado,
                    "marca": SIN_MARCA if f["Marca"] == "Sin marca" else f["Marca"], "fuente": "registro rápido"})
            motor_txt = "Leído por Gemini" if motor == "gemini" else "Leído por reglas de respaldo"
            st.markdown(f'<span class="etiqueta">{id_entrega}</span><span class="etiqueta">{motor_txt}</span>',
                        unsafe_allow_html=True)
            tabla = pd.DataFrame(filas).drop(columns="material").rename(columns={"kg": "Kilos"})
            st.markdown(ui.tabla(tabla), unsafe_allow_html=True)
            if entrega.bien_segregado:
                st.success("Entrega válida. Ya cuenta para el Bono Verde del vecino.")
            else:
                st.error("Entrega mezclada. Queda registrada, pero no suma puntos.")
