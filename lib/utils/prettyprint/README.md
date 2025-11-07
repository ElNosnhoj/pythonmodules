# lib/utils/prettyprint

## Installation
via https
```
pip install git+https://github.com/ElNosnhoj/pythonmodules.git@main#subdirectory=lib/utils/prettyprint
```

via ssh
```
pip install git+ssh://git@github.com:ElNosnhoj/pythonmodules.git@main#subdirectory=lib/utils/prettyprint

```

via local
```
pip install <path>/pythonmodules/lib/utils/prettyprint
```

to uninstall
```
pip uninstall prettyprint
```


## Usage
```python
from lib.utils.prettyprint.prettyprint import STYLE, prettyprint as print
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


print("Seperator if supported", style=STYLE.BOLD | STYLE.UNDERLINE)
print("A", "B", "C", sep=" • ", fg="#00ff00", style=STYLE.BOLD)
print()

print("Keep color persisting", style=STYLE.BOLD | STYLE.UNDERLINE)
print("Hello", end=" ", fg="#ffaa00", style=STYLE.BOLD)
print("World!", fg="#ffaa00", style=STYLE.BOLD)
print()

print("Status examples", style=STYLE.BOLD | STYLE.UNDERLINE)
print("[INFO]", fg="#00ccff", style=STYLE.BOLD, end=" ")
print("System initialized successfully")
print("[WARN]", fg="#ffcc00", style=STYLE.BOLD, end=" ")
print("Low disk space")
print("[ERROR]", fg="#ff4444", style=STYLE.BOLD, end=" ")
print("Failed to open configuration file")
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
for word, color in zip("RAINBOW", ["#ff0000","#ff7f00","#ffff00","#00ff00","#0000ff","#4b0082","#8b00ff"]):
    print(word, fg=color, style=STYLE.BOLD, end="")
print()
```



