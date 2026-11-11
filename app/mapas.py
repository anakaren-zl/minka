"""Mapas satelitales con Folium (sesión 06 del curso).

Base de imágenes satelitales de Esri World Imagery con una capa de nombres de calles y
lugares encima, para que el mapa se vea real y siga siendo legible.
"""
import folium

SATELITE = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
ETIQUETAS = ("https://server.arcgisonline.com/ArcGIS/rest/services/Reference/"
             "World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}")
ATRIBUCION = "Imágenes satelitales de Esri, Maxar, Earthstar Geographics y la comunidad de usuarios SIG"


def mapa_satelital(centro: list[float], zoom: int) -> folium.Map:
    m = folium.Map(location=centro, zoom_start=zoom, tiles=None, control_scale=True)
    folium.TileLayer(SATELITE, attr=ATRIBUCION, name="Satélite").add_to(m)
    folium.TileLayer(ETIQUETAS, attr="Esri", name="Nombres", overlay=True, opacity=0.9).add_to(m)
    return m
