"""Контроль правила «без логіки в тестах» (docs/test-guidelines.md).

Падає, якщо тестова функція в tests/ містить цикли, розгалуження, comprehension, lambda,
арифметику, f-рядки або try/except. Фікстурам (conftest.py) і хелперам у framework/ логіка
дозволена. Запуск: ``python scripts/check_test_style.py``.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

FORBIDDEN = {
    ast.For: "цикл",
    ast.While: "цикл",
    ast.If: "if",
    ast.IfExp: "inline if",
    ast.Try: "try/except",
    ast.ListComp: "comprehension",
    ast.SetComp: "comprehension",
    ast.DictComp: "comprehension",
    ast.GeneratorExp: "comprehension",
    ast.Lambda: "lambda",
    ast.BinOp: "арифметика",
    ast.JoinedStr: "f-рядок",
    ast.Subscript: "індексація",
}


def violations(path: Path) -> list[str]:
    found = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            for child in ast.walk(node):
                kind = FORBIDDEN.get(type(child))
                if kind and not _is_type_hint(child):
                    found.append(f"{path}:{child.lineno} {node.name}: {kind}")
    return found


def _is_type_hint(node: ast.AST) -> bool:
    # list[str] в анотаціях — це Subscript, але не логіка
    return (
        isinstance(node, ast.Subscript)
        and isinstance(node.value, ast.Name)
        and node.value.id in {"list", "dict", "tuple", "set"}
    )


def main() -> int:
    problems = [v for path in sorted(Path("tests").rglob("test_*.py")) for v in violations(path)]
    print("\n".join(problems) or "OK: у тестових функціях немає логіки")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
