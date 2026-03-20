#=================================================
# File: prettyprint.py
# Developer: nosnhoj
# Desc: printing with color + emoji support!
#=================================================
import os
import re
import sys
import unicodedata
from enum import IntFlag

try:
    # Optional, better width handling if available
    from wcwidth import wcwidth as _wcwidth
except Exception:
    _wcwidth = None

__all__ = [
    "prettyprint",
    "prettify",
    "strip_ansi",
    "display_width",
    "ljust_display",
    "rjust_display",
    "center_display",
    "truncate_display",
    "STYLE",
    "ICON",
    "icon",
    "set_color_enabled",
    "color_enabled",
    "set_emoji_enabled",
    "emoji_enabled",
    "print_icons",
]

_HEX_RE = re.compile(r"^#([0-9A-Fa-f]{6})$")
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

# Global switches:
#   None  -> auto-detect
#   True  -> always enable
#   False -> always disable
_COLOR_ENABLED = None
_EMOJI_ENABLED = True


#========================
# Styles
#========================
class STYLE(IntFlag):
    BOLD = 1 << 0
    DIM = 1 << 1
    ITALIC = 1 << 2
    UNDERLINE = 1 << 3
    BLINK = 1 << 4
    INVERTED = 1 << 5
    HIDDEN = 1 << 6
    STRIKETHROUGH = 1 << 7


_SGR = {
    STYLE.BOLD: "1",
    STYLE.DIM: "2",
    STYLE.ITALIC: "3",
    STYLE.UNDERLINE: "4",
    STYLE.BLINK: "5",
    STYLE.INVERTED: "7",
    STYLE.HIDDEN: "8",
    STYLE.STRIKETHROUGH: "9",
}


#========================
# Icons / Emoji
#========================
class ICON:
    # Logging / status
    INFO        = "ℹ️"
    SUCCESS     = "✅"
    OK          = "✅"
    ERROR       = "❌"
    FAIL        = "✖"
    WARN        = "⚠️"
    CRITICAL    = "🛑"
    QUESTION    = "❓"
    PIN         = "📌"
    NOTE        = "📝"
    TIP         = "💡"
    STAR        = "⭐"
    SPARK       = "🌟"
    MAGIC       = "✨"
    CHECK       = "✔️"
    CROSS       = "✖️"

    # Progress / actions
    START       = "▶️"
    STOP        = "⏹️"
    PAUSE       = "⏸️"
    PLAY        = "▶️"
    REFRESH     = "🔄"
    REPEAT      = "🔁"
    LOOP        = "🔁"
    FAST        = "⚡"
    WAIT        = "⏳"
    TIME        = "🕒"
    CLOCK       = "🕒"
    HOURGLASS   = "⌛"
    ARROW       = "➡️"
    UP          = "⬆️"
    DOWN        = "⬇️"
    LEFT        = "⬅️"
    RIGHT       = "➡️"

    # Build / dev / system
    WORK        = "🔧"
    BUILD       = "🛠️"
    CONFIG      = "⚙️"
    TOOLBOX     = "🧰"
    AXE         = "🪓"
    SCREWDRIVER = "🪛"
    HAMMER      = "🔨"
    GEAR        = "⚙️"
    TEST        = "🧪"
    BUG         = "🐞"
    FIRE        = "🔥"
    BOT         = "🤖"
    CPU         = "🧠"
    CHIP        = "💻"
    TERMINAL    = "🖥️"
    CODE        = "💻"
    PACKAGE     = "📦"
    FILE        = "📄"
    FOLDER      = "📁"
    LOCK        = "🔒"
    UNLOCK      = "🔓"
    KEY         = "🔑"
    SEARCH      = "🔍"
    LINK        = "🔗"

    # Network / data
    NETWORK     = "🌐"
    SATELLITE   = "📡"
    PLUG        = "🔌"
    DOWNLOAD    = "📥"
    UPLOAD      = "📤"
    SAVE        = "💾"
    DATABASE    = "🗄️"
    CLOUD       = "☁️"
    EMAIL       = "📧"

    # Vehicles / movement
    ROCKET      = "🚀"
    UFO         = "🛸"
    PLANE       = "✈️"
    HELI        = "🚁"
    CAR         = "🚗"
    BIKE        = "🚲"
    BOAT        = "⛵"
    MOTORCYCLE  = "🏍️"
    CANOE       = "🛶"

    # Space / weather / nature
    PLANET      = "🪐"
    SPACE       = "🌌"
    SHOOTING    = "🌠"
    SUN         = "☀️"
    MOON        = "🌙"
    RAIN        = "🌧️"
    WAVE        = "🌊"
    FLOWER      = "🌸"
    LEAF        = "🍂"
    RAINBOW     = "🌈"
    SNOW        = "❄️"
    TREE        = "🌳"

    # Creatures / fun
    ALIEN       = "👽"
    DRAGON      = "🐉"
    GHOST       = "👻"
    SKULL       = "💀"
    UNICORN     = "🦄"

    # Media / misc
    ART         = "🎨"
    GUITAR      = "🎸"
    GAME        = "🎮"
    JOYSTICK    = "🕹️"
    PUZZLE      = "🧩"
    CANDLE      = "🕯️"
    TROPHY      = "🏆"
    TARGET      = "🎯"
    PARTY       = "🎉"
    BOOKMARK    = "🔖"


