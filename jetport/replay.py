import asyncio, json, time
from pathlib import Path
import httpx

async def replay_request_file(path: str, override_url: str = None, times: int = 1, delay: float = 0.0):
    p = Path(path)
    if not p.exists():
        print('file not found', path); return
    data = json.loads(p.read_text())
    target = override_url or ('http://localhost' + data.get('path','/'))
    headers = {k:v for k,v in data.get('headers', []) if isinstance(k,str)}
    method = data.get('method','POST')
    body = data.get('request_body','')
    async with httpx.AsyncClient(verify=False) as client:
        for i in range(times):
            print(f'Replay {i+1}/{times} -> {target} ({method})')
            resp = await client.request(method, target, headers=headers, content=body.encode('utf-8'))
            print('->', resp.status_code)
            if delay:
                await asyncio.sleep(delay)

def replay_request_file_sync(path, override_url=None, times=1, delay=0.0):
    asyncio.run(replay_request_file(path, override_url=override_url, times=times, delay=delay))
