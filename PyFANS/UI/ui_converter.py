import os
import sys
import fnmatch

from PyQt4 import uic

def main(folder):
    # pattern = "*.ui"
    # files = os.listdir(folder)
    # files_found = fnmatch.filter(files, pattern)
    uic.compileUiDir(folder,recurse=False, execute=True)



if __name__=="__main__":
    folder = os.getcwd()
    main(folder)
