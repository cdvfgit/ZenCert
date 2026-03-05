# Sistema Automatizado de Certificados de Artes Marciales

MVP 1.0 — En desarrollo

## Estructura

```
sistema/
├── app.py                  # Streamlit — vista pública e interna
├── cli.py                  # CLI — interfaz del operador
├── core/
│   ├── lector_sheets.py    # Conexión y operaciones Google Sheets
│   ├── procesador.py       # Formateo, Gemini, kanjis, fechas
│   ├── generador.py        # Generación PPTX
│   └── registro.py         # Manejo JSON de registros
├── plantillas/
│   └── ocoa/               # Plantillas PPTX por organización
├── data/
│   └── registros.json      # Último número por organización
├── salida/
│   └── ocoa/               # Certificados generados
├── credenciales.json       # Cuenta de servicio Google Cloud (NO subir)
└── .env                    # GEMINI_API_KEY (NO subir)
```

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Editar .env con tu API Key de Gemini
# Colocar credenciales.json de Google Cloud en la raíz
```

## Credenciales requeridas

- `credenciales.json` — cuenta de servicio de Google Cloud con acceso a Sheets API
- `.env` — variable `GEMINI_API_KEY` con tu clave de Gemini Flash
