#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_all_checks.py
Ejecuta lint/format/type-check/complexidad y tests para el repo actual.
Uso:
  python run_all_checks.py         # solo chequeos
  python run_all_checks.py --fix   # aplica formateo automático si procede
"""
import argparse
import os
import sys
import shlex
import shutil
import subprocess
from pathlib import Path
import importlib.util as _iu

ROOT = Path.cwd()

def module_available(name: str) -> bool:
    return _iu.find_spec(name) is not None

def exe_available(name: str) -> bool:
    return shutil.which(name) is not None

def run(cmd: list[str], *, cwd: Path | None = None) -> int:
    print("$", " ".join(shlex.quote(x) for x in cmd), flush=True)
    try:
        proc = subprocess.run(cmd, cwd=cwd or ROOT)
        return proc.returncode
    except FileNotFoundError:
        # Ejecutable no encontrado: tratamos como paso omitido
        return 127

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true",
                    help="Aplica formateo automático (Black/isort/Ruff --fix) antes de los tests")
    args = ap.parse_args()

    steps: list[tuple[str, list[str]]] = []

    # ----- Calidad de código (opcional según disponibilidad) -----
    if exe_available("ruff") or module_available("ruff"):
        cmd = ["ruff", "check", "."]
        if args.fix:
            cmd.append("--fix")
        steps.append(("Ruff", cmd))

    if exe_available("black") or module_available("black"):
        cmd = ["black", "." if args.fix else "--check", "."]
        # Nota: si usas Ruff como formateador, puedes desinstalar Black para omitirlo
        steps.append(("Black", cmd if args.fix else ["black", "--check", "."]))

    if exe_available("isort") or module_available("isort"):
        steps.append(("isort", ["isort", "." if args.fix else "--check-only", "."] if args.fix
                     else ["isort", "--check-only", "."]))

    if exe_available("mypy") or module_available("mypy"):
        steps.append(("mypy", ["mypy", "--pretty"]))

    if exe_available("xenon") or module_available("xenon"):
        # Umbrales razonables; ajusta según tu política
        steps.append(("xenon", ["xenon", "--max-absolute", "B", "--max-modules", "A", "--max-average", "A", "."]))
    elif exe_available("radon") or module_available("radon"):
        # Complejidad ciclomática: peor que B falla
        steps.append(("radon-cc", ["radon", "cc", "-s", "-n", "B", "."]))

    # ----- Pruebas -----
    tox_ini = (ROOT / "tox.ini").exists()
    nox_file = (ROOT / "noxfile.py").exists()

    if tox_ini and (exe_available("tox") or module_available("tox")):
        steps.append(("tox", ["tox", "-q"]))
    elif nox_file and (exe_available("nox") or module_available("nox")):
        # Si no defines sesión 'tests', nox ejecutará las que haya
        steps.append(("nox", ["nox", "-q"]))
    elif module_available("pytest") or exe_available("pytest"):
        cmd = ["pytest", "-q"]
        if module_available("pytest_cov"):
            cmd += ["--maxfail=1", "--disable-warnings", "--cov=.", "--cov-report=term-missing"]
        steps.append(("pytest", cmd))
    else:
        # Fallback estándar de la librería
        steps.append(("unittest", [sys.executable, "-m", "unittest", "discover", "-v"]))

    print(f"Repositorio: {ROOT}")
    failed: list[str] = []
    skipped: list[str] = []

    for name, cmd in steps:
        print("\n=== {} ===".format(name))
        code = run(cmd)
        if code == 127:
            print(f"(omitido) {name}: herramienta no instalada")
            skipped.append(name)
            continue
        if code != 0:
            print(f"(fallo) {name} terminó con código {code}")
            failed.append(name)

    print("\nResumen:")
    if skipped:
        print("  Omitidos:", ", ".join(skipped))
    if failed:
        print("  Fallos  :", ", ".join(failed))
        return 1
    print("  OK: todos los pasos ejecutados pasaron")
    return 0

if __name__ == "__main__":
    sys.exit(main())
