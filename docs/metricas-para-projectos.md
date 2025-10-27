# Límites prácticos para funciones y scripts largos

A falta de “leyes” universales, lo que funciona es combinar principios de diseño con umbrales cuantitativos que puedas automatizar en tus linters y CI. Abajo tienes criterios claros, señales de alerta y un proceso de refactor paso a paso, con métricas y herramientas para Python (aplicables por analogía a C++ y JS/React).

---

## 1) Principios que gobiernan el tamaño

* **Responsabilidad única (SRP)**: una función debe hacer una cosa y hacerla bien; un módulo debe agrupar cosas que cambian por la misma razón.
* **Cohesión alta, acoplamiento bajo**: si para entender A tienes que leer B, probablemente A y B deberían vivir juntas; si una pieza se usa en muchos sitios, extrae una API estable.
* **Testabilidad**: cuanto más fácil de testear de forma aislada, mejor has dividido.

---

## 2) Umbrales recomendados para **funciones**

Usa estos límites para disparar refactors, no como dogmas. Si una función se pasa de varios a la vez, pártela.

| Métrica                                                    | Verde (ok) | Amarillo (revisar) | Rojo (refactor ya) |
| ---------------------------------------------------------- | ---------: | -----------------: | -----------------: |
| **Líneas de código (LOC)** (sin docstrings ni comentarios) |       ≤ 40 |              41–80 |               > 80 |
| **Complejidad ciclomática (CC)**                           |       ≤ 10 |              11–15 |               > 15 |
| **Profundidad de anidamiento** (ifs/loops/try)             |        ≤ 2 |                  3 |                ≥ 4 |
| **Nº de parámetros**                                       |        ≤ 4 |                5–6 |                > 6 |
| **Nº de puntos de retorno**                                |        ≤ 3 |                4–5 |                > 5 |

Notas:

* En C++ estas cifras suelen ser más estrictas (p. ej., LOC ≤ 60 como rojo suave), por coste de lectura/compilación.
* En React aplica a componentes: si un componente supera ~150 LOC o tiene más de 3 efectos/handlers densos, extrae hooks o subcomponentes.

**Señales claras de que debes partir una función**

* El nombre necesita “y”/“o” para describirla.
* Comentarios por bloques explicando “fase 1/2/3” dentro de la misma función.
* Más de dos niveles de anidamiento.
* Repite patrones (mismo bloque con pequeñas variaciones).
* Excesivo manejo de errores mezclado con la lógica de negocio.
* Demasiada E/S mezclada con cómputo puro.

**Técnicas de refactor útiles**

* *Extract Function / Split Phase*: separar “parsear → validar → transformar → ejecutar → reportar”.
* *Introduce Parameter Object*: agrupa 5–7 args en un objeto (o `dataclass`/`pydantic`).
* *Pipeline / Strategy / Command*: cuando hay múltiples “pasos” o variantes.
* *Guard Clauses*: returns tempranos para reducir anidamiento.

---

## 3) Umbrales recomendados para **scripts/módulos**

Piensa en tres tamaños: archivo, paquete y “aplicación” (con CLI/servicio).

| Métrica (por archivo .py/.cpp/.tsx)          | Verde | Amarillo |  Rojo |
| -------------------------------------------- | ----: | -------: | ----: |
| **LOC por archivo**                          | ≤ 300 |  301–600 | > 600 |
| **Nº de clases/funciones públicas**          |   ≤ 8 |     9–15 |  > 15 |
| **Imports que solo usa 1 parte del archivo** |   0–2 |      3–5 |   > 5 |

**Señales para dividir un script en varios módulos/paquetes**

* El archivo implementa **más de un “verbo”** (p. ej., entrenar, evaluar, desplegar) → usa subcomandos.
* Mezcla **infraestructura** (CLI, logging, wiring) con **dominio** (reglas de negocio).
* Hay código que te gustaría **reutilizar** en otros proyectos.
* Empiezan **ciclos de importación** o el tiempo de arranque sube.
* Los tests necesitan *fixtures* enormes para tocar una función.

**Regla práctica**

* A los **600–800 LOC** por archivo, planifica extracción.
* A los **>1000 LOC** o **>3 responsabilidades** claras, crea paquete: `src/paquete/...` con `__init__.py`, submódulos por capa.

