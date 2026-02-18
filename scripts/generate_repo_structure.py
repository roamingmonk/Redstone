"""
Redstone → docs/Repository_Structure.md  (Mac / Python)
Run using: python scripts/generate_repo_structure.py
"""

import os
from datetime import datetime

EXCLUDE = {
    "__pycache__", ".pyc", ".pyo", ".pyd",
    ".git", ".venv", "venv", "node_modules",
    "dist", "build", ".mypy_cache", ".pytest_cache", ".idea",
    ".gitignore", ".gitattributes", ".gitmodules", "Thumbs.db", ".DS_Store"
}

def is_excluded(name):
    for token in EXCLUDE:
        if token in name:
            return True
    return False

def build_tree(root_path, prefix=""):
    lines = []
    try:
        entries = sorted(os.listdir(root_path))
    except PermissionError:
        return lines

    entries = [e for e in entries if not is_excluded(e)]

    for i, entry in enumerate(entries):
        connector = "└── " if i == len(entries) - 1 else "├── "
        lines.append(f"{prefix}{connector}{entry}")
        full_path = os.path.join(root_path, entry)
        if os.path.isdir(full_path):
            extension = "    " if i == len(entries) - 1 else "│   "
            lines.extend(build_tree(full_path, prefix + extension))

    return lines

def main():
    os.makedirs("docs", exist_ok=True)
    out_path = os.path.join("docs", "Repository_Structure.md")

    root = os.path.basename(os.path.abspath("."))
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    tree_lines = [root] + build_tree(".")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"## Repository Structure (generated {timestamp})\n")
        f.write("```text\n")
        f.write("\n".join(tree_lines))
        f.write("\n```\n")

    print(f"✅ Wrote {out_path}")

if __name__ == "__main__":
    main()
