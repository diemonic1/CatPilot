# Значки пунктов меню трея из эмодзи в названии задачи.
# Меню трея — классическое Win32-меню, его текст рисует GDI: цветные эмодзи он не умеет,
# а символов, которых нет в Segoe UI и его запасных шрифтах (🥽, ᯅ, ⛶), не показывает вовсе.
# Поэтому значок из названия задачи рисуем картинкой и ставим слева от пункта
import ctypes
import os
import re
import unicodedata
import winreg
from contextlib import suppress

from PIL import Image, ImageChops, ImageDraw, ImageFont

SM_CXSMICON = 49

# Первый шрифт, в котором есть символ, и рисует значок. Segoe UI Emoji — цветной,
# остальные монохромные (рисуются цветом текста меню). SansSerifCollection есть только в Windows 11
ICON_FONTS = ["seguiemj.ttf", "seguisym.ttf", "SansSerifCollection.ttf", "seguihis.ttf"]
ICON_RENDER_SIZE = 96
ICON_JOINERS = "\u200d\ufe0e\ufe0f\u20e3"  # ZWJ, селекторы вида, keycap
BLACK = (0, 0, 0, 255)

trayBitmaps = {}
iconFonts = None

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [("biSize", ctypes.c_uint32), ("biWidth", ctypes.c_int32), ("biHeight", ctypes.c_int32),
                ("biPlanes", ctypes.c_uint16), ("biBitCount", ctypes.c_uint16), ("biCompression", ctypes.c_uint32),
                ("biSizeImage", ctypes.c_uint32), ("biXPelsPerMeter", ctypes.c_int32), ("biYPelsPerMeter", ctypes.c_int32),
                ("biClrUsed", ctypes.c_uint32), ("biClrImportant", ctypes.c_uint32)]

def IsIconChar(ch):
    if ch in ICON_JOINERS:
        return True
    if ch.isascii():
        return False

    category = unicodedata.category(ch)
    if category.startswith("S"):
        return True
    if category.startswith("L"):
        # Буква редкой письменности как значок (ᯅ), но не обычный текст
        return not unicodedata.name(ch, "").startswith(("LATIN", "CYRILLIC", "GREEK"))
    return False

def SplitTrayIcon(name):
    """Возвращает (значок или None, текст без значка). Значок — первая подряд идущая
    последовательность символов-значков в названии; все её вхождения убираются из текста"""
    match = None
    for found in re.finditer("[^\\s]+", name):
        run = ""
        for ch in found.group():
            if IsIconChar(ch):
                run += ch
            elif run:
                break
        letters = [ch for ch in run if unicodedata.category(ch).startswith("L")]
        # Несколько букв подряд — уже слово, а не значок
        if run.strip(ICON_JOINERS) and len(letters) <= 1 and (not letters or len(run.strip(ICON_JOINERS)) == 1):
            match = run
            break

    if match is None:
        return None, name

    text = " ".join(name.replace(match, " ").split())
    return match, text if text else name

def RenderIconGlyph(font, icon, color):
    image = Image.new("RGBA", (ICON_RENDER_SIZE * 2, ICON_RENDER_SIZE * 2), (0, 0, 0, 0))
    ImageDraw.Draw(image).text((ICON_RENDER_SIZE // 2, ICON_RENDER_SIZE // 2), icon, font=font, fill=color, embedded_color=True)
    return image

def LoadIconFonts():
    fonts = []
    fontsFolder = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")

    for fileName in ICON_FONTS:
        with suppress(Exception):
            font = ImageFont.truetype(os.path.join(fontsFolder, fileName), ICON_RENDER_SIZE * 2 // 3)
            # Как выглядит отсутствующий символ (.notdef) — чтобы отличать «нет символа» от значка
            fonts.append((font, RenderIconGlyph(font, "\U000F0000", BLACK).tobytes()))

    return fonts

def MenuTextColor():
    # Меню трея следует теме приложений Windows (см. SetPreferredAppMode в RunTray)
    with suppress(Exception):
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as key:
            if winreg.QueryValueEx(key, "AppsUseLightTheme")[0] == 0:
                return (240, 240, 240, 255)
    return BLACK

def RenderIconImage(icon, size):
    global iconFonts

    if iconFonts is None:
        iconFonts = LoadIconFonts()

    color = MenuTextColor()

    for font, missingGlyph in iconFonts:
        image = RenderIconGlyph(font, icon, color)
        box = image.getbbox()

        if box is None or RenderIconGlyph(font, icon, BLACK).tobytes() == missingGlyph:
            continue

        # Обрезаем по содержимому и вписываем в квадрат: у символов разная ширина и отступы
        image = image.crop(box)
        scale = size / max(image.size)
        image = image.resize((max(1, round(image.width * scale)), max(1, round(image.height * scale))), Image.LANCZOS)

        square = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        square.paste(image, ((size - image.width) // 2, (size - image.height) // 2))
        return square

    return None

def CreateMenuBitmap(image):
    """32-битный DIB с premultiplied alpha — так Windows рисует картинку пункта меню с прозрачностью"""
    header = BITMAPINFOHEADER(ctypes.sizeof(BITMAPINFOHEADER), image.width, -image.height, 1, 32, 0, 0, 0, 0, 0, 0)

    red, green, blue, alpha = image.split()
    pixels = Image.merge("RGBA", (ImageChops.multiply(blue, alpha), ImageChops.multiply(green, alpha),
                                  ImageChops.multiply(red, alpha), alpha)).tobytes()

    gdi32 = ctypes.windll.gdi32
    gdi32.CreateDIBSection.restype = ctypes.c_void_p
    gdi32.CreateDIBSection.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint, ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p, ctypes.c_uint32]

    bits = ctypes.c_void_p()
    bitmap = gdi32.CreateDIBSection(None, ctypes.byref(header), 0, ctypes.byref(bits), None, 0)
    if not bitmap or not bits.value:
        return None

    ctypes.memmove(bits, pixels, len(pixels))
    return bitmap

def TrayItemTextAndBitmap(name):
    """Текст пункта меню и картинка значка из названия задачи. Если значка нет или его
    нечем нарисовать — пункт остаётся как есть: исходное название без картинки"""
    icon, text = SplitTrayIcon(name)
    if icon is None:
        return name, None

    if icon not in trayBitmaps:
        bitmap = None
        with suppress(Exception):
            image = RenderIconImage(icon, ctypes.windll.user32.GetSystemMetrics(SM_CXSMICON) or 16)
            if image is not None:
                bitmap = CreateMenuBitmap(image)
        # Картинки живут до конца работы программы: меню пересоздаётся, а значков немного
        trayBitmaps[icon] = bitmap

    if trayBitmaps[icon] is None:
        return name, None

    return text, trayBitmaps[icon]
