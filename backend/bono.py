"""Cálculos del Bono Verde: puntos por vivienda, padrón de beneficiarios y ahorro.

Reemplaza el cruce manual que hoy hacen las municipalidades. En San Juan de Lurigancho, por
ejemplo, los recicladores entregan registros semanales firmados y cada dos meses alguien
cruza esa lista con los pagos de arbitrios antes de aplicar el descuento (Ordenanza 325).

    from backend.bono import resumen_viviendas, padron_beneficiarios
    resumen = resumen_viviendas(padron, entregas, "2026-10")
    beneficiarios = padron_beneficiarios(resumen, ReglasBono())
"""
from __future__ import annotations

import pandas as pd

from backend.reglas import MATERIALES, ReglasBono


def con_puntos(entregas: pd.DataFrame) -> pd.DataFrame:
    """Agrega EcoPuntos a cada línea. Una entrega mal segregada no suma puntos."""
    e = entregas.copy()
    e["puntos"] = [
        round(MATERIALES[m]["puntos_kg"] * kg) if ok else 0
        for m, kg, ok in zip(e.material, e.kg, e.bien_segregado)
    ]
    e["mes"] = e.fecha.astype(str).str[:7]
    return e


def resumen_viviendas(padron: pd.DataFrame, entregas: pd.DataFrame, mes: str, reglas: ReglasBono) -> pd.DataFrame:
    """Una fila por vivienda con lo que entregó en el mes."""
    e = con_puntos(entregas)
    e = e[e.mes == mes]
    por_entrega = e.groupby(["codigo", "id_entrega"]).agg(
        kg=("kg", "sum"), puntos=("puntos", "sum"), bien=("bien_segregado", "all"))
    por_entrega["valida"] = por_entrega.bien & (por_entrega.kg >= reglas.kg_minimos)

    r = por_entrega.groupby("codigo").agg(
        entregas=("kg", "size"), entregas_validas=("valida", "sum"),
        kg=("kg", "sum"), puntos=("puntos", "sum")).reset_index()
    r = padron.merge(r, on="codigo", how="left").fillna({"entregas": 0, "entregas_validas": 0, "kg": 0, "puntos": 0})
    r["cumple"] = r.inscrito & (r.entregas_validas >= reglas.entregas_minimas)
    r["descuento_soles"] = (r.cumple * r.arbitrio_limpieza * reglas.descuento).round(2)
    return r


def padron_beneficiarios(resumen: pd.DataFrame) -> pd.DataFrame:
    """Lo que la municipalidad le pasa al área de rentas para aplicar el descuento."""
    cols = {"codigo": "Vivienda", "contribuyente": "Código de contribuyente", "direccion": "Dirección",
            "entregas_validas": "Entregas válidas", "kg": "kg reciclados", "descuento_soles": "Descuento (S/)"}
    b = resumen[resumen.cumple][list(cols)].rename(columns=cols)
    b["kg reciclados"] = b["kg reciclados"].round(1)
    return b.sort_values("Vivienda").reset_index(drop=True)


def indicadores(resumen: pd.DataFrame) -> dict:
    """Cifras para el tablero municipal."""
    inscritas = resumen[resumen.inscrito]
    return {
        "inscritas": int(len(inscritas)),
        "participan": int((inscritas.entregas > 0).sum()),
        "beneficiarias": int(resumen.cumple.sum()),
        "kg": float(resumen.kg.sum()),
        "descuento_total": float(resumen.descuento_soles.sum()),
    }
