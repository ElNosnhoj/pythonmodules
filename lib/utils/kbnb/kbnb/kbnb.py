import os

# Windows
if os.name == 'nt':
    import msvcrt
    class kb:
        @classmethod
        def set_normal_term(cls): pass
        @classmethod
        def getch(cls): return msvcrt.getch().decode('utf-8')
        @classmethod
        def getarrow(cls):
            msvcrt.getch() # skip 0xE0
            c = msvcrt.getch()
            vals = [72, 77, 80, 75]
            return vals.index(ord(c.decode('utf-8')))
        @classmethod
        def kbhit(cls): return msvcrt.kbhit()

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

    class kb:
        @classmethod
        def set_normal_term(cls): termios.tcsetattr(fd, termios.TCSAFLUSH, old_term)
        @classmethod
        def getch(cls): return sys.stdin.read(1)
        @classmethod
        def getarrow(cls):
            c = sys.stdin.read(3)[2]
            vals = [65, 67, 66, 68]
            return vals.index(ord(c.decode('utf-8')))
        @classmethod
        def kbhit(cls):
            dr,dw,de = select([sys.stdin], [], [], 0)
            return dr != []

    
    atexit.register(kb.set_normal_term)


if __name__ == "__main__":
    while True:
        if kb.kbhit():
            c = kb.getch()
            if ord(c) == 27: # ESC
                break
            print(c)
             
    kb.set_normal_term()