_FALLBACK = {
    # Logging / status
    ICON.INFO: "[INFO]",
    ICON.SUCCESS: "[OK]",
    ICON.OK: "[OK]",
    ICON.ERROR: "[ERR]",
    ICON.FAIL: "[FAIL]",
    ICON.WARN: "[WARN]",
    ICON.CRITICAL: "[CRIT]",
    ICON.QUESTION: "[?]",
    ICON.PIN: "[PIN]",
    ICON.NOTE: "[NOTE]",
    ICON.TIP: "[TIP]",
    ICON.STAR: "*",
    ICON.SPARK: "*",
    ICON.MAGIC: "*",
    ICON.CHECK: "[OK]",
    ICON.CROSS: "[X]",

    # Progress / actions
    ICON.START: ">",
    ICON.STOP: "X",
    ICON.PAUSE: "||",
    ICON.PLAY: ">",
    ICON.REFRESH: "~",
    ICON.REPEAT: "R",
    ICON.LOOP: "R",
    ICON.FAST: "[FAST]",
    ICON.WAIT: "...",
    ICON.TIME: "[TIME]",
    ICON.CLOCK: "[TIME]",
    ICON.HOURGLASS: "[WAIT]",
    ICON.ARROW: "->",
    ICON.UP: "^",
    ICON.DOWN: "v",
    ICON.LEFT: "<-",
    ICON.RIGHT: "->",

    # Build / dev / system
    ICON.WORK: "[*]",
    ICON.BUILD: "[BUILD]",
    ICON.CONFIG: "[CFG]",
    ICON.TOOLBOX: "[TOOLS]",
    ICON.AXE: "[AXE]",
    ICON.SCREWDRIVER: "[DRV]",
    ICON.HAMMER: "[HAM]",
    ICON.GEAR: "[GEAR]",
    ICON.TEST: "[TEST]",
    ICON.BUG: "[BUG]",
    ICON.FIRE: "[HOT]",
    ICON.BOT: "[BOT]",
    ICON.CPU: "[CPU]",
    ICON.CHIP: "[PC]",
    ICON.TERMINAL: "[TERM]",
    ICON.CODE: "[CODE]",
    ICON.PACKAGE: "[PKG]",
    ICON.FILE: "[FILE]",
    ICON.FOLDER: "[DIR]",
    ICON.LOCK: "[LOCK]",
    ICON.UNLOCK: "[OPEN]",
    ICON.KEY: "[KEY]",
    ICON.SEARCH: "[SEARCH]",
    ICON.LINK: "[LINK]",

    # Network / data
    ICON.NETWORK: "[NET]",
    ICON.SATELLITE: "[SIG]",
    ICON.PLUG: "[PLUG]",
    ICON.DOWNLOAD: "[DOWN]",
    ICON.UPLOAD: "[UP]",
    ICON.SAVE: "[SAVE]",
    ICON.DATABASE: "[DB]",
    ICON.CLOUD: "[CLOUD]",
    ICON.EMAIL: "[MAIL]",

    # Vehicles / movement
    ICON.ROCKET: "[RUN]",
    ICON.UFO: "[UFO]",
    ICON.PLANE: "[PLANE]",
    ICON.HELI: "[HELI]",
    ICON.CAR: "[CAR]",
    ICON.BIKE: "[BIKE]",
    ICON.BOAT: "[BOAT]",
    ICON.MOTORCYCLE: "[MOTO]",
    ICON.CANOE: "[CANOE]",

    # Space / weather / nature
    ICON.PLANET: "[PLANET]",
    ICON.SPACE: "[SPACE]",
    ICON.SHOOTING: "[STAR]",
    ICON.SUN: "[SUN]",
    ICON.MOON: "[MOON]",
    ICON.RAIN: "[RAIN]",
    ICON.WAVE: "[WAVE]",
    ICON.FLOWER: "[FLOWER]",
    ICON.LEAF: "[LEAF]",
    ICON.RAINBOW: "[RAINBOW]",
    ICON.SNOW: "[SNOW]",
    ICON.TREE: "[TREE]",

    # Creatures / fun
    ICON.ALIEN: "[ALIEN]",
    ICON.DRAGON: "[DRAGON]",
    ICON.GHOST: "[GHOST]",
    ICON.SKULL: "[SKULL]",
    ICON.UNICORN: "[UNICORN]",

    # Media / misc
    ICON.ART: "[ART]",
    ICON.GUITAR: "[MUSIC]",
    ICON.GAME: "[GAME]",
    ICON.JOYSTICK: "[JOY]",
    ICON.PUZZLE: "[PUZZLE]",
    ICON.CANDLE: "[LIGHT]",
    ICON.TROPHY: "[WIN]",
    ICON.TARGET: "[TARGET]",
    ICON.PARTY: "[PARTY]",
    ICON.BOOKMARK: "[MARK]",
}


