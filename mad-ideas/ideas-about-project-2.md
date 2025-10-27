¡Sí, correcto! En tu **Guía Completa** ya fijaste como *canónicos* los tres archivos de reglas por etapa —`02-stage1-rules.md`, `02-stage2-rules.md`, `02-stage3-rules.md`— dentro de los templates `.claude/`. Esa es precisamente la sustitución práctica del antiguo `condensed_playbook_v2.md`. Además, tu **Quick Start** pide leer explícitamente esas reglas al inicio de cada sesión, y la **Comparativa de Etapas** las cita como referencia rápida para transiciones.   

A continuación te doy un **ejemplo completo** de cómo debería funcionar **stageguard** (MVP sólido, simple, y accionable):

---

## Qué es *stageguard*

Un **CLI** mínimo que convierte tu “estado de proyecto” en **reglas ejecutables**:

* `stageguard status` → diagnostica etapa recomendada + métricas + razones (lee tu código).
* `stageguard guard` → **frena** cambios que violen las reglas de la etapa actual (exit 1 si hay violaciones).
* `stageguard explain` → explica qué está permitido/prohibido en la etapa vigente y cuándo subir de etapa.

Se apoya en tu script actual (`assess_stage.py`) para métricas (ficheros, LOC, patrones, carpetas “arquitectónicas”) y señales de sub‑etapa (Early/Mid/Late). 

---

## Criterios que hace cumplir

Usa tus **Stage Assessment Criteria** como fuente de verdad (MVP):

* **Stage 1**: 1–3 archivos, **<500 LOC**, funciones (sin clases), **cero** patrones/capas.
* **Stage 2**: ≤20 archivos, <3000 LOC, ≤2 patrones, 2–3 capas **máx.** (Early/Mid/Late por nº de archivos/LOC).
* **Stage 3**: >20 archivos **o** >3000 LOC **o** >2 patrones (ya hay arquitectura más amplia). 

> Nota: *stageguard* **lee** la etapa a hacer cumplir desde `.claude/01-current-phase.md` (si existe) o permite override `--stage`. La distinción *Stage (técnico)* vs *Phase (roadmap de producto)* se mantiene clara (no mezclarlas).  

---

## UX del CLI (ejemplos)

### 1) Ver diagnóstico (lectura)

```bash
stageguard status .
```

**Salida (ejemplo):**

```
🎯 STAGE ASSESSMENT RESULTS
📊 Recommended Stage: 2
✅ Confidence: HIGH

📈 Project Metrics:
  - Code Files: 11
  - Lines of Code: ~1650
  - Directories: 7
  - Patterns Detected: Service Layer
  - Architecture: api, services, models

💡 Reasoning:
  • Medium codebase (11 files, ~1650 LOC)
  • Basic architecture present: 3 layer(s)
  • Some patterns in use: Service Layer
  • 📍 Mid Stage 2 - structure emerging

📖 Next Steps:
  1. Review .claude/02-stage2-rules.md
  2. Update .claude/01-current-phase.md with current stage
  3. Follow stage-appropriate practices
```

*(El formato deriva del propio `print_assessment` de tu script actual.)* 

---

### 2) Hacer cumplir reglas (bloquear sobre‑ingeniería)

```bash
# Usa la etapa declarada en .claude/01-current-phase.md
stageguard guard .

# O fuerza una etapa específica
stageguard guard . --stage 1 --strict
```

**Salida OK (Stage 1, repo pequeño):**

```
✅ Stage 1 guard passed.
Checked: files<=3, LOC<500, no classes, no patterns, no multi-layer folders.
```

**Salida con violaciones (Stage 1, repo se “infló”):**

```
❌ Stage 1 guard failed (3 violations):
  1) Files = 6 (>3). Stage 1 exige 1-3 archivos. [ref: STAGE_CRITERIA.md]
  2) Patterns detected: Service Layer. Stage 1 no permite patrones. [ref]
  3) Architectural folders present: services, models. Stage 1 no admite capas. [ref]
Tip: vuelve a funciones simples y unifica en 1-3 archivos.
Exit code: 1
```

*(Reglas y umbrales: ver “Stage Assessment Criteria”).* 

---

### 3) Explicar la etapa actual (educar al agente/equipo)

```bash
stageguard explain .
```

**Salida (ejemplo si estás en Stage 2):**

