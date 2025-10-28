# UI Design: Dark Minimalist Concept

## Principios clave
- **Enfoque en el contenido**: priorizar la lectura de archivos y símbolos, evitando adornos innecesarios.
- **Paleta oscura de alto contraste**: fondo gris antracita, paneles ligeramente diferenciados, tipografía clara.
- **Jerarquía visual clara**: tamaños y pesos de fuente para separar secciones (explorador, detalle, filtros).
- **Accesibilidad**: contraste mínimo AA (texto vs fondo > 4.5), tamaños de texto >= 14px, soportar navegación con teclado.
- **Reactividad**: adaptarse a pantallas medianas (>= 1280px) y manejar colapsado de paneles.

## Layout general
```
 ---------------------------------------------------------------------------------
| Header fijo (logo + selector de root + indicadores de estado)                   |
 ---------------------------------------------------------------------------------
| Sidebar izquierda      | Panel central (detalles)          | Panel derecho (extra)|
| - Árbol de carpetas    | - Título del archivo              | - Filtros/Symbol search|
| - Resumen de estado    | - Lista de clases/funciones       | - Historial de cambios |
|                        | - Docstrings (cuando existan)     | - Config rápida         |
 ---------------------------------------------------------------------------------
| Footer fino opcional con versión + link a docs                                 |
 ---------------------------------------------------------------------------------
```

- La **sidebar** ocupa ~26% de ancho, panel central 48%, panel derecho 26%. En pantallas pequeñas (< 1200px), el panel derecho se colapsa a un drawer accesible.
- El árbol de carpetas usa un componente de expansión con líneas guía sutiles y resalta el archivo seleccionado.
- El panel central muestra breadcrumb arriba, seguido por tarjetas de símbolos (clases con métodos anidados, funciones libres).
- El panel derecho alberga búsqueda global y filtros (por tipo: clase, método, función), resumen de eventos recientes y toggles (mostrar docstrings, auto-refresh).

## Paleta de colores
- Fondo global: `#11131a`
- Paneles: `#161923`, `#1d2130`
- Texto primario: `#f6f7fb`
- Texto secundario: `#a8b0c3`
- Acento principal: `#3b82f6` (azul eléctrico) para selección y botones primarios.
- Acento secundario: `#f97316` para alertas o indicadores de error.
- Bordes/divisores: `#22273a`
- Highlight para archivo seleccionado: degradado sutil `linear-gradient(90deg, #1f293d, #1a2140)`

## Tipografía y espaciado
- Fuente: `Inter` o `JetBrains Mono` para secciones de código; fallback `system-ui`.
- Tamaños:
  - Header: 18px semibold
  - Árbol carpeta: 14px regular, 13px para metadata
  - Panel detalle: 16px título, 14px cuerpo
- Espaciado base: 8px (múltiplos para márgenes y paddings).
- Iconografía simple (Feather o Lucide) con golpes de 1.5px, color secundario.

## Componentes clave

### 1. Header
- Logo minimal (`</>`), input de ruta raíz (typeahead con historial), botón de estado watcher (verde activo, gris inactivo, ámbar cuando reescaneando).
- Botón `Rescan` (icono refresco) y acceso a ajustes (modal).
- Indicador de cambios pendientes (badge).

### 2. Sidebar (Árbol)
- Búsqueda contextual por nombre de archivo (input inline).
- Cada nodo muestra icono (carpeta/archivo), nombre y, en tooltip, recuento de símbolos.
- Estados: collapsed/expanded, highlight al hover, marca persistente para archivo actual.
- Toolbar superior: toggle “solo archivos con símbolos”, filtros por tipo (clase/función).

### 3. Panel central (Detalle archivo)
- Breadcrumb (p.ej. `src › services › payments.py`).
- Header del archivo: nombre, última modificación (relativa: “hace 5 min”), badges si hay errores.
- Lista de símbolos:
  - Clases mostradas como bloques con título y metadata (número de métodos, docstring).
  - Métodos dentro con indentación y bullet; color secundario para async/static/classmethod (cuando se agregue).
  - Funciones libres como tarjetas en grid, mostrando docstring y línea.
- Código no se muestra; se centra en la estructura.
- Sección de errores: tarjetas rojo oscuro con mensaje y ubicación.

### 4. Panel derecho (Filtros y actividad)
- Búsqueda global de símbolos (`⌘K` / `Ctrl+K` abre modal).
- Filtros: checkboxes “Funciones”, “Clases”, “Métodos”; slider rápido para agrupar por carpeta.
- Historial de eventos (últimos 10): lista con icono (creado/modificado/eliminado), nombre y timestamp.
- Configuración rápida: toggles (auto-rescan, incluir docstrings, tema claro/dark).

### 5. Modal de búsqueda global
- Input central con autocompletado.
- Resultados listados con icono, nombre, ruta, tipo, docstring breve.
- Navegable con teclado (↑ ↓, Enter abre detalle).

## Estados y feedback
- **Cargando**: skeletons con barras horizontales en los paneles.
- **Sin resultados**: ilustración sutil + mensaje en gris claro.
- **Errores**: banner rojo suave en header si la API falla, con botón “Reintentar”.
- **Notificaciones**: toasts discreto en esquina inferior derecha, fondo `#1f2937`, border azul.

## Interacciones clave
- Click en carpeta/archivo actualiza panel central, panel derecho refleja símbolos filtrables.
- Doble click en archivo abre modal dentro de panel central con docstrings completos (futuro).
- Hover en símbolo resalta su ubicación en árbol (sincronización).
- Atajos (a documentar):
  - `Ctrl/Cmd+P`: ir a archivo por nombre.
  - `Ctrl/Cmd+Shift+F`: búsqueda global de símbolos.
  - `Ctrl/Cmd+R`: rescan manual.

## Responsividad
- Breakpoint 1280px: panel derecho se convierte en drawer.
- Breakpoint 1024px: sidebar colapsable (overlay), panel central ocupa todo.
- Breakpoint 768px: layout vertical (header > filtros > detalles > árbol en tabs).

## Roadmap visual
1. Implementar layout base con CSS grid/flex.
2. Añadir componente de árbol con lazy loading (si es necesario).
3. Integrar panel central con datos mockeados.
4. Conectar SSE para indicadores de cambios.
5. Afinar micro-interacciones (transiciones 150ms, easing `cubic-bezier(0.4, 0, 0.2, 1)`).

Este diseño sienta las bases para implementar la UI en React/Vite manteniendo coherencia con el backend y dando prioridad a la legibilidad en un entorno oscuro y minimalista.
