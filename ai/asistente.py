"""Asistente de dudas con RAG en miniatura (sesión 08 del curso).

1. Recuperación: parte ai/conocimiento.md en secciones y elige las más parecidas a la pregunta
   por palabras en común, sin tildes ni palabras vacías.
2. Generación: Gemini responde usando solo esas secciones. Si no hay clave o la API falla,
   se devuelve la sección más parecida tal cual, así el asistente nunca deja de responder.

    from ai.asistente import responder
    texto, fuentes, motor = responder("¿Cuánto descuento me dan?")
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

from ai.extraer import MODELO, _clave

CONOCIMIENTO = Path(__file__).with_name("conocimiento.md")
VACIAS = set("""a al algo como con cual cuales cuando de del el ella en es esta este hay la las lo los me mi
mis no o para pero por que quien se si sin sobre su sus te tu tus un una y ya puedo hago debo""".split())


def _normalizar(texto: str) -> list[str]:
    t = unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()
    palabras = re.findall(r"[a-z0-9]+", t)
    return [p[:6] for p in palabras if p not in VACIAS and len(p) > 2]  # raíz corta: separar, separo


def secciones() -> list[tuple[str, str]]:
    bloques = re.split(r"^# ", CONOCIMIENTO.read_text(encoding="utf-8"), flags=re.M)
    return [(b.split("\n", 1)[0].strip(), b.split("\n", 1)[1].strip()) for b in bloques if b.strip()]


def buscar(pregunta: str, k: int = 2) -> list[tuple[str, str]]:
    q = set(_normalizar(pregunta))
    puntaje = []
    for titulo, texto in secciones():
        titulo_n, texto_n = set(_normalizar(titulo)), set(_normalizar(texto))
        puntaje.append((3 * len(q & titulo_n) + len(q & texto_n), titulo, texto))
    puntaje.sort(key=lambda x: -x[0])
    return [(t, x) for s, t, x in puntaje[:k] if s > 0]


PROMPT = """Eres Vera, una vecina que ayuda a otros vecinos a entender el Bono Verde y ReciclaGov.
Responde en español peruano, cálido y claro, en tres oraciones como máximo, usando SOLO la
información de abajo. Si la respuesta no está ahí, dilo con amabilidad y sugiere consultar a la
municipalidad. No uses listas ni emojis.

Información:
{contexto}

Pregunta del vecino: {pregunta}"""


def responder(pregunta: str) -> tuple[str, list[str], str]:
    encontrados = buscar(pregunta)
    if not encontrados:
        return ("Esa pregunta se me escapa. Te recomiendo consultarla con tu municipalidad, en la "
                "subgerencia de limpieza pública o de gestión ambiental.", [], "reglas")
    fuentes = [t for t, _ in encontrados]
    clave = _clave()
    if clave:
        try:
            from google import genai
            contexto = "\n\n".join(f"{t}. {x}" for t, x in encontrados)
            r = genai.Client(api_key=clave).models.generate_content(
                model=MODELO, contents=PROMPT.format(contexto=contexto, pregunta=pregunta))
            return r.text.strip(), fuentes, "gemini"
        except Exception as e:
            print(f"Gemini falló ({e}); respondo con la sección más cercana.")
    return encontrados[0][1], fuentes, "reglas"
