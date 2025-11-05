# SPDX-License-Identifier: MIT
"""
Shared AST utilities for code analysis.

This module provides common functionality for analyzing Python AST nodes,
particularly for import resolution and module path handling.
"""

from __future__ import annotations


class ImportResolver:
    """Shared logic for resolving Python imports in AST analysis."""

    @staticmethod
    def resolve_relative_import(
        current_module: str, relative_module: str, level: int
    ) -> str:
        """
        Resolve relative imports to absolute module paths.

        Args:
            current_module: The fully qualified name of the current module (e.g., "foo.bar.baz")
            relative_module: The module being imported (e.g., "utils" or "" for package imports)
            level: The number of dots in the relative import (e.g., 1 for ".", 2 for "..")

        Returns:
            The resolved absolute module path.

        Examples:
            >>> ImportResolver.resolve_relative_import("foo.bar.baz", "utils", 1)
            'foo.bar.utils'
            >>> ImportResolver.resolve_relative_import("foo.bar.baz", "", 2)
            'foo'
            >>> ImportResolver.resolve_relative_import("foo.bar.baz", "qux", 2)
            'foo.qux'
        """
        if not level:
            # Absolute import
            return relative_module

        parts = current_module.split(".")
        if level > len(parts):
            # Invalid relative import (too many levels up)
            return relative_module

        # Go up 'level' directories
        base = parts[:-level]

        # Append the relative module if provided
        if relative_module:
            base.append(relative_module)

        return ".".join(base)