def set_emoji_enabled(val: bool):
    global _EMOJI_ENABLED
    _EMOJI_ENABLED = bool(val)


def emoji_enabled():
    return _EMOJI_ENABLED


def icon(value):
    if _EMOJI_ENABLED:
        return value
    return _FALLBACK.get(value, "")


#========================
# Color control
#========================
def set_color_enabled(enabled):
    global _COLOR_ENABLED
    if enabled not in (True, False, None):
        raise ValueError("enabled must be True, False, or None")
    _COLOR_ENABLED = enabled


def color_enabled():
    return _COLOR_ENABLED


def _supports_color(stream):
    if _COLOR_ENABLED is False:
        return False
    if _COLOR_ENABLED is True:
        return True

    if os.environ.get("NO_COLOR") is not None:
        return False

    if os.environ.get("CLICOLOR_FORCE", "") not in ("", "0"):
        return True

    if stream is None:
        stream = sys.stdout

    if not hasattr(stream, "isatty") or not stream.isatty():
        return False

    term = os.environ.get("TERM", "")
    if term.lower() == "dumb":
        return False

    if os.name == "nt":
        if os.environ.get("WT_SESSION"):
            return True
        if os.environ.get("TERM_PROGRAM") == "vscode":
            return True
        if "ANSICON" in os.environ:
            return True
        if os.environ.get("ConEmuANSI", "").upper() == "ON":
            return True
        if term:
            return True
        return False

    return True


#========================
# ANSI / display width helpers
#========================
def strip_ansi(text):
    return _ANSI_RE.sub("", str(text))


def _char_display_width(ch):
    # Best case: use wcwidth if installed
    if _wcwidth is not None:
        w = _wcwidth(ch)
        return 0 if w < 0 else w

    # Fallback heuristics
    # Zero-width / combining / formatting chars
    cat = unicodedata.category(ch)
    if cat in ("Mn", "Me", "Cf"):
        return 0

    # Variation selectors
    o = ord(ch)
    if 0xFE00 <= o <= 0xFE0F:
        return 0

    # Zero-width joiner
    if o == 0x200D:
        return 0

    # Tabs are ambiguous; keep it simple
    if ch == "\t":
        return 4

    # East Asian Wide / Fullwidth usually takes 2 cells
    if unicodedata.east_asian_width(ch) in ("W", "F"):
        return 2

    return 1


def display_width(text):
    """
    Return approximate terminal display width of text.
    ANSI codes are ignored.
    """
    s = strip_ansi(text)
    return sum(_char_display_width(ch) for ch in s)


def ljust_display(text, width, fillchar=" "):
    text = str(text)
    pad = max(0, width - display_width(text))
    return text + (fillchar * pad)


def rjust_display(text, width, fillchar=" "):
    text = str(text)
    pad = max(0, width - display_width(text))
    return (fillchar * pad) + text


