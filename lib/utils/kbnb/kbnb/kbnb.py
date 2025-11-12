import os


class __kb:
    buffer = ""
    @classmethod
    def set_normal_term(cls): pass
    @classmethod
    def __ch(cls): return None
    @classmethod
    def get_ch(cls, blocking=False): 
        if blocking: return cls.__ch()
        else: return cls.__ch() if cls.hit() else None
    @classmethod
    def __arrow(cls): return None
    @classmethod
    def get_arrow(cls, blocking=False): 
        if blocking: return cls.__arrow()
        else: return cls.__arrow() if cls.hit() else None
    @classmethod
    def get_line(cls, blocking=False):
        if blocking: 
            while True:
                if c:=kb.get_ch(True):
                    if c in ['\r','\n']:
                        out = cls.buffer
                        cls.buffer=""
                        return out
                    cls.buffer+=c
        elif c:=kb.get_ch():
            if c in ['\r','\n']:
                out = cls.buffer
                cls.buffer=""
                return out
            cls.buffer+=c
            return None

# Windows
if os.name == 'nt':
    import msvcrt
    class kb(__kb):
        @classmethod
        def __ch(cls): return msvcrt.getch().decode('utf-8')
        @classmethod
        def __arrow(cls): msvcrt.getch(); return [72, 77, 80, 75].index(ord(msvcrt.getch().decode('utf-8'))) # skip 0xE0
        @classmethod
        def hit(cls): return msvcrt.kbhit()

# Posix (Linux, OS X)
else:
    import sys
    import termios
    import atexit
    from select import select

    fd = sys.stdin.fileno()
    new_term = termios.tcgetattr(fd)
    old_term = termios.tcgetattr(fd)
    new_term[3] = (new_term[3] & ~termios.ICANON & ~termios.ECHO)
    termios.tcsetattr(fd, termios.TCSAFLUSH, new_term)

    class kb(__kb):
        @classmethod
        def set_normal_term(cls): termios.tcsetattr(fd, termios.TCSAFLUSH, old_term)
        @classmethod
        def __ch(cls): return sys.stdin.read(1)
        @classmethod
        def __arrow(cls): return [65, 67, 66, 68].index(ord(sys.stdin.read(3)[2].encode('utf-8')))
        @classmethod
        def hit(cls): return select([sys.stdin], [], [], 0)[0] != []
    atexit.register(kb.set_normal_term)


if __name__ == "__main__":
    print("ARROW KINDA JANKY")

    print("Wait for any key nb")
    while not kb.hit(): pass

    print("Wait for specific key nb")
    while kb.get_ch()!='\x1b': pass

    print("Wait for line nb")
    while True:
        if line:=kb.get_line():
            print(line)
            break
    



