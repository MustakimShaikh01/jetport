import json
from pathlib import Path
from jinja2 import Template

def create_inspector_app(base_dir: Path):
    logs_dir = base_dir / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)

    async def app(scope, receive, send):
        path = scope.get('path','/')
        if path in ('/','/index','/index.html'):
            html = _index_html()
            await send({'type':'http.response.start','status':200,'headers':[(b'content-type', b'text/html; charset=utf-8')]})
            await send({'type':'http.response.body','body': html.encode('utf-8')})
            return
        if path == '/logs':
            files = sorted(list(logs_dir.glob('*.json')), key=lambda p: p.stat().st_mtime, reverse=True)
            entries = []
            for f in files[:200]:
                try:
                    data = json.loads(f.read_text())
                    data['_file'] = f.name
                    entries.append(data)
                except Exception:
                    continue
            body = json.dumps(entries, ensure_ascii=False)
            await send({'type':'http.response.start','status':200,'headers':[(b'content-type', b'application/json')]})
            await send({'type':'http.response.body','body': body.encode('utf-8')})
            return
        if path.startswith('/log/'):
            name = path[len('/log/'):]
            p = logs_dir / name
            if p.exists():
                body = p.read_text()
                await send({'type':'http.response.start','status':200,'headers':[(b'content-type', b'application/json')]})
                await send({'type':'http.response.body','body': body.encode('utf-8')})
                return
            else:
                await send({'type':'http.response.start','status':404,'headers':[(b'content-type', b'text/plain')]})
                await send({'type':'http.response.body','body': b'Not found'})
                return
        await send({'type':'http.response.start','status':404,'headers':[(b'content-type', b'text/plain')]})
        await send({'type':'http.response.body','body': b'Not found'})

    return app

def _index_html():
    t = Template('''<!doctype html><html><head><meta charset="utf-8"/><title>JetPort Inspector</title><style>body{font-family:system-ui;padding:20px}pre{background:#f8f8f8;padding:8px;border-radius:6px}</style></head><body><h1>JetPort Inspector</h1><div id="list">Loading…</div><script>async function load(){let res = await fetch(window.location.pathname+'logs');let data = await res.json();let html='';for(let e of data){html += `<div><a href='${window.location.pathname}log/${e._file}' target='_blank'><strong>${e.method} ${e.path}</strong></a><div>${new Date(e.timestamp*1000).toLocaleString()} • ${e.response_status}</div><pre>${(e.request_body||'').slice(0,300)}</pre></div>`;}document.getElementById('list').innerHTML = html || '<p>No logs yet</p>';}load();</script></body></html>''')
    return t.render()