def center_display(text, width, fillchar=" "):
    text = str(text)
    pad = max(0, width - display_width(text))
    left = pad // 2
    right = pad - left
    return (fillchar * left) + text + (fillchar * right)


def truncate_display(text, width, suffix="..."):
    """
    Truncate by display width, not len().
    ANSI codes are stripped for truncation logic.
    """
    raw = strip_ansi(text)
    if display_width(raw) <= width:
        return raw

    suffix_w = display_width(suffix)
    if suffix_w >= width:
        out = ""
        cur = 0
        for ch in suffix:
            w = _char_display_width(ch)
            if cur + w > width:
                break
            out += ch
            cur += w
        return out

    out = ""
    cur = 0
    limit = width - suffix_w
    for ch in raw:
        w = _char_display_width(ch)
        if cur + w > limit:
            break
        out += ch
        cur += w
    return out + suffix


#========================
# Color helpers
#========================
def _hex_to_rgb(value):
    if not isinstance(value, str) or not _HEX_RE.fullmatch(value):
        raise ValueError("Invalid color. Must be #RRGGBB")
    value = value[1:]
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def _normalize_color(value):
    if isinstance(value, str):
        return _hex_to_rgb(value)

    if isinstance(value, (tuple, list)) and len(value) == 3:
        r, g, b = value
        if not all(isinstance(x, int) for x in (r, g, b)):
            raise ValueError("RGB tuple values must be integers")
        if not all(0 <= x <= 255 for x in (r, g, b)):
            raise ValueError("RGB tuple values must be in range 0..255")
        return r, g, b

    raise ValueError("Invalid color. Must be #RRGGBB or an (r, g, b) tuple")


def _fg_code(value):
    r, g, b = _normalize_color(value)
    return f"38;2;{r};{g};{b}"


def _bg_code(value):
    r, g, b = _normalize_color(value)
    return f"48;2;{r};{g};{b}"


def _style_code(style):
    if style is None:
        return ""

    if not isinstance(style, int):
        raise TypeError("style must be an int or STYLE flag")

    return ";".join(code for flag, code in _SGR.items() if style & flag)


#========================
# Core
#========================
def prettify(text, fg=None, bg=None, style=None, *, stream=None, force=False, reset=True):
    """
    Return text wrapped in ANSI color/style codes.
    """
    stream = sys.stdout if stream is None else stream
    text = str(text)

    if not force and not _supports_color(stream):
        return text

    parts = []

    if fg is not None:
        parts.append(_fg_code(fg))

    if bg is not None:
        parts.append(_bg_code(bg))

    if style is not None:
        sc = _style_code(style)
        if sc:
            parts.append(sc)

    if not parts:
        return text

    prefix = f"\033[{';'.join(parts)}m"
    suffix = "\033[0m" if reset else ""
    return f"{prefix}{text}{suffix}"


__print = print


def prettyprint(
    *objects,
    sep=" ",
    end="\n",
    file=None,
    flush=False,
    fg=None,
    bg=None,
    style=None,
    force=False,
    reset=True,
):
    """
    Drop-in replacement for print() with optional ANSI styling.
    """
    file = sys.stdout if file is None else file
    text = sep.join(str(obj) for obj in objects)
    text = prettify(
        text,
        fg=fg,
        bg=bg,
        style=style,
        stream=file,
        force=force,
        reset=reset,
    )
    __print(text, end=end, file=file, flush=flush)


#========================
# Emoji dump
#========================
def print_icons():
    print(
        "🚀🛸🪐🌌⭐🌠👽🤖☀️🌙🌧️⚡🌊🌸🍂🌈"
        "🔧🛠️⚙️🪓🪛🧰🔨"
        "✈️🚁🚗🚲⛵🏍️🛶"
        "ℹ️📌✅❌⚠️✖➡️⬆️⬇️⬅️🔁🔄⏳⌛🕒"
        "🎨🎸🎮🕹️🐉🧩🕯️🎯🎉🏆"
        "🔥💡📦📁📄🧪🐞📡🔌💾📥📤🔍🔒🔓🔑🔗🌐☁️📧"
        "👻💀🦄✨✔️❓📝🔖"
    )


