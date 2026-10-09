# -*- mode: python ; coding: utf-8 -*-
# Сборка: pyinstaller.exe --noconfirm CatPilot.spec
#
# Модули, которые PyInstaller подтягивает по цепочке необязательных импортов библиотек,
# но которые ни ядро, ни окно (--gui) при работе не загружают. Везде, где библиотеки
# их импортируют, импорт обёрнут в try/except ImportError, поэтому без них ничего не ломается
EXCLUDES = [
    # tkinter + Tcl/Tk: остался от старого интерфейса, pyautogui тянет его ради
    # alert()/mouseInfo(), которые CatPilot не использует
    "tkinter", "_tkinter", "mouseinfo",
    # numpy: pyscreeze (поиск картинки на экране в pyautogui) — не используется
    "numpy",
    # Асинхронные клиенты и серверы, которые telebot/werkzeug/pywebview умеют
    # использовать опционально
    "aiohttp", "aiosignal", "aiohappyeyeballs", "yarl", "multidict", "frozenlist", "propcache",
    "gevent", "greenlet", "zope", "twisted", "service_identity",
    "cherrypy", "cheroot", "jaraco",
    # Шифрование для adhoc-SSL в werkzeug и pyOpenSSL в urllib3 — HTTPS обычным ssl работает и так
    "cryptography", "OpenSSL",
    # Прочее, что программе не нужно
    "yaml", "dateutil", "psutil", "setuptools", "pkg_resources",
    "win32com", "pythoncom", "pythonwin",
    "PIL.ImageTk", "PIL._imagingtk", "PIL.ImageQt", "PIL._avif", "PIL.AvifImagePlugin",
]

a = Analysis(
    ['CatPilot.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=EXCLUDES,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CatPilot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['CatPilot.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CatPilot',
)
