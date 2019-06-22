import os
import sys
import ctypes

PATH_ENV = "PATH"
PATH_SPLITTER = ";"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def print_path():
    for p in sys.path:
        print(20 * "*")
        print(p)


if __name__ == "__main__":
    # if not is_admin():
    #     ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

    library_path = os.path.dirname(os.path.realpath(__file__))
    print(library_path)

    print_path()

    if library_path in sys.path:
        print("pyfans is already in PATH variable")
    else:
        sys.path.append(library_path)
        print("successfully added pyfans to PATH variable")