#========================
# Demo
#========================
if __name__ == "__main__":
    print = prettyprint

    print("Simple!", style=STYLE.BOLD | STYLE.UNDERLINE)
    print("Just plain text")
    print("Bright red text", fg="#ff0000")
    print("Blue on yellow", fg="#0000ff", bg="#ffff00")
    print("Bold green", fg="#00ff00", style=STYLE.BOLD)
    print("Underlined cyan", fg="#00ffff", style=STYLE.UNDERLINE)
    print("Dim gray text", fg="#888888", style=STYLE.DIM)
    print("Inverted magenta", fg="#ff00ff", style=STYLE.INVERTED)
    print()

    print("Combinations", style=STYLE.BOLD | STYLE.UNDERLINE)
    print("Bold + Underlined purple", fg="#a020f0", style=STYLE.BOLD | STYLE.UNDERLINE)
    print("Blinking (if supported)", fg="#ff0000", style=STYLE.BLINK)
    print("Hidden text (easter egg)", fg="#00ff00", style=STYLE.HIDDEN)
    print("Strikethrough example", fg="#ff4444", style=STYLE.STRIKETHROUGH)
    print()

    print("Contrasting", style=STYLE.BOLD | STYLE.UNDERLINE)
    print("Red on Black", fg="#ff0000", bg="#000000")
    print("Black on Red", fg="#000000", bg="#ff0000")
    print("White on Blue", fg="#ffffff", bg="#0000aa")
    print("Yellow on Purple", fg="#ffff00", bg="#800080", style=STYLE.BOLD)
    print()

    print("Separator if supported", style=STYLE.BOLD | STYLE.UNDERLINE)
    print("A", "B", "C", sep=" • ", fg="#00ff00", style=STYLE.BOLD)
    print()

    print("Keep color persisting", style=STYLE.BOLD | STYLE.UNDERLINE)
    print("Hello", end=" ", fg="#ffaa00", style=STYLE.BOLD, reset=False)
    print("World!", fg="#ffaa00", style=STYLE.BOLD)
    print()

    print("Status examples", style=STYLE.BOLD | STYLE.UNDERLINE)
    print("[INFO]", fg="#00ccff", style=STYLE.BOLD, end=" ")
    print("System initialized successfully")
    print("[WARN]", fg="#ffcc00", style=STYLE.BOLD, end=" ")
    print("Low disk space")
    print("[ERROR]", fg="#ff4444", style=STYLE.BOLD, end=" ")
    print("Failed to open configuration file")
    print("✅ Success.", fg="#00ff00", style=STYLE.BOLD)
    print("❌ Failed!", fg="#ff4444", style=STYLE.BOLD)
    print("⚠️  Warning!", fg="#ffaa00")
    print("🔧 Working ...", fg="#00ffff", style=STYLE.BOLD)
    print("Press Enter to close ...", fg="#888888", style=STYLE.DIM)
    print()

    print("Gradient", style=STYLE.BOLD | STYLE.UNDERLINE)
    colors = ["#ff0000", "#ff7f00", "#ffff00", "#00ff00", "#0000ff", "#4b0082", "#8b00ff"]
    for i, c in enumerate(colors):
        print(f"Color {i+1}", fg=c, style=STYLE.BOLD, end="  ")
    print()
    print()

    print("Table!", style=STYLE.BOLD | STYLE.UNDERLINE)
    headers = ["Name", "Age", "Role"]
    print(f"{headers[0]:<10}{headers[1]:<5}{headers[2]:<10}", style=STYLE.BOLD | STYLE.UNDERLINE, fg="#00ffcc")

    rows = [
        ("Alice", 28, "Engineer"),
        ("Bob", 34, "Designer"),
        ("Charlie", 41, "Manager"),
    ]
    for name, age, role in rows:
        print(f"{name:<10}{age:<5}{role:<10}", fg="#cccccc")
    print()

    print("🌈 Rainbow Text Demo", style=STYLE.BOLD | STYLE.UNDERLINE)
    for word, color in zip("RAINBOW", ["#ff0000", "#ff7f00", "#ffff00", "#00ff00", "#0000ff", "#4b0082", "#8b00ff"]):
        print(word, fg=color, style=STYLE.BOLD, end="")
    print()
    print()

    print("Icon examples", style=STYLE.BOLD | STYLE.UNDERLINE)
    print(icon(ICON.INFO), "Informational message", fg="#00ccff")
    print(icon(ICON.SUCCESS), "Everything looks good", fg="#00ff00")
    print(icon(ICON.WARN), "Something needs attention", fg="#ffaa00")
    print(icon(ICON.ERROR), "Something went wrong", fg="#ff4444", style=STYLE.BOLD)
    print(icon(ICON.BOT), "Automated job started", fg="#00ffff")
    print(icon(ICON.ROCKET), "Launching service", fg="#ff66cc")
    print(icon(ICON.BUG), "Found a bug", fg="#ff5555")
    print(icon(ICON.TEST), "Running tests", fg="#aaffaa")
    print(icon(ICON.SEARCH), "Searching files", fg="#ccccff")
    print(icon(ICON.LOCK), "Secured resource", fg="#ffdd88")
    print()

    print("Icon gallery", style=STYLE.BOLD | STYLE.UNDERLINE)
    print_icons()
    print()

    print("Tuple RGB colors", style=STYLE.BOLD | STYLE.UNDERLINE)
    print("RGB tuple foreground", fg=(255, 120, 0), style=STYLE.BOLD)
    print("RGB tuple background", fg=(255, 255, 255), bg=(30, 60, 120))
    print()

    print("prettify() examples", style=STYLE.BOLD | STYLE.UNDERLINE)
    normal_print = __print
    normal_print(prettify("Styled via prettify()", fg="#00ffaa", style=STYLE.BOLD))
    normal_print(prettify("This uses built-in print underneath", fg="#ff88ff"))
    print()

    print("Force color example", style=STYLE.BOLD | STYLE.UNDERLINE)
    forced = prettify("Forced ANSI string", fg="#ff8800", style=STYLE.BOLD, force=True)
    __print(repr(forced))
    print()

    print("ANSI stripping", style=STYLE.BOLD | STYLE.UNDERLINE)
    colored = prettify("Strip me", fg="#00ffcc", style=STYLE.BOLD, force=True)
    __print("raw   :", repr(colored))
    __print("clean :", repr(strip_ansi(colored)))
    print()

    print("Emoji toggle demo", style=STYLE.BOLD | STYLE.UNDERLINE)
    print(icon(ICON.ROCKET), "Emoji enabled")
    set_emoji_enabled(False)
    print(icon(ICON.ROCKET), "Emoji disabled fallback")
    set_emoji_enabled(True)
    print(icon(ICON.ROCKET), "Emoji enabled again")
    print()

    print("Color toggle demo", style=STYLE.BOLD | STYLE.UNDERLINE)
    print("Colors currently auto-detected", fg="#00ffcc")
    set_color_enabled(False)
    print("This should be plain text even with fg/style kwargs", fg="#ff0000", style=STYLE.BOLD)
    set_color_enabled(None)
    print("Auto-detect restored", fg="#00ffcc")
    print()

    print("Extra icons", style=STYLE.BOLD | STYLE.UNDERLINE)
    extras = [
        ICON.UFO, ICON.PLANET, ICON.SPACE, ICON.SUN, ICON.MOON,
        ICON.RAIN, ICON.WAVE, ICON.FLOWER, ICON.LEAF, ICON.RAINBOW,
        ICON.PLANE, ICON.HELI, ICON.CAR, ICON.BIKE, ICON.BOAT, ICON.MOTORCYCLE, ICON.CANOE,
        ICON.ALIEN, ICON.DRAGON, ICON.GHOST, ICON.SKULL, ICON.UNICORN,
        ICON.ART, ICON.GUITAR, ICON.GAME, ICON.JOYSTICK, ICON.PUZZLE,
        ICON.CANDLE, ICON.TROPHY, ICON.TARGET, ICON.PARTY, ICON.BOOKMARK,
    ]
    for ic in extras:
        print(icon(ic), end=" ")
    print()
    print()

    # potentially useful icons
    # 🚀🛸🪐🌌⭐🌠👽🤖☀️🌙🌧️⚡🌊🌸🍂🌈🔧🛠️⚙️🪓🪛🧰✈️🚁🚗🚲⛵🏍️🛶ℹ️📌✅❌⚠️✖️➡️⬆️🔁🎨🎸🎮🕹️🐉🧩🕯️🔥💡📦📁📄🧪🐞📡🔌💾📥📤🔍🔒🔓🔑🔗🌐☁️📧👻💀🦄✨✔️❓📝🔖🛑