```
ETAPA ACTUAL: Stage 2 (Structuring)
Permitido:
  - 4–20 archivos, <3000 LOC, 2–3 capas
  - 0–2 patrones si hay dolor real (p.ej., Repository/Service)
Prohibido:
  - 4+ patrones
  - 4+ capas
  - Abstracciones "por si acaso"
Cuándo pasar a Stage 3:
  - >20 archivos, >3000 LOC, o patrones creciendo (3+), y uso real lo exige
Refs: 02-stage2-rules.md / STAGES_COMPARISON.md / STAGE_CRITERIA.md
```

 

---

## Integración recomendada

**Pre‑commit** (bloquea en local):

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: stageguard
        name: stageguard guard (enforce current stage)
        entry: stageguard guard .
        language: system
        pass_filenames: false
```

**CI (GitHub Actions) — falla el PR si viola reglas:**

```yaml
name: Stageguard
on: [pull_request]
jobs:
  guard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install .
      - run: stageguard status . | tee stage_status.md
      - run: stageguard guard .
```

**Comentario automático al PR** (usa el formato del “Stage Assessment Request” para dar feedback legible): 

---

## Esqueleto de implementación (MVP en Python)

> **Idea clave:** reutiliza tu `assess_stage.py` para métricas/diagnóstico y añade una capa delgada de “enforcement”.

```python
#!/usr/bin/env python3
# file: stageguard.py
import argparse, re, sys, json
from pathlib import Path
from assess_stage import assess_stage  # tu script actual (métricas + reasoning)  # :contentReference[oaicite:12]{index=12}

STAGE_LIMITS = {
    1: {"max_files": 3, "max_loc": 500, "max_patterns": 0, "max_layers": 0, "forbid_classes": True},  # :contentReference[oaicite:13]{index=13}
    2: {"max_files": 20, "max_loc": 3000, "max_patterns": 2, "max_layers": 3, "forbid_classes": False},  # :contentReference[oaicite:14]{index=14}
    3: {"max_patterns": 999, "max_layers": 999, "forbid_classes": False},  # Stage 3 raramente bloquea; se audita
}

def read_declared_stage(root: Path) -> int | None:
    phase = root / ".claude" / "01-current-phase.md"  # fuente del "estado vigente"  # :contentReference[oaicite:15]{index=15}
    if not phase.exists():
        return None
    text = phase.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"(ETAPA|Stage)\s*[:=]\s*(\d)", text, re.IGNORECASE)
    return int(m.group(2)) if m else None

def detect_classes(root: Path) -> bool:
    # Naive: busca "class " en archivos de código comunes
    exts = (".py",".js",".ts",".java",".go",".rb",".php")
    for p in root.rglob("*"):
        if p.suffix in exts and p.is_file():
            try:
                for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
                    if line.lstrip().startswith("class "):
                        return True
            except Exception:
                pass
    return False

def violations_for(stage: int, assessment: dict, strict: bool) -> list[str]:
    v, m = [], assessment["metrics"]
    limits = STAGE_LIMITS[stage]
    # Reglas duras por etapa (de STAGE_CRITERIA.md)
    if stage == 1:
        if m["file_count"] > limits["max_files"]:
            v.append(f"Files = {m['file_count']} (>3). Stage 1 exige 1–3 archivos.")
        if m["lines_of_code"] >= limits["max_loc"]:
            v.append(f"LOC = ~{m['lines_of_code']} (>=500). Stage 1 exige <500 LOC.")
        if m["patterns_found"]:
            v.append(f"Patterns detectados: {', '.join(m['patterns_found'])}. Stage 1 no permite patrones.")
        if m["architectural_folders"]:
            v.append(f"Carpetas arquitectónicas presentes: {', '.join(m['architectural_folders'])}. Stage 1 no admite capas.")
        if limits["forbid_classes"] and detect_classes(Path(".")):
            v.append("Encontradas clases. Stage 1 favorece funciones (sin clases).")
    elif stage == 2:
        if m["file_count"] > limits["max_files"]:
            v.append(f"Files = {m['file_count']} (>20). Stage 2 máximo 20.")
        if m["lines_of_code"] >= limits["max_loc"]:
            v.append(f"LOC = ~{m['lines_of_code']} (>=3000). Stage 2 máximo <3000.")
        if len(m["patterns_found"]) > limits["max_patterns"]:
            v.append(f"Patterns = {len(m['patterns_found'])} (>2). Stage 2 permite ≤2 patrones justificados.")
        if len(m["architectural_folders"]) > limits["max_layers"]:
            v.append(f"Capas ~{len(m['architectural_folders'])} (>3). Stage 2 permite 2–3 capas.")
    else:
        # En Stage 3, solo avisos (no bloquear salvo --strict)
        if len(m["architectural_folders"]) < 3 and strict:
            v.append("Stage 3 con pocas capas: revisa si realmente necesitas Stage 3.")
    return v

