"""Genera el padrón y el historial de entregas SINTÉTICOS de un distrito piloto.

No usamos datos de vecinos reales: el curso lo prohíbe sin consentimiento y, además, ninguna
municipalidad los publica. Las viviendas, nombres de sector y entregas son inventados, pero
caen dentro del polígono real de Lurigancho-Chosica y siguen las reglas de su ordenanza.

    python scripts/generar_padron.py

Escribe data/padron_sintetico.csv (una fila por vivienda) y data/entregas_sinteticas.csv
(una fila por material entregado).
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from shapely.geometry import Point, shape

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.reglas import MATERIAL_MARCAS, SIN_MARCA  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
DISTRITO = "150118"  # Lurigancho (Chosica), código INEI
SEMILLA = 20261110
N_VIVIENDAS = 160

# Centros poblados del distrito (aproximados) donde se ubican las viviendas sintéticas
SECTORES = {
    "Chosica": (-11.937, -76.697),
    "Ñaña": (-11.985, -76.835),
    "Carapongo": (-11.990, -76.860),
    "Cajamarquilla": (-11.975, -76.905),
    "Huachipa": (-12.000, -76.925),
}
RECICLADORES = ["REC-01", "REC-02", "REC-03"]
# Lunes de recojo selectivo, de septiembre a la primera semana de noviembre de 2026
FECHAS = pd.date_range("2026-09-07", "2026-11-02", freq="W-MON")
# Probabilidad de que un material aparezca en una entrega y kg típicos por entrega
MEZCLA = {"papel_carton": (0.85, 1.8), "plastico_pet": (0.75, 0.6), "plastico_otro": (0.40, 0.4),
          "vidrio": (0.30, 1.2), "metal": (0.35, 0.3), "tetrapak": (0.30, 0.3)}


def viviendas(rng: np.random.Generator, poligono) -> pd.DataFrame:
    filas = []
    nombres = list(SECTORES)
    while len(filas) < N_VIVIENDAS:
        sector = nombres[rng.integers(len(nombres))]
        lat0, lon0 = SECTORES[sector]
        lat, lon = lat0 + rng.normal(0, 0.006), lon0 + rng.normal(0, 0.008)
        if not poligono.contains(Point(lon, lat)):
            continue
        i = len(filas) + 1
        filas.append({
            "codigo": f"V-{i:04d}",
            "contribuyente": f"C-{rng.integers(100000, 999999)}",
            "direccion": f"Mz. {chr(65 + rng.integers(20))} Lt. {rng.integers(1, 40)}, {sector}",
            "sector": sector,
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "arbitrio_limpieza": round(float(rng.uniform(9, 24)), 2),  # S/ al mes, valor sintético
            "inscrito": bool(rng.random() < 0.7),
            "constancia": float(rng.beta(5, 1.2)),  # qué tan seguido entrega, no se guarda
        })
    return pd.DataFrame(filas)


def entregas(rng: np.random.Generator, padron: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for v in padron[padron.inscrito].itertuples():
        reciclador = RECICLADORES[rng.integers(len(RECICLADORES))]
        for fecha in FECHAS:
            if rng.random() > v.constancia:
                continue
            id_entrega = f"E-{len(filas) + 1:05d}"
            bien = bool(rng.random() > 0.07)
            for material, (p, kg) in MEZCLA.items():
                if rng.random() < p:
                    opciones = MATERIAL_MARCAS.get(material)
                    con_marca = 0.8 if material in ("metal", "plastico_pet", "vidrio", "tetrapak") else 0.1  # el cartón rara vez se identifica
                    marca = opciones[rng.integers(len(opciones))] if opciones and rng.random() < con_marca else SIN_MARCA
                    filas.append({
                        "id_entrega": id_entrega, "fecha": fecha.date().isoformat(), "codigo": v.codigo,
                        "reciclador": reciclador, "material": material, "marca": marca,
                        "kg": round(float(rng.gamma(2.0, kg / 2.0)), 2), "bien_segregado": bien,
                        "fuente": "sintético",
                    })
    return pd.DataFrame(filas)


def main() -> None:
    rng = np.random.default_rng(SEMILLA)
    mapa = json.loads((RAIZ / "data" / "lima_distritos.geojson").read_text(encoding="utf-8"))
    poligono = next(shape(f["geometry"]) for f in mapa["features"] if f["properties"]["IDDIST"] == DISTRITO)

    padron = viviendas(rng, poligono)
    historial = entregas(rng, padron)
    padron.drop(columns="constancia").to_csv(RAIZ / "data" / "padron_sintetico.csv", index=False)
    historial.to_csv(RAIZ / "data" / "entregas_sinteticas.csv", index=False)
    print(f"{len(padron)} viviendas ({padron.inscrito.sum()} inscritas) y "
          f"{historial.id_entrega.nunique()} entregas sintéticas")


if __name__ == "__main__":
    main()
