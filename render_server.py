import hmac
import os

import uvicorn
from gsc_server import mcp


class BearerAuthMiddleware:
    """Protect the remote MCP endpoint with a bearer token."""

    def __init__(self, app, token):
        self.app = app
        self.expected = f"Bearer {token}".encode("utf-8")

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        supplied = headers.get(b"authorization", b"")

        if not hmac.compare_digest(supplied, self.expected):
            body = b'{"error":"Unauthorized"}'
            await send({
                "type": "http.response.start",
                "status": 401,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode()),
                    (b"www-authenticate", b"Bearer"),
                    (b"cache-control", b"no-store"),
                ],
            })
            await send({
                "type": "http.response.body",
                "body": body,
            })
            return

        await self.app(scope, receive, send)


def main():
    token = os.environ.get("MCP_AUTH_TOKEN", "")

    if len(token) < 32:
        raise RuntimeError(
            "MCP_AUTH_TOKEN must contain at least 32 characters."
        )

    port = int(os.environ.get("PORT", "10000"))

    try:
        mcp.settings.transport_security.enable_dns_rebinding_protection = False
    except Exception:
        pass

    app = BearerAuthMiddleware(
    mcp.streamable_http_app(host="0.0.0.0"),
    token,
)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
    )


if __name__ == "__main__":
    main()