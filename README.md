# JetPort (prototype)

JetPort is a local ASGI development server with automatic TLS for localhost,
request capture, a minimal inspector UI, and a request replay helper.

This archive contains a working prototype scaffold meant for local development.

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install uvicorn typer cryptography httpx aiofiles jinja2
pip install -e .
jetport run example_app:app
```

Visit: https://127.0.0.1:8443/  (use -k with curl or accept browser warning)
Inspector: https://127.0.0.1:8443/__jetport__/
