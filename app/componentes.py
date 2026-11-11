"""Piezas visuales en HTML para que nada se vea como una hoja de cálculo.

Barras comparativas, ranking, tablas con estilo, línea de tiempo de entregas e íconos de
materiales. Todas usan la paleta de estilo.py con contraste alto (azul noche sobre blanco y
acento sol para lo destacado).
"""
import html

import pandas as pd

NOCHE, MUSGO, SOL, LAGUNA, HOJA = "#1E4D3A", "#3E8E63", "#6DBE45", "#4E9A6E", "#BFD37A"

# íconos simples de cada material, en trazo blanco sobre un círculo de color
_TRAZO = 'fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"'
ICONOS = {
    "papel_carton": (NOCHE, f'<path {_TRAZO} d="M14 22 L32 14 L50 22 L50 42 L32 50 L14 42 Z M14 22 L32 30 L50 22 M32 30 V50"/>'),
    "plastico_pet": (LAGUNA, f'<path {_TRAZO} d="M28 12 H36 V18 C42 21 44 26 44 30 V52 H20 V30 C20 26 22 21 28 18 Z M20 36 H44"/>'),
    "metal": ("#4E7A5C", f'<path {_TRAZO} d="M20 16 H44 V48 H20 Z M20 22 H44 M20 42 H44 M27 13 H37"/>'),
    "vidrio": (MUSGO, f'<path {_TRAZO} d="M28 10 H36 V22 C42 25 44 30 44 34 V54 H20 V34 C20 30 22 25 28 22 Z M24 40 H40"/>'),
    "tetrapak": (SOL, f'<path {_TRAZO} d="M20 22 L26 12 H38 L44 22 V52 H20 Z M20 22 H44 M30 12 V6 H36"/>'),
    "plastico_otro": ("#7A9E3B", f'<path {_TRAZO} d="M18 22 H46 L43 52 H21 Z M25 22 C25 12 39 12 39 22"/>'),
}


def icono(material: str, tamano: int = 64) -> str:
    color, trazo = ICONOS[material]
    return (f'<svg viewBox="0 0 64 64" width="{tamano}" height="{tamano}" aria-hidden="true">'
            f'<circle cx="32" cy="32" r="32" fill="{color}"/>{trazo}</svg>')


def tarjeta_material(material: str, nombre: str, puntos_kg: int) -> str:
    return (f'<div class="mat">{icono(material, 58)}<div class="mat-nom">{html.escape(nombre)}</div>'
            f'<div class="mat-pts">{puntos_kg} EcoPuntos por kilo</div></div>')


def _num(v: float, unidad: str) -> str:
    """Toneladas sin decimales, porcentajes con uno y kilos con dos."""
    if unidad.startswith("t"):
        return f"{v:,.0f}"
    return f"{v:,.1f}" if unidad == "%" else f"{v:,.2f}"


def barras(filas: list[tuple[str, float, str]], unidad: str = "kg", destacar: str | None = None) -> str:
    """Barras horizontales con etiqueta y valor. filas = (etiqueta, valor, detalle)."""
    tope = max([v for _, v, _ in filas] + [1e-9])
    partes = []
    for i, (etq, v, det) in enumerate(filas):
        color = SOL if etq == destacar else (NOCHE if i % 2 == 0 else LAGUNA)
        partes.append(
            f'<div class="barra"><div class="barra-top"><span class="barra-etq">{html.escape(etq)}</span>'
            f'<span class="barra-val">{_num(v, unidad)} {unidad}</span></div>'
            f'<div class="barra-pista"><div class="barra-relleno" style="width:{max(v / tope * 100, 2):.1f}%;'
            f'background:{color}"></div></div>'
            + (f'<div class="barra-det">{html.escape(det)}</div>' if det else "") + '</div>')
    return f'<div class="panel">{"".join(partes)}</div>'


