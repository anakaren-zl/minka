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


PROMPT = """Eres Vera, una vecina de Carapongo que ayuda a otros vecinos a entender el Bono Verde y Minka.
Responde en español peruano, cálido y claro, en tres oraciones como máximo, usando SOLO la
información de abajo. Si la respuesta no está ahí, dilo con amabilidad y sugiere consultar a la
municipalidad. No uses listas ni emojis.

Información:
{contexto}

Pregunta del vecino: {pregunta}"""


SALUDOS = {"hola", "holi", "buenas", "buenos", "hey", "alo", "saludos", "que tal", "qué tal"}
GRACIAS = {"gracias", "graciass", "muchas gracias", "genial", "perfecto", "chevere", "chévere", "ok", "oki", "listo"}
TEMAS = ("Puedo contarte qué es el Bono Verde, cuánto descuento dan, cómo separar tus residuos, cómo funciona "
         "el ticket digital o qué hacer si tu distrito no tiene el beneficio.")


def charla(pregunta: str) -> str | None:
    """Respuestas para saludos y frases sueltas, que no necesitan buscar en la guía."""
    t = unicodedata.normalize("NFKD", pregunta.lower()).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-z ]", " ", t).strip()
    palabras = set(t.split())
    if not t:
        return None
    if palabras & {"adios", "chau", "chao", "bye"}:
        return "¡Hasta pronto, vecino! Gracias por reciclar. Cada aporte cuenta."
    if t in GRACIAS or (palabras & {"gracias"} and len(palabras) <= 4):
        return "¡Con gusto! Si te queda alguna duda sobre el reciclaje o tu Bono Verde, aquí estoy."
    if ("quien eres" in t or "como te llamas" in t or "que eres" in t) and len(palabras) <= 8:
        return ("Soy Vera, vecina de Carapongo y guía de Minka. Te ayudo a entender el Bono Verde, a separar bien "
                "tus residuos y a usar tu ticket digital.")
    if ("que puedes hacer" in t or "en que me ayudas" in t or "ayuda" == t or "que haces" in t) and len(palabras) <= 8:
        return TEMAS
    if (palabras & SALUDOS or t.startswith("buen")) and len(palabras) <= 5:
        return f"¡Hola! Soy Vera, tu vecina guía de Minka. {TEMAS} ¿Por dónde empezamos?"
    if "como estas" in t and len(palabras) <= 6:
        return "¡Muy bien, gracias! Feliz de ayudarte a reciclar. ¿Qué te gustaría saber?"
    return None


def responder(pregunta: str) -> tuple[str, list[str], str]:
    corta = charla(pregunta)
    if corta:
        return corta, [], "charla"
    encontrados = buscar(pregunta)
    if not encontrados:
        return ("Todavía no sé responder eso, pero sigo aprendiendo. " + TEMAS +
                " Para otros temas, tu municipalidad puede orientarte en la subgerencia de limpieza pública "
                "o de gestión ambiental.", [], "reglas")
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
