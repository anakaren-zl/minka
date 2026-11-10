"""Datos reales del MINAM sobre los residuos domiciliarios de Lima Metropolitana y el Callao.

Fuente: Plataforma Nacional de Datos Abiertos, «Composición de residuos sólidos domiciliarios» y
«Generación anual de residuos sólidos domiciliarios y municipales» (corte del 12/12/2024).
Los archivos se recortan a Lima con scripts/preparar_minam.py. Las cantidades están en toneladas
al año.

    from backend import minam
    comp, gen = minam.cargar(Path("data"))
    perfil = minam.perfil(comp, "150118")
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

# Columnas del MINAM agrupadas en palabras que entiende cualquier vecino
GRUPOS = {
    "Papel y cartón": ["PAPEL_BLANCO", "PAPEL_PERIODICO", "PAPEL_MIXTO", "CARTON_BLANCO", "CARTON_MARRON", "CARTON_MIXTO"],
    "Botellas PET": ["TEREFLATO_POLIETILENO"],
    "Otros plásticos": ["POLIETILENO_ALTA_DENSIDAD", "POLIETILENO_BAJA_DENSIDAD", "POLIPROPILENO", "POLIESTIRENO",
                        "POLICLORURO_VINILO"],
    "Vidrio": ["VIDRIO_TRANSPARENTE", "VIDRIO_OTROS_COLORES", "VIDRIOS_OTROS"],
    "Latas y metales": ["LATA", "METALES_FERROSOS", "ALUMINIO", "OTROS_METALES"],
    "Tetra Pak": ["TETRABRICK"],
}
NO_RECICLABLES = {
    "Restos de comida y jardín": ["ALIMENTOS", "MALEZA", "OTROS_ORGANICOS"],
    "Residuos sanitarios": ["SANITARIOS"],
    "Bolsas plásticas": ["BOLSAS_PLASTICAS"],
}
# material de Minka (backend/reglas.py) → grupo del MINAM
DE_MATERIAL = {"papel_carton": "Papel y cartón", "plastico_pet": "Botellas PET", "plastico_otro": "Otros plásticos",
               "vidrio": "Vidrio", "metal": "Latas y metales", "tetrapak": "Tetra Pak"}


def nombre(texto: str) -> str:
    """SAN JUAN DE LURIGANCHO → San Juan de Lurigancho."""
    t = str(texto).title()
    for chico in [" De ", " Del ", " La ", " Las ", " Los ", " Y "]:
        t = t.replace(chico, chico.lower())
    return t


def en_texto(grupos: list[str]) -> str:
    """Lista de grupos en minúscula, salvo las siglas, unida con comas e y."""
    g = [x.lower().replace("pet", "PET").replace("tetra pak", "Tetra Pak") for x in grupos]
    return g[0] if len(g) == 1 else ", ".join(g[:-1]) + " y " + g[-1]


def cargar(data: Path) -> tuple[pd.DataFrame, pd.DataFrame] | None:
    comp, gen = data / "minam_lima_composicion.csv", data / "minam_lima_generacion.csv"
    if not (comp.exists() and gen.exists()):
        return None
    c, g = pd.read_csv(comp), pd.read_csv(gen)
    c["UBIGEO"] = c.UBIGEO.astype(str).str.zfill(6)
    g["UBIGEO"] = g.UBIGEO.astype(str).str.zfill(6)
    for nombre, cols in {**GRUPOS, **NO_RECICLABLES}.items():
        c[nombre] = c[[f"QRESIDUOS_{x}" for x in cols]].sum(axis=1)
    c["Reciclables"] = c[list(GRUPOS)].sum(axis=1)
    return c, g


def anio_reciente(comp: pd.DataFrame) -> int:
    return int(comp.PERIODO.max())


def perfil(comp: pd.DataFrame, ubigeo: str, anio: int | None = None) -> dict | None:
    """Toneladas al año del distrito, total y por tipo de residuo."""
    anio = anio or anio_reciente(comp)
    fila = comp[(comp.UBIGEO == ubigeo) & (comp.PERIODO == anio)]
    if fila.empty:
        return None
    r = fila.iloc[0]
    return {
        "anio": anio,
        "distrito": nombre(r.DISTRITO),
        "poblacion": int(r.POB_TOTAL),
        "total": float(r.QRESIDUOS_DOM),
        "reciclables": float(r.Reciclables),
        "por_grupo": {g: float(r[g]) for g in GRUPOS},
        "no_reciclables": {g: float(r[g]) for g in NO_RECICLABLES},
        "kg_hab_dia": float(r.GPC_DOM),
    }


def serie(gen: pd.DataFrame, ubigeo: str) -> pd.DataFrame:
    """Toneladas de residuos domiciliarios por año."""
    s = gen[gen.UBIGEO == ubigeo][["ANIO", "GENERACION_DOM_URBANA_TANIO"]].sort_values("ANIO")
    return s.rename(columns={"ANIO": "anio", "GENERACION_DOM_URBANA_TANIO": "toneladas"})


def potencial(comp: pd.DataFrame, grupos: list[str], anio: int | None = None, n: int = 8) -> pd.DataFrame:
    """Distritos de Lima con más toneladas al año de los materiales indicados."""
    anio = anio or anio_reciente(comp)
    d = comp[comp.PERIODO == anio].copy()
    d["toneladas"] = d[grupos].sum(axis=1)
    d["distrito"] = d.DISTRITO.map(nombre)
    d["detalle"] = [f"{p:,.0f} habitantes · {t / p * 1000:.1f} kg por habitante al año"
                    for t, p in zip(d.toneladas, d.POB_TOTAL)]
    return d.nlargest(n, "toneladas")[["distrito", "toneladas", "detalle", "UBIGEO"]]