---

## 4) Estructura recomendada para proyectos con **agentes de IA**

Separa orquestación, herramientas y configuración. Ejemplo de organización (sin código):

```
project/
  pyproject.toml
  src/
    app/                  # wiring / cli / entrypoints
      cli.py
      __main__.py
    agents/               # planners, policies, roles
      planner.py
      executor.py
    tools/                # “acciones” del agente (APIs, DB, FS)
      search.py
      files.py
    llm/
      client.py           # provider adapter
      retries.py
    prompts/
      templates/          # jinja/md/yaml; versionadas y testeables
      registry.py
    memory/
      vectorstore.py
      state.py
    config/
      settings.py         # pydantic/BaseSettings + .env
    evaluation/
      harness.py          # golden tests / offline eval
  tests/
    unit/
    integration/
```

Criterios:

* **Prompts como artefactos**: plantillas/versionado separados del código.
* **Herramientas** plug-and-play: cada tool en su módulo, registrada en un “tool registry”.
* **Cliente LLM** aislado detrás de una interfaz (fácil de *mockear*).
* **CLI** con subcomandos (p. ej., Typer): `run`, `eval`, `dump-state`, `repl`.

---

## 5) Proceso de refactor disciplinado

1. **Congela comportamiento con tests**: mínimos smoke tests y “golden tests” de prompts/respuestas críticas.
2. **Mide**: LOC, CC, anidamiento y tiempos de import.
3. **Ataca lo peor primero**: funciones con CC > 15 o archivos > 800 LOC.
4. **Divide por fases** (parse/validar/transformar/actuar) y mueve E/S a bordes.
5. **Introduce capas** (tools, llm, policy, orquestación) y contratos tipados.
6. **Limpia dependencias**: rompe ciclos, inyecta lo externo.
7. **Automatiza checks en CI** y bloquea regresiones.

---

## 6) Tooling y umbrales automatizables

* **Ruff** (o Flake8) con Mccabe: `C901` (complejidad).
  Objetivo: **CC ≤ 10** por función; fallo de CI en **> 15**.
* **Radon**: CC, mantenibilidad; **Xenon** para fallar builds:
  `--max-absolute B --max-modules A --max-average A` (ajusta a tu gusto).
* **Pylint**: fija `max-args=5`, `max-branches=12`, `max-returns=5`, `max-locals=15`.
* **mypy**: disciplina de tipos para reducir comentarios “explicativos”.
* **Pre-commit**: ruff + black + isort + mypy + radon/xenon.
* **Coverage**: exige cobertura mínima en módulos recién extraídos.

---

## 7) Documentación y comentarios

* **Docstring** clara para el *qué* y *contrato*; el *cómo* debe emerger del código.
* **Densidad de comentarios** objetivo: **10–20%** de las líneas; si necesitas más para explicar flujo, es señal de dividir.
* **README/ADR** para decisiones arquitectónicas de agentes (p. ej., por qué un planner jerárquico).

---

## 8) Criterios rápidos de decisión

* **Parte una función** si: LOC > 80 **o** CC > 15 **o** anidamiento ≥ 4 **o** > 6 parámetros **o** múltiples fases lógicas.
* **Parte un archivo** si: LOC > 600 **o** > 15 símbolos públicos **o** mezcla CLI/infra con dominio **o** surgen ciclos de import.
* **Crea paquete** si: el proyecto tiene ≥ 3 áreas (orquestación, tools, LLM, memoria) o el archivo principal se acerca a 1000 LOC.

---

## 9) Notas específicas para C++ y JS/React

* **C++**: refuerza límites (CC ≤ 10, LOC función ≤ 60–80), separa headers/impl, y evita archivos > ~500 LOC por compilación incremental y legibilidad.
* **React**: extrae **custom hooks** cuando un componente gestiona múltiples efectos/estados; componentes presentacionales pequeños, contenedores que orquestan. Si un hook supera ~150 LOC o combina 3+ preocupaciones, divídelo.

---

## 10) Próximo paso

Si quieres, comparte un árbol de tu repo (nombres de archivos y tamaños) o salidas de `radon`/`ruff` y te indico exactamente dónde y cómo partir, con un plan de refactor concreto. Cuando pidas ejemplos de código, los incluyo con tests y configuración de CI.
