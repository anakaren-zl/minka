"""Recorta los datos abiertos del MINAM a Lima Metropolitana y el Callao.

Fuente: Plataforma Nacional de Datos Abiertos, conjuntos «Composición de residuos sólidos
domiciliarios» y «Generación anual de residuos sólidos domiciliarios y municipales» (corte
12/12/2024). Los archivos completos pesan varios MB, así que en el repo solo queda el recorte.

    python scripts/preparar_minam.py ruta/minam_composicion.csv ruta/minam_generacion.csv
"""
import sys
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data"


def leer(ruta: str) -> pd.DataFrame:
    df = pd.read_csv(ruta, sep=";", encoding="latin-1", dtype=str)
    df.columns = [c.strip().replace(" ", "_") for c in df.columns]
    for c in df.columns:
        df[c] = df[c].str.strip()
        convertido = pd.to_numeric(df[c].str.replace(",", ".", regex=False), errors="coerce")
        if convertido.notna().mean() > 0.95:  # columnas numéricas, con coma o punto decimal
            df[c] = convertido
    return df


def lima(df: pd.DataFrame) -> pd.DataFrame:
    return df[df.UBIGEO.astype(int).astype(str).str.zfill(6).str[:4].isin(["1501", "0701"])].copy()


if __name__ == "__main__":
    comp, gen = leer(sys.argv[1]), leer(sys.argv[2])
    lima(comp).drop(columns=["FECHA_CORTE", "N_SEC"]).to_csv(DATA / "minam_lima_composicion.csv", index=False)
    lima(gen).drop(columns=["FECHA_CORTE"]).to_csv(DATA / "minam_lima_generacion.csv", index=False)
    print("Listo: data/minam_lima_composicion.csv y data/minam_lima_generacion.csv")
