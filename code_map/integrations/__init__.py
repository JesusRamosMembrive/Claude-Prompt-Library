# SPDX-License-Identifier: MIT
"""
Integraciones con herramientas externas.
"""

from __future__ import annotations

from .ollama_service import (
    OllamaChatError,
    OllamaChatMessage,
    OllamaChatResponse,
    OllamaDiscovery,
    OllamaModelInfo,
    OllamaStartError,
    OllamaStartResult,
    OllamaStatus,
    chat_with_ollama,
    discover_ollama,
    start_ollama_server,
)

__all__ = [
    "chat_with_ollama",
    "discover_ollama",
    "start_ollama_server",
    "OllamaChatResponse",
    "OllamaChatMessage",
    "OllamaChatError",
    "OllamaModelInfo",
    "OllamaStatus",
    "OllamaDiscovery",
    "OllamaStartResult",
    "OllamaStartError",
]
