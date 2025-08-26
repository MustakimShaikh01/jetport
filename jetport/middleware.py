import json, time, traceback
from pathlib import Path

class JetPortMiddleware:
    def __init__(self, app, inspector_app, storage_dir: Path, inspector_path: str = "/__jetport__/"):
        self.app = app
        self.inspector_app = inspector_app
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir = self.storage_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        self.inspector_path = inspector_path.rstrip("/") + "/"

    def __call__(self, scope):
        path = scope.get("path", "")
        if path.startswith(self.inspector_path):
            new_scope = dict(scope)
            new_scope["path"] = path[len(self.inspector_path)-1:] or "/"
            return self.inspector_app(new_scope)
        return self._wrap_app(scope)

    def _wrap_app(self, scope):
        if scope["type"] not in ("http","websocket"):
            return self.app(scope)

        async def asgi(receive, send):
            start = time.time()
            body_chunks = []
            async def capture_receive():
                msg = await receive()
                if msg.get('type') == 'http.request':
                    b = msg.get('body', b'')
                    if b:
                        body_chunks.append(b)
                return msg

            response_body = bytearray()
            status = None

            async def capture_send(message):
                nonlocal status
                if message.get('type') == 'http.response.start':
                    status = message.get('status')
                elif message.get('type') == 'http.response.body':
                    response_body.extend(message.get('body', b''))
                await send(message)

            try:
                await self.app(scope, capture_receive, capture_send)
            except Exception:
                tb = traceback.format_exc()
                status = 500
                await send({"type":"http.response.start","status":500,"headers":[[b"content-type",b"text/plain"]]})
                await send({"type":"http.response.body","body": tb.encode('utf-8')})
            finally:
                duration = time.time() - start
                entry = {
                    'timestamp': time.time(),
                    'method': scope.get('method'),
                    'path': scope.get('path'),
                    'query_string': scope.get('query_string', b'').decode('utf-8') if scope.get('query_string') else '',
                    'headers': [(k.decode('latin1'), v.decode('latin1')) for k,v in scope.get('headers', [])],
                    'request_body': b''.join(body_chunks).decode('utf-8', errors='replace') if body_chunks else '',
                    'response_status': status,
                    'response_body': response_body.decode('utf-8', errors='replace') if response_body else '',
                    'duration': duration
                }
                fname = int(time.time()*1000)
                try:
                    p = self.logs_dir / f"{fname}.json"
                    p.write_text(json.dumps(entry, ensure_ascii=False))
                except Exception:
                    pass

        return asgi
