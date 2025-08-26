````markdown
# JetPort

JetPort is a **blazing-fast local HTTP/WS development server** with built-in TLS, a request inspector, and request replay functionality.  
It's like Uvicorn — but designed specifically for debugging, testing, and running secure local environments.

---

## Features

- **Automatic TLS on localhost** — no more manual cert setup.
- **Request/response inspector** — view requests live in your browser.
- **Request replay** — resend captured requests for debugging or CI pipelines.
- **ASGI compatible** — works with FastAPI, Starlette, Django, or any ASGI app.
- **CLI ready** — `jetport run example_app:app` spins up your app instantly.
- **CI friendly** — can be used in pipelines for webhook testing (Stripe, GitHub, etc.).

---

## Installation

Clone the repo and install in editable mode:

```bash
git clone <your-repo-url> jetport
cd jetport
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install uvicorn typer cryptography httpx aiofiles jinja2
pip install -e .
````

---

## Running JetPort

Run any ASGI app with TLS enabled automatically:

```bash
jetport run example_app:app
```

* Server will run at: [https://127.0.0.1:8443/](https://127.0.0.1:8443/)
* Inspector available at: [https://127.0.0.1:8443/**jetport**/](https://127.0.0.1:8443/__jetport__/)

Since the certificate is self-signed, your browser will show a warning — click **Advanced → Proceed** to continue.

---

## Example App

The included `example_app.py` is a minimal ASGI app to test JetPort:

```python
async def app(scope, receive, send):
    assert scope['type'] == 'http'
    await send({
        'type': 'http.response.start',
        'status': 200,
        'headers': [(b'content-type', b'text/plain')],
    })
    await send({
        'type': 'http.response.body',
        'body': b'Hello from JetPort!',
    })
```

You can replace this with **FastAPI**, **Starlette**, or any ASGI framework.

---

## Running Tests

JetPort uses `unittest` for testing:

```bash
python -m unittest
```

Example test (`tests/test_sanity.py`):

```python
import unittest

class SanityTest(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(1 + 1, 2)

if __name__ == "__main__":
    unittest.main()
```

---

## Roadmap

* [ ] WebSocket request capture & replay
* [ ] React-based inspector UI with live updates
* [ ] Richer CI integration (Docker image + GitHub Actions)
* [ ] PyPI release

---
