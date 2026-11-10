"""Kaggle shim for Folivox Web Studio (folivox ui).

Why this exists
---------------
`folivox ui` is designed for a *local* PC:

* binds to 127.0.0.1:8765
* refuses non-loopback Host / Origin headers (DNS-rebinding guard)
* auto-opens a desktop browser

On Kaggle none of that works: the kernel runs in a container and your
browser is elsewhere. The notebook therefore:

1. starts uvicorn on 0.0.0.0:8765 in a background thread,
2. exposes it with a tunnel (cloudflared),
3. wraps the Starlette app so the loopback guard sees "127.0.0.1"
   while the real tunnel Host is preserved for routing.

Security: the ?token= check is NOT disabled. Anyone opening the tunnel
URL still needs the token printed by the notebook. Do not share that URL.
Stop the notebook / tunnel when done.

Usage inside Kaggle (see kaggle_folivox.ipynb Cell 6):

    import kaggle_patch
    info = kaggle_patch.launch(port=8765)
    print(info["local_url"], info["token"])
    # then start cloudflared in another cell and open <tunnel_url>/?token=<token>
"""

from __future__ import annotations

import threading
from pathlib import Path


def get_token() -> str:
    """Reuse the same persistent token folivox ui uses."""
    from folivox.ui import ui_token

    return ui_token()


def _normalise_scope_for_guard(scope: dict) -> None:
    """Rewrite Host/Origin seen by the inner app to loopback.

    The tunnel (e.g. https://xyz.trycloudflare.com) forwards with
    Host: xyz.trycloudflare.com which folivox's rebinding guard would
    reject. We spoof only what the *inner* app sees so its check passes.
    Token auth still runs on the query string / cookie, untouched.
    """
    try:
        headers = scope.get("headers")
        if not headers:
            return
        new_headers = []
        for k, v in headers:
            lk = k.lower()
            if lk == b"host":
                new_headers.append((k, b"127.0.0.1:8765"))
            elif lk in (b"origin", b"referer"):
                # point origin back at loopback so an Origin check passes;
                # the browser still sends the real token cookie / query.
                try:
                    from urllib.parse import urlparse, urlunparse

                    u = urlparse(v.decode("latin-1"))
                    u = u._replace(netloc="127.0.0.1:8765")
                    new_headers.append((k, urlunparse(u).encode("latin-1")))
                except Exception:
                    new_headers.append((k, v))
            else:
                new_headers.append((k, v))
        scope["headers"] = new_headers
        # Some guards also check scope["server"]; normalise it too.
        if scope.get("type") in ("http", "websocket"):
            scope["server"] = ("127.0.0.1", scope.get("server", (None, None))[1] or 8765)
            scope["client"] = scope.get("client") or ("127.0.0.1", 0)
    except Exception:
        pass


def create_kaggle_app(token: str, port: int = 8765):
    """Call original create_app() then wrap with guard-normalising middleware."""
    from folivox.ui.app import create_app

    inner = create_app(token=token, port=port)

    async def kaggle_guard_wrapper(scope, receive, send):
        if scope["type"] in ("http", "websocket"):
            _normalise_scope_for_guard(scope)
        await inner(scope, receive, send)

    return kaggle_guard_wrapper


def launch(port: int = 8765, log_level: str = "warning") -> dict:
    """Start the Studio server in a background thread on 0.0.0.0.

    Returns {"port","token","local_url","thread"}.
    Open it via a tunnel: <tunnel_url>/?token=<token>
    """
    import uvicorn

    token = get_token()
    app = create_kaggle_app(token=token, port=port)

    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=port,
        log_level=log_level,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True, name="folivox-kaggle-ui")
    thread.start()
    return {
        "port": port,
        "token": token,
        "local_url": f"http://127.0.0.1:{port}/?token={token}",
        "thread": thread,
        "server": server,
    }


if __name__ == "__main__":
    info = launch()
    print("Folivox Kaggle Studio (patched) running on 0.0.0.0:%s" % info["port"])
    print("Local URL (inside kernel only):", info["local_url"])
    print("Via tunnel open: <your-tunnel-url>/?token=%s" % info["token"])
    info["thread"].join()
