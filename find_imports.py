import os
import re

def find_imports():
    imports = set()
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Find import statements
                        import_lines = re.findall(r'^(?:import|from)\s+(\w+)', content, re.MULTILINE)
                        imports.update(import_lines)
                except:
                    pass

    for imp in sorted(imports):
        print(imp)

find_imports()