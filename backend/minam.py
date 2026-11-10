"""Contexto distrital con los datos abiertos del MINAM (se completa al tener el CSV)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


def cargar(data: Path) -> pd.DataFrame | None:
    archivos = sorted(data.glob("minam_*.csv"))
    if not archivos:
        return None
    return pd.read_csv(archivos[0], encoding="latin-1", sep=None, engine="python")


def mostrar(df: pd.DataFrame, mapa: dict, distrito: str, kg_programa: float) -> None:
    import streamlit as st
    st.dataframe(df.head())
