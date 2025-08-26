import asyncio, importlib, ssl
from pathlib import Path
import typer, uvicorn
from .tls import ensure_local_cert
from .middleware import JetPortMiddleware
from .inspector import create_inspector_app
from .replay import replay_request_file

app = typer.Typer(help="JetPort CLI")
DEFAULT_PORT = 8443
JETPORT_DIR = Path.home() / ".jetport"

@app.command()
def run(app_path: str, host: str = "127.0.0.1", port: int = DEFAULT_PORT, https: bool = True, inspector_path: str = "/__jetport__/"):
    """Run an ASGI app under JetPort: e.g. jetport run example_app:app"""
    JETPORT_DIR.mkdir(parents=True, exist_ok=True)
    ssl_context = None
    if https:
        cert_file, key_file = ensure_local_cert(JETPORT_DIR)
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(certfile=str(cert_file), keyfile=str(key_file))
    module_name, app_attr = app_path.split(":")
    module = importlib.import_module(module_name)
    asgi_app = getattr(module, app_attr)
    inspector = create_inspector_app(JETPORT_DIR)
    wrapped = JetPortMiddleware(asgi_app, inspector_app=inspector, storage_dir=JETPORT_DIR, inspector_path=inspector_path)
    # config = uvicorn.Config(app=wrapped, host=host, port=port, ssl=ssl_context, log_level="info", loop="asyncio")
    
    config = uvicorn.Config(
        app=wrapped,
        host=host,
        port=port,
        ssl_certfile=str(cert_file),
        ssl_keyfile=str(key_file),
        log_level="info"
    )
    server = uvicorn.Server(config)
    asyncio.run(server.serve())

@app.command()
def replay(logfile: str, url: str = None, times: int = 1, delay: float = 0.0):
    """Replay a JetPort-saved log file to target URL"""
    asyncio.run(replay_request_file(logfile, override_url=url, times=times, delay=delay))
