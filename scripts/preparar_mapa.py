"""Recorta el mapa distrital del Perú a Lima Metropolitana y el Callao.

El GeoJSON de origen es el de la sesión 06 del curso
(sessions/06-geoespacial/lab/Data/peru_distrital_simple.geojson). Solo se guardan los
distritos de Lima Metropolitana y el Callao, para que el mapa de la app cargue rápido.

    python scripts/preparar_mapa.py ruta/a/peru_distrital_simple.geojson
"""
import json
import sys
from pathlib import Path

PROVINCIAS = {"1501": "LIMA", "0701": "CALLAO"}  # IDPROV del INEI
SALIDA = Path(__file__).resolve().parents[1] / "data" / "lima_distritos.geojson"
CAMPOS = ["IDDIST", "NOMBDIST", "NOMBPROV"]


def main() -> None:
    origen = Path(sys.argv[1])
    mapa = json.loads(origen.read_text(encoding="utf-8"))

    distritos = [
        {"type": "Feature", "geometry": f["geometry"],
         "properties": {k: f["properties"][k] for k in CAMPOS}}
        for f in mapa["features"]
        if f["properties"]["IDPROV"] in PROVINCIAS
    ]

    SALIDA.parent.mkdir(exist_ok=True)
    SALIDA.write_text(json.dumps({"type": "FeatureCollection", "features": distritos}), encoding="utf-8")
    print(f"{len(distritos)} distritos guardados en {SALIDA}")


if __name__ == "__main__":
    main()
