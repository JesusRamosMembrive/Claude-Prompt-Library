# SPDX-License-Identifier: MIT
"""
Descubrimiento del ecosistema de linters y reglas de calidad disponibles.
"""

from __future__ import annotations

import asyncio
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from importlib import metadata
from importlib.metadata import PackageNotFoundError
import platform
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ToolDefinition:
    """Definición básica de una herramienta de calidad estándar."""

    key: str
    name: str
    description: str
    command: Optional[str] = None
    package: Optional[str] = None
    homepage: Optional[str] = None


@dataclass(frozen=True)
class ToolStatus:
    """Estado detectado para una herramienta estándar."""

    key: str
    name: str
    description: str
    installed: bool
    version: Optional[str] = None
    command_path: Optional[str] = None
    homepage: Optional[str] = None
    error: Optional[str] = None


@dataclass(frozen=True)
class CustomRuleStatus:
    """Descripción de una regla personalizada implementada por el proyecto."""

    key: str
    name: str
    description: str
    enabled: bool = True
    threshold: Optional[int] = None
    configurable: bool = True


@dataclass(frozen=True)
class NotificationChannelStatus:
    """Canales disponibles para notificaciones locales."""

    key: str
    name: str
    available: bool
    description: Optional[str] = None
    command: Optional[str] = None


STANDARD_TOOLS: tuple[ToolDefinition, ...] = (
    ToolDefinition(
        key="ruff",
        name="Ruff",
        description="Linter y formateador ultrarápido para Python.",
        command="ruff",
        package="ruff",
        homepage="https://docs.astral.sh/ruff/",
    ),
    ToolDefinition(
        key="black",
        name="Black",
        description="Formateador de código Python sin configuración.",
        command="black",
        package="black",
        homepage="https://black.readthedocs.io/",
    ),
    ToolDefinition(
        key="mypy",
        name="mypy",
        description="Type checker estático para Python.",
        command="mypy",
        package="mypy",
        homepage="https://www.mypy-lang.org/",
    ),
    ToolDefinition(
        key="bandit",
        name="Bandit",
        description="Análisis de seguridad para código Python.",
        command="bandit",
        package="bandit",
        homepage="https://bandit.readthedocs.io/",
    ),
    ToolDefinition(
        key="pytest",
        name="pytest",
        description="Framework de testing para Python.",
        command="pytest",
        package="pytest",
        homepage="https://docs.pytest.org/",
    ),
    ToolDefinition(
        key="pytest_cov",
        name="pytest-cov",
        description="Plugin de pytest para medir cobertura.",
        package="pytest-cov",
        homepage="https://pytest-cov.readthedocs.io/",
    ),
    ToolDefinition(
        key="pre_commit",
        name="pre-commit",
        description="Framework de hooks para repositorios Git.",
        command="pre-commit",
        package="pre-commit",
        homepage="https://pre-commit.com/",
    ),
)

CUSTOM_RULES: tuple[CustomRuleStatus, ...] = (
    CustomRuleStatus(
        key="max_file_length",
        name="Longitud máxima de archivo",
        description="Recomienda refactorizar archivos que superen el umbral configurado.",
        threshold=500,
        configurable=True,
    ),
)


def _safe_get_version(package: str) -> tuple[Optional[str], Optional[str]]:
    """
    Obtiene la versión de un paquete sin propagar excepciones.

    Devuelve una tupla (version, error).
    """
    try:
        return metadata.version(package), None
    except PackageNotFoundError:
        return None, None
    except Exception as exc:  # pragma: no cover - errores inesperados
        return None, f"Error obteniendo versión de {package}: {exc}"


def _detect_tool(definition: ToolDefinition) -> ToolStatus:
    """
    Calcula el estado de instalación de una herramienta estándar.
    """
    command_path: Optional[str] = None
    error: Optional[str] = None
    installed = False

    if definition.command:
        command_path = shutil.which(definition.command)
        installed = command_path is not None

    version: Optional[str] = None
    if definition.package:
        version, version_error = _safe_get_version(definition.package)
        if version:
            installed = True
        if version_error:
            error = version_error

    return ToolStatus(
        key=definition.key,
        name=definition.name,
        description=definition.description,
        installed=installed,
        version=version,
        command_path=command_path,
        homepage=definition.homepage,
        error=error,
    )


def _detect_standard_tools() -> List[ToolStatus]:
    """Evalúa el estado de todas las herramientas estándar."""
    return [_detect_tool(definition) for definition in STANDARD_TOOLS]


def _detect_notifications() -> List[NotificationChannelStatus]:
    """
    Determina los canales de notificación disponibles dependiendo del SO.
    """
    system = platform.system().lower()
    candidates: List[NotificationChannelStatus] = []

    if system == "linux":
        path = shutil.which("notify-send")
        candidates.append(
            NotificationChannelStatus(
                key="notify_send",
                name="notify-send",
                available=bool(path),
                description="Notificaciones nativas en entornos Linux compatibles con libnotify.",
                command=path,
            )
        )
    elif system == "darwin":
        path = shutil.which("osascript")
        candidates.append(
            NotificationChannelStatus(
                key="osascript",
                name="osascript",
                available=bool(path),
                description="Notificaciones nativas mediante AppleScript (macOS).",
                command=path,
            )
        )
    elif system == "windows":
        # En Windows asumimos que se pueden usar ToastNotifications vía PowerShell.
        path = shutil.which("powershell")
        candidates.append(
            NotificationChannelStatus(
                key="powershell_toast",
                name="PowerShell Toast",
                available=bool(path),
                description="Notificaciones tipo toast a través de PowerShell.",
                command=path,
            )
        )
    return candidates


def _build_payload(root: Path) -> Dict[str, Any]:
    """Construye el payload base para la API."""
    tools = _detect_standard_tools()
    notifications = _detect_notifications()

    return {
        "root_path": str(root.resolve()),
        "generated_at": datetime.now(timezone.utc),
        "tools": [asdict(tool) for tool in tools],
        "custom_rules": [asdict(rule) for rule in CUSTOM_RULES],
        "notifications": [asdict(channel) for channel in notifications],
    }


async def discover_linters(root: Path) -> Dict[str, Any]:
    """
    Ejecuta el proceso de descubrimiento en un hilo separado para no bloquear el event loop.
    """
    return await asyncio.to_thread(_build_payload, root)
