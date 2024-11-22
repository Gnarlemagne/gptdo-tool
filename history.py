import os
import readline

from . import ROOT
histfile = os.path.join(ROOT, "history.txt")
try:
    readline.read_history_file(histfile)
    # default history len is -1 (infinite), which may grow unruly
    readline.set_history_length(1000)
except IOError:
    pass

import atexit
atexit.register(readline.write_history_file, histfile)
del os, histfile