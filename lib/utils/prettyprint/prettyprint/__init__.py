#=================================================
# File: prettyprint.py
# Developer: nosnhoj
# Desc: printing with color!
#=================================================
import re

class STYLE:
	RESET			= 1<<0
	BOLD			= 1<<1
	DIM				= 1<<2
	UNDERLINE		= 1<<4
	BLINK			= 1<<5
	INVERTED 		= 1<<7
	HIDDEN 			= 1<<8
	STRIKETHROUGH	= 1<<9

def __hex_rgb(s):
    if not re.match(r'^#([0-9A-Fa-f]{6})$', s): raise ValueError("Invalid color. Must be #RRGGBB")
    s = s.lstrip('#')
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)     
def __hex_rgb_fg(s):
	r,g,b = __hex_rgb(s)
	return f"38;2;{r};{g};{b}"
def __hex_rgb_bg(s):
	r,g,b = __hex_rgb(s)
	return f"48;2;{r};{g};{b}"
def __stylish(val):
	return ';'.join([str(i) for i in range(val.bit_length()) if (val >> i) & 1])

def prettify(s,fg=None,bg=None,style=None):
	# individual formatting
	fg=__hex_rgb_fg(fg) if fg else ''
	bg=__hex_rgb_bg(bg) if bg else ''
	st = __stylish(style) if style else ''

	# combining
	if fg==bg==st: code = ''
	else: code = f"\033[{';'.join([w for w in [fg,bg,st] if w])}m"

	return f"{code}{s}\033[0m"

__print = print
def prettyprint(*objects, sep=None, end=None, file=None, flush=False,fg:str=None, bg:str=None, style:int=None):
	s = f"{' '.join([str(o) for o in objects])}"
	s = prettify(s,fg,bg,style)
	end = end and prettify(end,fg,bg,style)
	__print(s,sep=sep,end=end,file=file,flush=flush)

__all__ = ['prettyprint', 'STYLE']

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
	for word, color in zip("RAINBOW", ["#ff0000","#ff7f00","#ffff00","#00ff00","#0000ff","#4b0082","#8b00ff"]):
		print(word, fg=color, style=STYLE.BOLD, end="")
	print()



	# potentially useful icons
	# 🚀🛸🪐🌌⭐🌠👽🤖☀️🌙🌧️⚡🌊🌸🍂🌈🔧🛠️⚙️🪓🪛🧰✈️🚁🚗🚲⛵🏍️🛶ℹ️📌✅❌⚠️✖➡️⬆️🔁🎨🎸🎮🕹️🐉🧩🕯️
