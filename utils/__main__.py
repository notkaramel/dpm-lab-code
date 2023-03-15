from . import wifi
from .__init__ import setup
import sys

debug = False
help_msg = """
Running "python3 -m utils" allows you to perform some actions
-------------------------------------------------------------
"python3 -m utils wifi"  - Starts a program to edit your robot's wifi networks

"python3 -m utils setup" - Starts a program to install Python Packages in nearby lib/ folders
                           valid lib folders are relative to the utils folder:
                           - utils/lib
                           - utils/../lib

"python3 -m utils setup true" - Only lists the packages it would install. Doesn't install.

"""

if len(sys.argv) > 2:
    debug = bool(sys.argv[2])

if len(sys.argv) == 1:
    print(help_msg)
elif sys.argv[1] == "wifi":
    wifi.main()
elif sys.argv[1] == "setup":
    print()
    code = setup(debug)
    if code == 0:
        if debug:
            print("+++ Installation Would Be Successful")
        else:
            print("+++ Installation Was Successful")
    print()
else:
    print(help_msg)