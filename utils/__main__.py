from . import wifi
from .__init__ import setup
import sys

debug = False

if len(sys.argv) == 1:
    exit()
if len(sys.argv) > 2:
    debug = bool(sys.argv[2])

if sys.argv[1] == "wifi":
    wifi.main()
elif sys.argv[1] == "setup":
    setup(debug)