def ranking(df: pd.DataFrame, etiqueta: str, valor: str, detalle: str, unidad: str) -> str:
    """Ranking con medallas para los tres primeros."""
    medallas = ["#6DBE45", "#BFD37A", "#D0E6A6"]
    tope = df[valor].max() or 1
    filas = []
    for i, r in enumerate(df.itertuples()):
        fondo = medallas[i] if i < 3 else "#E7F1D2"
        texto = NOCHE
        filas.append(
            f'<div class="rk"><div class="rk-pos" style="background:{fondo};color:{texto}">{i + 1}</div>'
            f'<div class="rk-cuerpo"><div class="barra-top"><span class="barra-etq">{html.escape(str(getattr(r, etiqueta)))}</span>'
            f'<span class="barra-val">{_num(getattr(r, valor), unidad)} {unidad}</span></div>'
            f'<div class="barra-pista"><div class="barra-relleno" style="width:{getattr(r, valor) / tope * 100:.1f}%;'
            f'background:{SOL if i == 0 else NOCHE}"></div></div>'
            f'<div class="barra-det">{html.escape(str(getattr(r, detalle)))}</div></div></div>')
    return f'<div class="panel">{"".join(filas)}</div>'


def tabla(df: pd.DataFrame, alto: int | None = None) -> str:
    """Tabla HTML con encabezado azul noche, filas alternas y números alineados a la derecha."""
    cab = "".join(f"<th>{html.escape(str(c))}</th>" for c in df.columns)
    cuerpo = []
    for _, fila in df.iterrows():
        celdas = []
        for v in fila:
            num = isinstance(v, (int, float)) and not isinstance(v, bool)
            txt = f"{v:,.2f}".rstrip("0").rstrip(".") if isinstance(v, float) else html.escape(str(v))
            celdas.append(f'<td class="{"num" if num else ""}">{txt}</td>')
        cuerpo.append(f"<tr>{''.join(celdas)}</tr>")
    estilo_alto = f'style="max-height:{alto}px"' if alto else ""
    return (f'<div class="tabla" {estilo_alto}><table><thead><tr>{cab}</tr></thead>'
            f'<tbody>{"".join(cuerpo)}</tbody></table></div>')


def linea_tiempo(entregas: list[dict]) -> str:
    """Entregas del vecino como tarjetas en una línea de tiempo."""
    if not entregas:
        return '<div class="panel vacio-panel">Aún no tienes entregas este mes. Tu primera entrega empieza en Recicla ahora.</div>'
    items = []
    for e in entregas:
        ok = e["valida"]
        items.append(
            f'<div class="lt-item"><div class="lt-punto" style="background:{MUSGO if ok else SOL}"></div>'
            f'<div class="lt-caja"><div class="lt-fecha">{e["fecha"]}</div>'
            f'<div class="lt-txt"><b>{e["kg"]:.1f} kg</b> · {e["puntos"]} EcoPuntos · {html.escape(e["detalle"])}</div>'
            f'<span class="lt-est {"ok" if ok else "no"}">{"Válida" if ok else "No suma"}</span></div></div>')
    return f'<div class="panel lt">{"".join(items)}</div>'


def comparar(yo: float, barrio: float, sector: str) -> str:
    """Comparación visual entre la vivienda y el promedio de su sector."""
    tope = max(yo, barrio, 1e-9)
    mejor = yo >= barrio
    msg = "Vas por encima de tu barrio. ¡Sigue así!" if mejor else f"Te faltan {barrio - yo:.1f} kg para igualar a {sector}."
    return (f'<div class="panel cmp">'
            f'<div class="cmp-fila"><span class="cmp-etq">Tú</span><div class="barra-pista grande"><div class="barra-relleno" '
            f'style="width:{yo / tope * 100:.1f}%;background:{SOL}"></div></div>'
            f'<span class="cmp-val">{yo:.1f} kg</span></div>'
            f'<div class="cmp-fila"><span class="cmp-etq">{html.escape(sector)}</span><div class="barra-pista grande">'
            f'<div class="barra-relleno" style="width:{barrio / tope * 100:.1f}%;background:{NOCHE}"></div></div>'
            f'<span class="cmp-val">{barrio:.1f} kg</span></div>'
            f'<div class="cmp-msg">{msg}</div></div>')


