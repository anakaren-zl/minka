# Minka

Proyecto final de la Diplomatura de Ciencia de Datos (Q-Lab PUCP). Startup (antes ReciclaGov) que digitaliza el Bono Verde
municipal (artículo 70 del D. L. 1278): el reciclador registra cada recojo, el vecino ve sus EcoPuntos y la
municipalidad descarga el padrón de beneficiarios del descuento en arbitrios.

## Cómo correr

```
uv run --python 3.12 --with-requirements requirements.txt python -m streamlit run app/streamlit_app.py
```

## Estructura

- `app/streamlit_app.py`: la app (inicio, tu municipalidad, recicla ahora, reciclador, mi Bono Verde, municipalidad, empresas y Vera).
- `ai/extraer.py`: salidas estructuradas con Gemini (Pydantic) y extractor de reglas de respaldo.
- `backend/`: reglas del bono, cálculos del padrón y datos abiertos del MINAM recortados a Lima (`backend/minam.py`).
- Identidad visual en `app/estilo.py`: paleta original de verdes y azules (noche #234257, musgo #3E8E63, sol #F2A541), dibujos ecológicos flotando al fondo y logotipo solo con el nombre en Montserrat Black.
- `scripts/`: preparación del mapa y generación de datos sintéticos.
- `data/`: solo datos públicos o sintéticos. Nunca datos personales reales.
- `docs/research/`: notas de las conversaciones con usuarios.

## Reglas

- Nunca subir `.env`, `.streamlit/secrets.toml`, audios ni transcripciones de entrevistas.
- La autora es nueva en Git: explicar paso a paso y usar GitHub Desktop para ramas y commits.
- Textos del README y de docs/: redacción 100 % académica en español, sin dos puntos ni doble guion
  en la prosa y con conectores académicos.
