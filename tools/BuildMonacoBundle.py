# Генерирует catpilot_monaco.py — редактор Monaco, упакованный в Python-модуль.
# Так PyInstaller забирает его в сборку сам, без --add-data и ручного копирования.
#
# Запускать только при обновлении Monaco:
#   npm pack monaco-editor@0.52.2
#   tar xzf monaco-editor-0.52.2.tgz
#   python tools\BuildMonacoBundle.py package 0.52.2
import base64
import io
import os
import sys
import zipfile

# Только то, что нужно для подсветки VBS: остальные языки, воркеры TS/JSON/CSS
# и переводы интерфейса редактора не нужны
FILES = [
    "vs/loader.js",
    "vs/editor/editor.main.js",
    "vs/editor/editor.main.css",
    "vs/base/worker/workerMain.js",
    "vs/basic-languages/vb/vb.js",
    "vs/base/browser/ui/codicons/codicon/codicon.ttf",
]

TEMPLATE = '''# Сгенерировано tools/BuildMonacoBundle.py, вручную не редактировать.
# Monaco Editor {version} (MIT, https://github.com/microsoft/monaco-editor), файлы из min/vs
import base64
import io
import zipfile

MONACO_VERSION = "{version}"

MONACO_ZIP = (
{chunks}
)

def OpenMonacoArchive():
    return zipfile.ZipFile(io.BytesIO(base64.b64decode(MONACO_ZIP)))
'''

def main():
    packageDir, version = sys.argv[1], sys.argv[2]

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in FILES:
            archive.write(os.path.join(packageDir, "min", path), path)

    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    chunks = "\n".join('    "' + encoded[i:i + 120] + '"' for i in range(0, len(encoded), 120))

    target = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "catpilot_monaco.py")
    with open(target, "w", encoding="utf-8", newline="\n") as file:
        file.write(TEMPLATE.format(version=version, chunks=chunks))

    print(target, len(buffer.getvalue()) // 1024, "KB zip")

if __name__ == "__main__":
    main()
