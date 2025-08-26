# Minimal ASGI example app (no external dependencies required)
async def app(scope, receive, send):
    assert scope['type'] == 'http'
    path = scope.get('path', '/')
    if scope.get('method') == 'GET' and path == '/':
        body = b'{"msg":"Hello from JetPort example"}'
        await send({"type":"http.response.start","status":200,"headers":[[b"content-type", b"application/json"]]})
        await send({"type":"http.response.body","body": body})
        return
    if scope.get('method') == 'POST' and path == '/webhook':
        # read body
        body = b''
        more_body = True
        while more_body:
            msg = await receive()
            if msg['type'] == 'http.request':
                body += msg.get('body', b'')
                more_body = msg.get('more_body', False)
            else:
                more_body = False
        await send({"type":"http.response.start","status":200,"headers":[[b"content-type", b"application/json"]]})
        await send({"type":"http.response.body","body": b'{"received":' + body + b'}'})
        return
    # default 404
    await send({"type":"http.response.start","status":404,"headers":[[b"content-type", b"text/plain"]]})
    await send({"type":"http.response.body","body": b"Not found"})
