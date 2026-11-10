"""Reglas del Bono Verde: qué vale cada material y quién gana el descuento.

Cada municipalidad fija su propio Bono Verde por ordenanza (artículo 70 del D. L. 1278).
Los valores por defecto siguen a los distritos que ya lo aplican:

- Villa María del Triunfo: 4 tickets al mes dan el bono, un 20 % de descuento.
- Lurigancho-Chosica (Ordenanza 353-MDL, 2024): 15 % de descuento en limpieza pública.

Aquí todo es configurable desde el tablero municipal.
"""
from __future__ import annotations

from dataclasses import dataclass

# ───────────────────────────────────────────────────────── materiales
# Los nombres son los que pide la IA al estructurar una entrega (ai/extraer.py).
MATERIALES = {
    "papel_carton": {"nombre": "Papel y cartón", "puntos_kg": 10, "kg_unidad": 0.20},
    "plastico_pet": {"nombre": "Botellas PET", "puntos_kg": 25, "kg_unidad": 0.03},
    "plastico_otro": {"nombre": "Otros plásticos", "puntos_kg": 15, "kg_unidad": 0.05},
    "vidrio": {"nombre": "Vidrio", "puntos_kg": 8, "kg_unidad": 0.35},
    "metal": {"nombre": "Latas y metales", "puntos_kg": 30, "kg_unidad": 0.015},
    "tetrapak": {"nombre": "Tetra Pak", "puntos_kg": 12, "kg_unidad": 0.03},
    "organico": {"nombre": "Orgánicos", "puntos_kg": 5, "kg_unidad": 0.25},
}
# kg_unidad: peso aproximado de una unidad (una botella PET de 625 ml pesa unos 30 g)


@dataclass
class ReglasBono:
    """Lo que decide la ordenanza de cada municipalidad."""

    entregas_minimas: int = 4  # entregas en el periodo para ganar el bono
    descuento: float = 0.15  # fracción del arbitrio de limpieza pública
    kg_minimos: float = 0.5  # una entrega con menos de esto no cuenta


def puntos(material: str, kg: float) -> int:
    """EcoPuntos de una línea de la entrega."""
    return round(MATERIALES[material]["puntos_kg"] * kg)


# ───────────────────────────────────────────────────────── marcas
# Las empresas solo cuentan para sus indicadores los envases de sus propias marcas (conversación 2).
# Catálogo referencial de marcas públicas del mercado peruano, agrupadas por empresa titular. Sirve
# para demostrar la trazabilidad por marca; la demo no implica ninguna alianza con estas empresas.
LATA, PET, VID, TETRA, CAJA, BOLSA = "metal", "plastico_pet", "vidrio", "tetrapak", "papel_carton", "plastico_otro"
CATALOGO = {
    "Backus (AB InBev)": {
        "Cristal": [LATA, VID], "Pilsen Callao": [LATA, VID], "Cusqueña": [LATA, VID], "Arequipeña": [LATA, VID],
        "San Juan": [LATA, VID], "Corona": [LATA, VID], "Stella Artois": [LATA, VID], "Guaraná Backus": [PET, LATA],
        "San Mateo": [PET]},
    "Arca Continental Lindley (Sistema Coca-Cola)": {
        "Coca-Cola": [PET, LATA, VID], "Inca Kola": [PET, LATA, VID], "Fanta": [PET, LATA], "Sprite": [PET, LATA],
        "San Luis": [PET], "Powerade": [PET], "Frugos del Valle": [TETRA, PET]},
    "Grupo AJE": {
        "Big Cola": [PET], "Cielo": [PET], "Sporade": [PET], "Volt": [PET, LATA], "Pulp": [TETRA, PET],
        "Cifrut": [PET]},
    "CBC Peruana (Pepsi)": {
        "Pepsi": [PET, LATA], "7Up": [PET, LATA], "Concordia": [PET], "Triple Kola": [PET], "Gatorade": [PET]},
    "Gloria": {"Gloria": [LATA, TETRA], "Pura Vida": [LATA, TETRA], "Bonlé": [LATA, TETRA]},
    "Nestlé Perú": {"Ideal": [LATA], "Nescafé": [VID, CAJA], "Nesquik": [CAJA, TETRA]},
    "Laive": {"Laive": [TETRA, LATA]},
    "Alicorp": {"Primor": [PET], "Cocinero": [PET], "Bolívar": [BOLSA, CAJA], "Opal": [BOLSA], "Don Vittorio": [BOLSA, CAJA]},
}
EMPRESAS = {empresa: list(marcas) for empresa, marcas in CATALOGO.items()}
EMPRESA_DE = {marca: empresa for empresa, marcas in CATALOGO.items() for marca in marcas}
MARCAS = list(EMPRESA_DE)
SIN_MARCA = "Otra o no sé"
MATERIAL_MARCAS = {}
for _empresa, _marcas in CATALOGO.items():
    for _marca, _materiales in _marcas.items():
        for _m in _materiales:
            MATERIAL_MARCAS.setdefault(_m, []).append(_marca)
MATERIALES_EMPRESA = {e: sorted({m for mats in marcas.values() for m in mats}) for e, marcas in CATALOGO.items()}
