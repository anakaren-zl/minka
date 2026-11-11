"""Convierte lo que escribe o dicta el reciclador en un registro estructurado.

Es la técnica de salidas estructuradas de la sesión 08: se le pasa al LLM un esquema de
Pydantic y el modelo responde con un JSON que lo cumple. Así, «3 kilos de cartón y 10
botellas, todo limpio» se vuelve una lista de materiales con su peso, sin formularios.

    from ai.extraer import extraer
    entrega = extraer("3 kilos de cartón y 10 botellas, todo limpio")

Si no hay clave de Gemini, o la API falla, un extractor de reglas hace lo mismo para los
casos simples. La app nunca se cae en la demo.
"""
from __future__ import annotations

import os
import re
from typing import Literal

from pydantic import BaseModel, Field

from backend.reglas import MARCAS, MATERIALES, puntos

Material = Literal["papel_carton", "plastico_pet", "plastico_otro", "vidrio", "metal", "tetrapak", "organico"]
MODELO = os.getenv("GEMINI_MODEL", "gemini-flash-latest")


# ───────────────────────────────────────────────────────── esquema
class Linea(BaseModel):
    material: Material
    cantidad: float = Field(gt=0)
    unidad: Literal["kg", "unidades"]
    marca: str | None = Field(default=None, description="Marca del envase si la nota la menciona, por ejemplo Cristal o San Luis")


class Entrega(BaseModel):
    lineas: list[Linea]
    bien_segregado: bool = Field(description="False si el texto dice que venía mezclado, sucio o con basura común")
    observacion: str = Field(default="", description="Algo que el reciclador comenta sobre la entrega, en pocas palabras")


PROMPT = """Eres el asistente de un reciclador formalizado de una municipalidad del Perú.
Convierte su nota sobre una entrega de residuos en un registro estructurado.

Materiales posibles:
- papel_carton: papel, cartón, periódicos, cajas
- plastico_pet: botellas de plástico transparente (agua, gaseosa)
- plastico_otro: otros plásticos (bolsas, envases de yogur, baldes, tápers)
- vidrio: botellas y frascos de vidrio
- metal: latas, chatarra, aluminio
- tetrapak: cajas de leche o jugo
- organico: restos de comida, cáscaras

Reglas:
- Si dice kilos, kg o "k", la unidad es "kg". Si cuenta objetos (botellas, latas, cajas), la unidad es "unidades".
- Si un material aparece sin cantidad, usa cantidad 1 y unidad "unidades".
- bien_segregado es false solo si la nota dice que venía mezclado, sucio o con basura.
- No inventes materiales que no estén en la nota.
- Si la nota dice la marca (por ejemplo «5 latas de Cristal»), ponla en marca. Si no la dice, deja marca vacía.
  Si hay envases del mismo material de marcas distintas, crea una línea por marca.

Nota del reciclador:
{texto}"""


# ───────────────────────────────────────────────────────── con Gemini
def _clave() -> str | None:
    """La clave viene de .env en local o de los secrets de Streamlit Cloud."""
    clave = os.getenv("GEMINI_API_KEY")
    if clave:
        return clave
    try:
        import streamlit as st
        return st.secrets.get("GEMINI_API_KEY")
    except Exception:
        return None


def _con_gemini(texto: str, clave: str) -> Entrega:
    from google import genai
    from google.genai import types

    cliente = genai.Client(api_key=clave)
    respuesta = cliente.models.generate_content(
        model=MODELO,
        contents=PROMPT.format(texto=texto),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Entrega,
            temperature=0,
        ),
    )
    return respuesta.parsed if isinstance(respuesta.parsed, Entrega) else Entrega.model_validate_json(respuesta.text)


# ───────────────────────────────────────────────────────── con reglas
SINONIMOS = {
    "papel_carton": r"cart[oó]n(?:es)?|papel(?:es)?|peri[oó]dicos?|cajas? de cart[oó]n",
    "plastico_pet": r"botellas?(?: de pl[aá]stico| pet)?|pet",
    "plastico_otro": r"bolsas?|pl[aá]sticos?|t[aá]pers?|envases? de pl[aá]stico",
    "vidrio": r"vidrios?|frascos?|botellas? de vidrio",
    "metal": r"latas?|latitas?|metal(?:es)?|aluminio|chatarra",
    "tetrapak": r"tetra ?paks?|cajas? de leche|cajas? de jugo",
    "organico": r"org[aá]nicos?|c[aá]scaras?|restos de comida",
}
NUMERO = r"(\d+(?:[.,]\d+)?|un|una|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|medio)"
PALABRAS = {"un": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6,
            "siete": 7, "ocho": 8, "nueve": 9, "diez": 10, "medio": 0.5}


def _numero(s: str) -> float:
    return PALABRAS.get(s.lower(), None) or float(s.replace(",", "."))


def _con_reglas(texto: str) -> Entrega:
    """Busca «<número> [kilos de] <material>». Sirve para notas simples."""
    t = texto.lower()
    lineas, usados = [], []
    # vidrio y tetrapak primero, para que «botellas de vidrio» no se cuente como PET
    for material in ["vidrio", "tetrapak", "papel_carton", "metal", "plastico_pet", "plastico_otro", "organico"]:
        patron = rf"{NUMERO}\s*(kg|kilos?|k)?\s*(?:de\s+)?(?:{SINONIMOS[material]})\b"
        for m in re.finditer(patron, t):
            if any(a <= m.start() < b for a, b in usados):
                continue
            usados.append(m.span())
            unidad = "kg" if m.group(2) else "unidades"
            resto = t[m.end():m.end() + 25]
            marca = next((mc for mc in MARCAS if mc.lower() in resto), None)
            lineas.append(Linea(material=material, cantidad=_numero(m.group(1)), unidad=unidad, marca=marca))
    mezclado = bool(re.search(r"mezclad|sucio|con basura|no segreg|mal segreg", t))
    return Entrega(lineas=lineas, bien_segregado=not mezclado, observacion="")


# ───────────────────────────────────────────────────────── uso
def extraer(texto: str) -> tuple[Entrega, str]:
    """Devuelve la entrega y qué motor la produjo ('gemini' o 'reglas')."""
    clave = _clave()
    if clave:
        try:
            return _con_gemini(texto, clave), "gemini"
        except Exception as e:  # sin internet, cuota agotada, modelo retirado...
            print(f"Gemini falló ({e}); uso el extractor de reglas.")
    return _con_reglas(texto), "reglas"


def a_tabla(entrega: Entrega) -> list[dict]:
    """Una fila por material, con su peso en kg y sus EcoPuntos."""
    filas = []
    for l in entrega.lineas:
        kg = l.cantidad if l.unidad == "kg" else l.cantidad * MATERIALES[l.material]["kg_unidad"]
        filas.append({
            "material": l.material,
            "Material": MATERIALES[l.material]["nombre"],
            "Cantidad": f"{l.cantidad:g} {l.unidad}",
            "Marca": l.marca or "Sin marca",
            "kg": round(kg, 2),
            "EcoPuntos": puntos(l.material, kg),
        })
    return filas
