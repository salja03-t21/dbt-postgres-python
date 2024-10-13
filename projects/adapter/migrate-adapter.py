import argparse
import ast
from collections import namedtuple
from pathlib import Path

Import = namedtuple("Import", ["module", "name", "alias"])


def get_imports(path):
    try:
        with open(path, encoding="utf-8") as fh:  # Use utf-8 encoding to handle various file types
            root = ast.parse(fh.read(), path)
    except Exception as e:
        print(f"Failed to parse {path}: {e}")
        return  # Skip files that cause parsing issues

    for node in ast.iter_child_nodes(root):
        if isinstance(node, ast.Import):
            module = []
        elif isinstance(node, ast.ImportFrom):
            module = node.module.split(".") if node.module else []  # Check if node.module is None
        else:
            continue

        for n in node.names:
            yield Import(module, n.name.split("."), n.asname)


parser = argparse.ArgumentParser("migrate_adapters")
parser.add_argument("path", help="The path to run the migration tool over.", type=str)
args = parser.parse_args()

path = Path(args.path)
pathlist = list(path.rglob("*.py"))  # Get the list of .py files

print(f"Scanning {len(pathlist)} files...")

total_dbt_imports = 0
invalid_dbt_imports = 0
path_to_invalid_imports = {}

for path in pathlist:
    print(f"Processing file: {path}")  # Print each file being processed
    path_to_invalid_imports[path] = []
    for imported_module in get_imports(str(path)):
        if imported_module.module and imported_module.module[0] == "dbt":
            total_dbt_imports += 1
            if len(imported_module.module) < 2 or imported_module.module[1] not in ("common", "adapters"):
                invalid_dbt_imports += 1
                path_to_invalid_imports[path].append(
                    f"{'.'.join(imported_module.module)}::{imported_module.name[0]}"
                )

# Check if any dbt imports were found
if total_dbt_imports == 0:
    print("No dbt imports found! Check the directory and the path provided.")
    exit(1)  # Exit early to prevent the ZeroDivisionError

migrated_imports = total_dbt_imports - invalid_dbt_imports
migrated_imports_progress = round((migrated_imports / total_dbt_imports) * 100, 2)

for path, invalid_imports in path_to_invalid_imports.items():
    if invalid_imports:
        print()
        print(f"\033[92m{path}:\033[0m")
        for invalid_import in invalid_imports:
            print(f"  - {invalid_import}")

print()
print(
    f"Migration progress: {migrated_imports_progress}% of dbt imports are valid (from adapters or common)"
)
print(f"Remaining core imports: {invalid_dbt_imports}")
