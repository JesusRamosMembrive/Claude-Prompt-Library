# SPDX-License-Identifier: MIT
"""
Utilidad de línea de comandos para probar el endpoint
`/integrations/ollama/test` sin necesidad de usar la UI.

Ejemplo:
    python tools/test_backend_ollama.py \
        --api http://127.0.0.1:8000 \
        --model gpt-oss:latest \
        --prompt "Ping de prueba"
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from urllib import request as urlrequest
from urllib import error as urlerror

DEFAULT_API_BASE = "http://127.0.0.1:8000"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Lanza un ping contra el endpoint /integrations/ollama/test del backend."
    )
    parser.add_argument(
        "--api",
        default=DEFAULT_API_BASE,
        help="URL base del backend (por defecto %(default)s)",
    )
    parser.add_argument(
        "--model",
        required=True,
        help="Nombre del modelo que quieres probar (ej. 'gpt-oss:latest').",
    )
    parser.add_argument(
        "--prompt",
        default="Di 'pong' si recibiste este mensaje.",
        help="Mensaje que se enviará al modelo.",
    )
    parser.add_argument(
        "--system-prompt",
        default=None,
        help="System prompt opcional a enviar junto al mensaje de usuario.",
    )
    parser.add_argument(
        "--endpoint",
        default=None,
        help="Endpoint alternativo de Ollama (si se deja vacío, el backend usa el detectado).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="Tiempo máximo de espera en segundos (vacío usa el valor por defecto del backend).",
    )
    return parser.parse_args()


def run() -> int:
    args = parse_args()
    api_base = args.api.rstrip("/")
    url = f"{api_base}/integrations/ollama/test"

    payload: dict[str, object] = {
        "model": args.model,
        "prompt": args.prompt,
    }
    if args.system_prompt:
        payload["system_prompt"] = args.system_prompt
    if args.endpoint:
        payload["endpoint"] = args.endpoint
    if args.timeout:
        payload["timeout_seconds"] = args.timeout

    data = json.dumps(payload).encode("utf-8")
    req = urlrequest.Request(
        url=url,
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )

    print(f"POST {url}")
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    start = time.perf_counter()
    try:
        with urlrequest.urlopen(req, timeout=120) as response:
            body = response.read().decode(response.headers.get_content_charset() or "utf-8")
            latency_ms = (time.perf_counter() - start) * 1000
            print(f"\n✅ Respuesta {response.status} en {latency_ms:.0f} ms")
            try:
                parsed = json.loads(body)
            except json.JSONDecodeError:
                print(body or "(sin cuerpo)")
                return 0

            print(json.dumps(parsed, ensure_ascii=False, indent=2))
            return 0

    except urlerror.HTTPError as exc:
        latency_ms = (time.perf_counter() - start) * 1000
        detail_text = exc.read().decode("utf-8", errors="replace")
        print(f"\n⚠️  Respuesta HTTP {exc.code} en {latency_ms:.0f} ms")
        try:
            detail = json.loads(detail_text)
            print(json.dumps(detail, ensure_ascii=False, indent=2))
        except json.JSONDecodeError:
            print(detail_text or "(sin detalle)")
        return 2
    except urlerror.URLError as exc:
        print(f"\n❌ Error de transporte: {exc.reason}")
        return 3


if __name__ == "__main__":  # pragma: no cover - utilidad CLI
    sys.exit(run())
