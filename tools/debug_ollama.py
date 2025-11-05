# SPDX-License-Identifier: MIT
"""
Herramienta de depuración para comprobar la conectividad con Ollama.

Uso:
    python tools/debug_ollama.py --endpoint http://127.0.0.1:11434 --model gpt-oss:latest
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
import time
from dataclasses import dataclass
from urllib import error as urlerror
from urllib import request as urlrequest
from urllib.parse import urlparse

DEFAULT_ENDPOINT = "http://127.0.0.1:11434"


@dataclass(frozen=True)
class HttpResponse:
    status: str
    body: str
    latency_ms: float


def build_request(
    method: str, url: str, data: dict | None = None
) -> urlrequest.Request:
    payload = json.dumps(data).encode("utf-8") if data is not None else None
    headers = {"Content-Type": "application/json"}
    return urlrequest.Request(
        url=url, data=payload, headers=headers, method=method.upper()
    )


def perform_request(req: urlrequest.Request, timeout: float) -> HttpResponse:
    start = time.perf_counter()
    try:
        with urlrequest.urlopen(req, timeout=timeout) as response:
            body = response.read().decode(
                response.headers.get_content_charset() or "utf-8"
            )
            return HttpResponse(
                status=str(response.status),
                body=body,
                latency_ms=(time.perf_counter() - start) * 1000,
            )
    except urlerror.HTTPError as exc:
        try:
            detail = exc.read().decode("utf-8", errors="replace")
        except Exception:
            detail = exc.reason if isinstance(exc.reason, str) else repr(exc.reason)
        return HttpResponse(
            status=f"HTTP {exc.code}",
            body=detail,
            latency_ms=(time.perf_counter() - start) * 1000,
        )
    except socket.timeout:
        return HttpResponse(
            status="timeout",
            body="Tiempo de espera agotado.",
            latency_ms=(time.perf_counter() - start) * 1000,
        )
    except Exception as exc:
        return HttpResponse(
            status="error",
            body=str(exc),
            latency_ms=(time.perf_counter() - start) * 1000,
        )


def check_tcp(host: str, port: int, timeout: float) -> tuple[bool, str]:
    start = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, f"{(time.perf_counter() - start) * 1000:.0f} ms"
    except Exception as exc:  # pragma: no cover - diagnóstico directo
        return False, str(exc)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Depuración de conectividad contra Ollama."
    )
    parser.add_argument(
        "--endpoint",
        default=DEFAULT_ENDPOINT,
        help="Endpoint base de Ollama (por defecto %(default)s)",
    )
    parser.add_argument(
        "--model",
        default="gpt-oss:latest",
        help="Modelo a utilizar para la llamada de prueba.",
    )
    parser.add_argument(
        "--prompt",
        default="Di 'pong' si recibiste este mensaje.",
        help="Prompt que se enviará al modelo.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Tiempo máximo de espera en segundos.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    endpoint = args.endpoint.rstrip("/")

    print(f"📡 Endpoint objetivo: {endpoint}")

    parsed = urlparse(endpoint)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 11434

    ok, tcp_info = check_tcp(host, port, timeout=min(args.timeout, 5.0))
    if not ok:
        print(f"❌ No se pudo abrir conexión TCP con {host}:{port} -> {tcp_info}")
        return 1
    print(f"✅ Puerto accesible ({host}:{port}) en {tcp_info}")

    tags_request = build_request("GET", f"{endpoint}/api/tags")
    tags_response = perform_request(tags_request, timeout=args.timeout)
    print(
        f"\n📦 /api/tags · estado={tags_response.status} · latencia={tags_response.latency_ms:.0f} ms"
    )
    try:
        tags_json = json.loads(tags_response.body)
        print(json.dumps(tags_json, ensure_ascii=False, indent=2))
    except json.JSONDecodeError:
        print(tags_response.body or "(respuesta vacía)")

    chat_request = build_request(
        "POST",
        f"{endpoint}/api/chat",
        data={
            "model": args.model,
            "messages": [
                {"role": "user", "content": args.prompt},
            ],
            "stream": False,
        },
    )
    chat_response = perform_request(chat_request, timeout=args.timeout)
    print(
        f"\n💬 /api/chat · estado={chat_response.status} · latencia={chat_response.latency_ms:.0f} ms"
    )
    try:
        chat_json = json.loads(chat_response.body)
        print(json.dumps(chat_json, ensure_ascii=False, indent=2))
    except json.JSONDecodeError:
        print(chat_response.body or "(respuesta vacía)")

    return (
        0
        if chat_response.status.isdigit() and chat_response.status.startswith("2")
        else 2
    )


if __name__ == "__main__":  # pragma: no cover - script CLI
    sys.exit(main())