# ilustraciones planas para perfiles, valores, noticias y empresas (trazo blanco sobre color)
_T = 'fill="none" stroke="#FFFFFF" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"'
DIBUJOS = {
    "muni": f'<path {_T} d="M14 50 H50 M18 50 V30 M26 50 V30 M38 50 V30 M46 50 V30 M14 30 H50 L32 16 Z M30 50 V42 H34 V50"/>',
    "empresa": f'<path {_T} d="M12 50 V30 L22 36 V30 L32 36 V22 H40 V14 H46 V50 Z M12 50 H52 M20 43 H24 M30 43 H34"/>',
    "vecino": f'<path {_T} d="M14 30 L32 15 L50 30 M19 26 V50 H45 V26 M28 50 V39 H36 V50"/>',
    "reciclador": f'<path {_T} d="M12 42 H38 V24 H12 Z M38 30 H46 L52 37 V42 H38 M18 46 a4 4 0 1 0 0.1 0 M44 46 a4 4 0 1 0 0.1 0"/>',
    "transparencia": f'<path {_T} d="M10 32 C18 20 46 20 54 32 C46 44 18 44 10 32 Z M32 26 a6 6 0 1 0 0.1 0"/>',
    "colaboracion": f'<path {_T} d="M22 28 a6 6 0 1 0 0.1 0 M42 28 a6 6 0 1 0 0.1 0 M12 48 C12 38 32 38 32 48 M32 48 C32 38 52 38 52 48"/>',
    "equidad": f'<path {_T} d="M32 14 V50 M22 50 H42 M14 22 H50 M14 22 L8 36 H20 Z M50 22 L44 36 H56 Z"/>',
    "sostenibilidad": f'<path {_T} d="M18 46 C14 30 26 16 48 16 C48 36 36 48 18 46 Z M18 46 C26 36 34 30 42 24"/>',
    "innovacion": f'<path {_T} d="M24 38 C18 33 18 20 32 16 C46 20 46 33 40 38 V44 H24 Z M26 50 H38"/>',
    "reconocimiento": f'<path {_T} d="M32 12 L37 24 L50 25 L40 34 L43 47 L32 40 L21 47 L24 34 L14 25 L27 24 Z"/>',
    "botella": f'<path {_T} d="M28 12 H36 V18 C42 21 44 26 44 30 V52 H20 V30 C20 26 22 21 28 18 Z M20 36 H44"/>',
    "lata": f'<path {_T} d="M20 16 H44 V48 H20 Z M20 22 H44 M20 42 H44 M27 13 H37"/>',
    "carrito": f'<path {_T} d="M10 16 H18 L24 40 H46 L52 22 H20 M26 48 a3 3 0 1 0 0.1 0 M44 48 a3 3 0 1 0 0.1 0"/>',
    "planta": f'<path {_T} d="M14 50 H50 M20 50 V34 H44 V50 M32 34 V20 M24 20 H40 M28 12 H36"/>',
    "noticia": f'<path {_T} d="M14 16 H44 V48 H14 Z M44 24 H50 V44 a4 4 0 0 1 -8 0 M20 24 H38 M20 32 H38 M20 40 H32"/>',
}


def dibujo(nombre: str, color: str = NOCHE, tamano: int = 64, fondo: bool = True) -> str:
    """Ilustración simple de la librería DIBUJOS, sobre un círculo de color."""
    circulo = f'<circle cx="32" cy="32" r="32" fill="{color}"/>' if fondo else ""
    return (f'<svg viewBox="0 0 64 64" width="{tamano}" height="{tamano}" aria-hidden="true">'
            f'{circulo}{DIBUJOS[nombre]}</svg>')
