# JobHunterRD

Asistente personal de búsqueda de empleo para posiciones IT en República Dominicana.

## Descripción

JobHunterRD monitorea múltiples portales de empleo, filtra vacantes relevantes para tu perfil y envía notificaciones por Telegram. Construido como un agente modular y extensible.

## Portales Soportados

- Aldaba
- Computrabajo
- LinkedIn Jobs
- Google Jobs (deshabilitado por defecto)

## Requisitos

- Python 3.12+
- Playwright (solo si se requiere para portales con JS pesado)

## Instalación

```bash
pip install -r requirements.txt
playwright install chromium
```

## Configuración

1. Copia `.env.example` a `.env` y agrega tu token de Telegram:
```env
TELEGRAM_BOT_TOKEN=tu_token
TELEGRAM_CHAT_ID=tu_chat_id
```

2. Edita `config.yaml` para ajustar provincias, palabras clave, empresas excluidas, etc.

## Uso

```bash
python main.py
```

El sistema ejecutará una búsqueda inmediata y luego se repetirá cada 20 minutos.

## Estructura

```
JobHunterRD/
  app/
    config/     # Configuración YAML + loader
    database/   # Modelos SQLAlchemy + repositorio
    filters/    # Motor de filtros
    models/     # Modelos Pydantic
    notifications/  # Notificaciones Telegram
    scheduler/  # APScheduler
    scrapers/   # Scrapers por portal
    services/   # Orquestador
    utils/      # Hash, logger
  data/         # Base de datos SQLite
  logs/         # Archivos de log
  tests/        # Tests
```

## Extender

Agrega un nuevo portal creando un archivo en `app/scrapers/` que herede de `BaseScraper` e implemente el método `scrape()`. El orquestador lo registrará automáticamente.