def cmd_status(path: Path, fmt: str):
    a = assess_stage(path)
    if not a:
        print("❌ No se pudo evaluar el proyecto"); sys.exit(2)
    if fmt == "json":
        print(json.dumps(a, indent=2, ensure_ascii=False)); return
    # Texto simple estilo print_assessment (resumen)
    print(f"Recommended Stage: {a['recommended_stage']}  | Confidence: {a['confidence'].upper()}")
    m = a["metrics"]
    print(f"Metrics: files={m['file_count']}  LOC≈{m['lines_of_code']}  dirs={m['directory_count']}")
    if m["patterns_found"]: print("Patterns:", ", ".join(m["patterns_found"]))
    if m["architectural_folders"]: print("Architecture:", ", ".join(m["architectural_folders"][:6]))
    print("Reasons:")
    for r in a["reasons"]: print(" -", r)

def cmd_guard(path: Path, stage: int | None, strict: bool):
    declared = read_declared_stage(path)
    enforced = stage or declared or assess_stage(path)["recommended_stage"]
    a = assess_stage(path)
    v = violations_for(enforced, a, strict)
    if v:
        print(f"❌ Stage {enforced} guard failed ({len(v)} violations):")
        for i, msg in enumerate(v, 1): print(f"  {i}) {msg} [ref: STAGE_CRITERIA.md]")
        sys.exit(1)
    print(f"✅ Stage {enforced} guard passed.")

def cmd_explain(enforced: int):
    if enforced == 1:
        print("Stage 1: 1–3 archivos, <500 LOC, funciones, sin patrones ni capas.")
    elif enforced == 2:
        print("Stage 2: 4–20 archivos, <3000 LOC, 2–3 capas, ≤2 patrones justificados.")
    else:
        print("Stage 3: arquitectura amplia; patrones/capas según necesidad y evidencia.")

def main():
    p = argparse.ArgumentParser(prog="stageguard")
    sub = p.add_subparsers(dest="cmd", required=True)
    s1 = sub.add_parser("status"); s1.add_argument("path", nargs="?", default="."); s1.add_argument("--format", choices=["txt","json"], default="txt")
    s2 = sub.add_parser("guard");  s2.add_argument("path", nargs="?", default="."); s2.add_argument("--stage", type=int); s2.add_argument("--strict", action="store_true")
    s3 = sub.add_parser("explain"); s3.add_argument("--stage", type=int, required=False)
    args = p.parse_args()
    root = Path(getattr(args, "path", ".")).resolve()
    if args.cmd == "status":  cmd_status(root, args.format)
    elif args.cmd == "guard": cmd_guard(root, args.stage, args.strict)
    elif args.cmd == "explain":
        st = args.stage or read_declared_stage(root) or 1
        cmd_explain(st)

if __name__ == "__main__":
    main()
```

**Por qué este MVP encaja contigo:**

* Reutiliza tu **motor actual** de métricas y razonamiento (`assess_stage.py`). 
* Hace cumplir **exactamente** los umbrales y señales que ya definiste (archivos, LOC, patrones, capas). 
* Expone una **salida legible** (el mismo estilo del “Assessment Request” que ya usas para comentar PRs). 
* Mantiene separadas *Stage (técnico)* y *Phase (roadmap)*, como estableciste. 

---

## Siguientes pasos (concretos)

1. Copiar el esqueleto de `stageguard.py` junto a `assess_stage.py` y probar `status/guard/explain` sobre tu repo. 
2. Añadir el hook de **pre-commit** y la **Action** de CI para frenar violaciones temprano.
3. (Iteración ligera) Mejorar detección de clases con **AST** y enriquecer la lista de “carpetas arquitectónicas”/patrones si lo necesitas.
4. Usar `stageguard explain` como **header auto‑inyectado** al inicio de cada conversación con el agente (consistente con tu Quick Start). 

Si quieres, te dejo en otro mensaje el **snippet de “header auto‑inyectado”** y el texto corto de **Stage Cards** para que el agente siempre arranque con las reglas vigentes (Stage 1/2/3) sin tener que volver a documentos largos.












