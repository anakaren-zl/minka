"""Certificado de material reciclado trazable para empresas (modelo mixto).

Cada recojo que registra un reciclador queda con fecha, distrito, sector y kg por material.
Con eso se arma un certificado que una embotelladora puede usar para demostrar cuánto PET
posconsumo se recuperó en el Perú (Ley 30884). No se comparten direcciones de los vecinos.
"""
from __future__ import annotations

import pandas as pd

TARIFA_TONELADA = 150.0  # S/ por tonelada trazada que paga la empresa (supuesto de negocio)
FONDO_PREMIOS = 0.55     # parte de la tarifa que se devuelve a los vecinos como premios (supuesto)


def certificado(entregas: pd.DataFrame, padron: pd.DataFrame, material: str, mes: str) -> pd.DataFrame:
    """Una fila por entrega válida del material, sin datos personales."""
    e = entregas.merge(padron[["codigo", "sector"]], on="codigo", how="left")
    e = e[(e.material == material) & e.bien_segregado & (e.fecha.astype(str).str[:7] == mes)]
    return (e[["id_entrega", "fecha", "sector", "reciclador", "kg"]]
            .rename(columns={"id_entrega": "Entrega", "fecha": "Fecha", "sector": "Sector",
                             "reciclador": "Reciclador", "kg": "kg"})
            .sort_values(["Fecha", "Entrega"]).reset_index(drop=True))


def resumen(cert: pd.DataFrame) -> dict:
    toneladas = cert.kg.sum() / 1000
    return {
        "entregas": int(len(cert)),
        "toneladas": float(toneladas),
        "sectores": int(cert.Sector.nunique()),
        "pago": float(toneladas * TARIFA_TONELADA),
        "premios": float(toneladas * TARIFA_TONELADA * FONDO_PREMIOS),
    }
