# SPDX-License-Identifier: MIT
"""
Import Resolution - Stage 2

Resuelve imports de Python para permitir análisis cross-file.
Maneja:
- import module
- from module import function
- from .relative import function
- from ..parent import function
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ImportResolver:
    """
    Resuelve imports de Python para análisis cross-file.

    Example:
        >>> resolver = ImportResolver(project_root=Path("/project"))
        >>> imports = resolver.extract_imports("module.py")
        >>> resolved = resolver.resolve_import("from utils import helper", "module.py")
        >>> print(resolved)  # Path("/project/utils.py"), "helper"
    """

    def __init__(self, project_root: Path):
        """
        Inicializa el resolver con el directorio raíz del proyecto.

        Args:
            project_root: Ruta al directorio raíz del proyecto
        """
        self.project_root = project_root.resolve()
        self._import_cache: Dict[str, List[Tuple[str, Optional[str], Path]]] = {}

    def extract_imports(
        self, filepath: str | Path
    ) -> List[Tuple[str, Optional[str], str]]:
        """
        Extrae todos los imports de un archivo Python.

        Args:
            filepath: Ruta al archivo Python

        Returns:
            Lista de tuplas (module, name, import_type):
            - ("utils", None, "import") para `import utils`
            - ("utils", "helper", "from") para `from utils import helper`
            - (".", "helper", "from") para `from . import helper`

        Example:
            >>> resolver.extract_imports("my_module.py")
            [("os", None, "import"),
             ("pathlib", "Path", "from"),
             (".utils", "helper", "from")]
        """
        path = Path(filepath)

        if not path.exists():
            return []

        try:
            with open(path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(path))
        except (SyntaxError, UnicodeDecodeError):
            return []

        imports: List[Tuple[str, Optional[str], str]] = []

        for node in ast.walk(tree):
            # import module
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append((alias.name, None, "import"))

            # from module import name
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""  # puede ser None para `from . import`
                level = node.level  # 0 = absoluto, 1 = ., 2 = .., etc.

                # Construir nombre de módulo con dots relativos
                if level > 0:
                    module = "." * level + module

                for alias in node.names:
                    imports.append((module, alias.name, "from"))

        return imports

    def resolve_import(
        self, module: str, name: Optional[str], source_file: Path
    ) -> Optional[Tuple[Path, Optional[str]]]:
        """
        Resuelve un import a su archivo real y nombre de símbolo.

        Args:
            module: Nombre del módulo ("utils", ".helpers", "..parent")
            name: Nombre específico importado (None si es `import module`)
            source_file: Archivo desde donde se hace el import

        Returns:
            Tupla (archivo_resuelto, nombre_simbolo) o None si no se puede resolver

        Example:
            >>> resolver.resolve_import("utils", "helper", Path("src/module.py"))
            (Path("src/utils.py"), "helper")

            >>> resolver.resolve_import(".helpers", "func", Path("src/module.py"))
            (Path("src/helpers.py"), "func")
        """
        source_file = source_file.resolve()
        source_dir = source_file.parent

        # Imports absolutos (sin dots)
        if not module.startswith("."):
            return self._resolve_absolute(module, name, source_dir)

        # Imports relativos (con dots)
        return self._resolve_relative(module, name, source_dir)

    def _resolve_absolute(
        self, module: str, name: Optional[str], source_dir: Optional[Path] = None
    ) -> Optional[Tuple[Path, Optional[str]]]:
        """
        Resuelve import absoluto.

        Example:
            import utils → utils.py
            from utils import helper → utils.py, helper
            from utils.helpers import func → utils/helpers.py, func
        """
        # Convertir nombre de módulo a path
        # utils.helpers → utils/helpers.py
        module_path = Path(module.replace(".", "/"))

        # Primero, intentar relativo al directorio del archivo fuente
        # Esto maneja imports entre archivos del mismo directorio sin ser relativos
        if source_dir:
            candidate_file = source_dir / f"{module_path}.py"
            if candidate_file.exists():
                return (candidate_file, name)

            candidate_package = source_dir / module_path / "__init__.py"
            if candidate_package.exists():
                return (candidate_package, name)

        # Luego, intentar desde la raíz del proyecto
        candidate_file = self.project_root / f"{module_path}.py"
        if candidate_file.exists():
            return (candidate_file, name)

        # Intentar como paquete (directorio con __init__.py)
        candidate_package = self.project_root / module_path / "__init__.py"
        if candidate_package.exists():
            return (candidate_package, name)

        # No se pudo resolver (probablemente módulo externo)
        return None

    def _resolve_relative(
        self, module: str, name: Optional[str], source_dir: Path
    ) -> Optional[Tuple[Path, Optional[str]]]:
        """
        Resuelve import relativo.

        Example:
            from . import helper → ./helper.py
            from .utils import func → ./utils.py, func
            from ..parent import x → ../parent.py, x
        """
        # Contar niveles de dots
        level = 0
        while module.startswith("."):
            level += 1
            module = module[1:]

        # Subir tantos niveles como dots
        target_dir = source_dir
        for _ in range(level):
            target_dir = target_dir.parent
            if not target_dir.is_relative_to(self.project_root):
                # Nos salimos del proyecto
                return None

        # Si no hay más módulo, es `from . import name`
        if not module:
            if name:
                # from . import helper → ./helper.py
                candidate = target_dir / f"{name}.py"
                if candidate.exists():
                    return (candidate, name)

                # O puede ser submódulo
                candidate_init = target_dir / name / "__init__.py"
                if candidate_init.exists():
                    return (candidate_init, None)
            return None

        # from .module import name → ./module.py, name
        module_path = Path(module.replace(".", "/"))

        candidate_file = target_dir / f"{module_path}.py"
        if candidate_file.exists():
            return (candidate_file, name)

        candidate_package = target_dir / module_path / "__init__.py"
        if candidate_package.exists():
            return (candidate_package, name)

        return None

    def build_import_map(self, filepath: Path) -> Dict[str, Tuple[Path, Optional[str]]]:
        """
        Construye un mapa de todos los imports del archivo a sus resoluciones.

        Args:
            filepath: Archivo a analizar

        Returns:
            Dict de {nombre_local: (archivo_real, nombre_en_archivo)}

        Example:
            >>> resolver.build_import_map(Path("src/module.py"))
            {
                "helper": (Path("src/utils.py"), "helper"),
                "Path": (Path("pathlib.py"), "Path"),  # externo
                "utils": (Path("src/utils.py"), None)
            }
        """
        imports = self.extract_imports(filepath)
        import_map = {}

        for module, name, import_type in imports:
            resolved = self.resolve_import(module, name, filepath)

            if resolved:
                target_file, symbol = resolved

                # Determinar nombre local
                if import_type == "import":
                    # import utils → local name = "utils"
                    local_name = module.split(".")[-1]
                else:
                    # from utils import helper → local name = "helper"
                    local_name = name if name else module.split(".")[-1]

                import_map[local_name] = (target_file, symbol)

        return import_map

    def get_all_python_files(self) -> List[Path]:
        """
        Obtiene todos los archivos Python del proyecto.

        Returns:
            Lista de paths a archivos .py
        """
        return list(self.project_root.rglob("*.py"))
