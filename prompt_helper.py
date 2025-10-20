#!/usr/bin/env python3
"""
Prompt Helper - Navegador simple de la biblioteca de prompts
"""
import os
import sys
import argparse

# Intentar importar simple_term_menu, solo necesario para modo interactivo
try:
    from simple_term_menu import TerminalMenu
    INTERACTIVE_MODE_AVAILABLE = True
except ImportError:
    INTERACTIVE_MODE_AVAILABLE = False

# Intentar importar pyperclip, pero es opcional
try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False


def clear_screen():
    """Limpia la pantalla de la consola."""
    os.system('clear' if os.name != 'nt' else 'cls')


def parse_markdown_files(prompts_dir):
    """
    Parsea estructura de directorios con archivos individuales de prompts.

    Estructura esperada:
    prompts/
      debugging/
        stuck-in-loop.md
        error-oscuro.md
      refactoring/
        ...

    Retorna un diccionario:
    {
      "DEBUGGING": {
        "Stuck in Loop": "contenido del snippet...",
        "Error Oscuro": "contenido...",
      },
      ...
    }
    """
    from pathlib import Path

    library = {}
    prompts_path = Path(prompts_dir)

    if not prompts_path.exists():
        return library

    # Escanear directorios (categorías)
    for category_dir in sorted(prompts_path.iterdir()):
        if not category_dir.is_dir():
            continue

        category_name = category_dir.name.upper()
        library[category_name] = {}

        # Escanear archivos .md en cada categoría
        for prompt_file in sorted(category_dir.glob('*.md')):
            with open(prompt_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Extraer nombre del prompt (# Título)
            prompt_name = None
            for line in lines:
                if line.startswith('# '):
                    prompt_name = line.strip('#').strip()
                    break

            if not prompt_name:
                # Fallback: usar nombre del archivo
                prompt_name = prompt_file.stem.replace('-', ' ').title()

            # Extraer contenido del bloque ## Prompt
            content_lines = []
            in_prompt_section = False
            in_code_block = False

            for line in lines:
                # Detectar sección ## Prompt
                if line.startswith('## Prompt'):
                    in_prompt_section = True
                    continue

                # Salir si encontramos otra sección ##
                if in_prompt_section and line.startswith('## ') and not line.startswith('## Prompt'):
                    break

                # Procesar líneas dentro de la sección Prompt
                if in_prompt_section:
                    if line.strip().startswith('```'):
                        if not in_code_block:
                            in_code_block = True
                            continue  # Skip opening ```
                        else:
                            break  # End of code block
                    elif in_code_block:
                        content_lines.append(line.rstrip('\n'))

            if content_lines:
                library[category_name][prompt_name] = '\n'.join(content_lines).strip()

    return library


def parse_markdown(file_path):
    """
    Parsea el archivo PROMPT_LIBRARY.md y extrae categorías y snippets.
    (Mantenido para backwards compatibility)

    Retorna un diccionario:
    {
      "DEBUGGING": {
        "Stuck in Loop": "contenido del snippet...",
        "Error Oscuro": "contenido...",
      },
      ...
    }
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    library = {}
    current_category = None
    current_snippet_name = None
    in_code_block = False
    code_lines = []

    for line in lines:
        # Detectar categorías (## TITULO)
        if line.startswith('## ') and not line.startswith('###'):
            category_name = line.strip('#').strip()
            # Ignorar secciones que no son categorías de prompts
            if category_name not in ['NOTAS DE USO', 'EXPANSIÓN FUTURA (Phase 2)']:
                current_category = category_name
                library[current_category] = {}
            else:
                # Resetear todo cuando salimos de las secciones de prompts
                current_category = None
                current_snippet_name = None
                in_code_block = False
                code_lines = []

        # Detectar snippets (### Nombre)
        elif line.startswith('### ') and current_category:
            # Guardar snippet anterior si existe
            if current_snippet_name and code_lines and current_category:
                library[current_category][current_snippet_name] = '\n'.join(code_lines).strip()
                code_lines = []

            current_snippet_name = line.strip('#').strip()
            in_code_block = False

        # Detectar inicio/fin de bloque de código
        elif line.strip().startswith('```') and current_snippet_name and current_category:
            if not in_code_block:
                in_code_block = True
                code_lines = []  # Reiniciar para nuevo bloque
            else:
                # Fin del bloque
                in_code_block = False
                library[current_category][current_snippet_name] = '\n'.join(code_lines).strip()
                code_lines = []

        # Acumular líneas del snippet
        elif in_code_block and current_category:
            code_lines.append(line.rstrip('\n'))

    return library


def show_categories(library):
    """Muestra el menú de categorías y retorna la selección."""
    clear_screen()
    print("\n" + "="*60)
    print("  BIBLIOTECA DE PROMPTS")
    print("="*60)

    categories = list(library.keys())
    menu_items = [f"{cat} ({len(library[cat])} prompts)" for cat in categories]
    menu_items.append("[Salir]")

    terminal_menu = TerminalMenu(
        menu_items,
        title="Usa ↑/↓ para navegar, Enter para seleccionar:",
        menu_cursor="→ ",
        menu_cursor_style=("fg_cyan", "bold"),
        menu_highlight_style=("bg_cyan", "fg_black"),
    )

    choice = terminal_menu.show()

    if choice is None or choice == len(categories):
        return None

    return categories[choice]


def show_snippets(category, snippets):
    """Muestra el menú de snippets dentro de una categoría."""
    clear_screen()
    print("\n" + "="*60)
    print(f"  {category}")
    print("="*60)

    snippet_names = list(snippets.keys())
    menu_items = snippet_names.copy()
    menu_items.append("[← Volver]")

    terminal_menu = TerminalMenu(
        menu_items,
        title="Usa ↑/↓ para navegar, Enter para seleccionar:",
        menu_cursor="→ ",
        menu_cursor_style=("fg_cyan", "bold"),
        menu_highlight_style=("bg_cyan", "fg_black"),
    )

    choice = terminal_menu.show()

    if choice is None or choice == len(snippet_names):
        return 'back'

    return snippet_names[choice]


def normalize_text(text):
    """Normaliza texto para búsqueda flexible."""
    return text.lower().replace(' ', '-').replace('_', '-')


def find_snippet(library, path):
    """
    Busca un snippet por path (categoria/nombre).
    Permite matching parcial y flexible.
    Retorna (categoria, snippet_name, content) o (None, None, None).
    """
    parts = path.split('/', 1)
    if len(parts) != 2:
        return None, None, None

    category_query, snippet_query = parts
    category_query_norm = normalize_text(category_query)
    snippet_query_norm = normalize_text(snippet_query)

    # Buscar categoría
    matching_category = None
    for cat in library.keys():
        if category_query_norm in normalize_text(cat):
            matching_category = cat
            break

    if not matching_category:
        return None, None, None

    # Buscar snippet
    for snippet_name, content in library[matching_category].items():
        if snippet_query_norm in normalize_text(snippet_name):
            return matching_category, snippet_name, content

    return None, None, None


def list_prompts(library):
    """Lista todas las categorías y prompts."""
    for category in library:
        print(f"\n{category}:")
        for snippet_name in library[category]:
            path = f"{normalize_text(category)}/{normalize_text(snippet_name)}"
            print(f"  - {snippet_name}")
            print(f"    ({path})")


def show_prompt(library, path):
    """Muestra un prompt específico."""
    category, snippet_name, content = find_snippet(library, path)

    if not content:
        print(f"Error: No se encontró el prompt '{path}'")
        print("\nUsa 'python prompt_helper.py list' para ver todos los prompts disponibles")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  {category} / {snippet_name}")
    print(f"{'='*60}\n")
    print(content)
    print(f"\n{'='*60}")


def copy_prompt(library, path):
    """Copia un prompt al portapapeles."""
    category, snippet_name, content = find_snippet(library, path)

    if not content:
        print(f"Error: No se encontró el prompt '{path}'")
        print("\nUsa 'python prompt_helper.py list' para ver todos los prompts disponibles")
        sys.exit(1)

    if PYPERCLIP_AVAILABLE:
        try:
            pyperclip.copy(content)
            print(f"✓ Prompt '{category} / {snippet_name}' copiado al portapapeles")
        except Exception as e:
            print(f"⚠ Error al copiar: {e}")
            print("\nContenido del prompt:")
            print(content)
    else:
        print("⚠ pyperclip no está disponible. Mostrando contenido:")
        print(f"\n{'='*60}")
        print(content)
        print(f"{'='*60}")


def interactive_mode(library):
    """Modo interactivo con menú."""
    if not INTERACTIVE_MODE_AVAILABLE:
        print("Error: simple-term-menu no está instalado.")
        print("Instálalo con: pip install simple-term-menu")
        print("\nO usa el modo comando:")
        print("  python prompt_helper.py list")
        print("  python prompt_helper.py show <categoria>/<nombre>")
        print("  python prompt_helper.py copy <categoria>/<nombre>")
        sys.exit(1)

    # Loop principal
    while True:
        # Mostrar categorías
        category = show_categories(library)
        if category is None:
            clear_screen()
            print("\n¡Hasta luego!\n")
            break

        # Mostrar snippets de la categoría
        while True:
            snippet_name = show_snippets(category, library[category])

            if snippet_name is None:
                clear_screen()
                print("\n¡Hasta luego!\n")
                return

            if snippet_name == 'back':
                break  # Volver al menú de categorías

            # Mostrar snippet
            snippet_content = library[category][snippet_name]

            # Intentar copiar al portapapeles si está disponible
            if PYPERCLIP_AVAILABLE:
                try:
                    pyperclip.copy(snippet_content)
                    print("\n✓ Prompt copiado al portapapeles!")
                except Exception:
                    print("\n⚠ No se pudo copiar al portapapeles automáticamente")

            # Mostrar snippet completo
            print("\n" + "="*60)
            print(f"  {snippet_name}")
            print("="*60)
            print()
            print(snippet_content)
            print()
            print("="*60)

            if not PYPERCLIP_AVAILABLE:
                print("💡 Selecciona el texto con el mouse y copia con Ctrl+Shift+C")

            print("\nPresiona Enter para continuar...", end='')
            input()
            clear_screen()


def main():
    """Función principal."""
    # Parsear argumentos
    parser = argparse.ArgumentParser(
        description='Prompt Helper - Navegador de la biblioteca de prompts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s                              Modo interactivo
  %(prog)s list                         Lista todos los prompts
  %(prog)s show debugging/stuck         Muestra un prompt
  %(prog)s copy planning/feature        Copia un prompt al portapapeles
        """
    )

    parser.add_argument(
        'command',
        nargs='?',
        choices=['list', 'show', 'copy'],
        help='Comando a ejecutar (opcional, sin comando inicia modo interactivo)'
    )

    parser.add_argument(
        'path',
        nargs='?',
        help='Path del prompt en formato categoria/nombre (para show y copy)'
    )

    args = parser.parse_args()

    # Determinar ruta a los prompts
    script_dir = os.path.dirname(os.path.abspath(__file__))
    prompts_dir = os.path.join(script_dir, 'templates', 'docs', 'prompts')
    library_file = os.path.join(script_dir, 'templates', 'docs', 'PROMPT_LIBRARY.md')

    # Intentar cargar desde estructura de directorios primero (nueva estructura)
    library = None
    if os.path.exists(prompts_dir) and os.path.isdir(prompts_dir):
        library = parse_markdown_files(prompts_dir)

    # Fallback: cargar desde archivo único (backwards compatibility)
    if not library and os.path.exists(library_file):
        library = parse_markdown(library_file)

    if not library:
        print("Error: No se pudieron cargar los prompts.")
        print(f"Buscado en:")
        print(f"  - {prompts_dir} (estructura de directorios)")
        print(f"  - {library_file} (archivo único)")
        sys.exit(1)

    # Ejecutar según el comando
    if args.command is None:
        # Modo interactivo
        interactive_mode(library)
    elif args.command == 'list':
        list_prompts(library)
    elif args.command == 'show':
        if not args.path:
            print("Error: 'show' requiere especificar un path")
            print("Ejemplo: python prompt_helper.py show debugging/stuck")
            sys.exit(1)
        show_prompt(library, args.path)
    elif args.command == 'copy':
        if not args.path:
            print("Error: 'copy' requiere especificar un path")
            print("Ejemplo: python prompt_helper.py copy debugging/stuck")
            sys.exit(1)
        copy_prompt(library, args.path)


if __name__ == '__main__':
    main()
