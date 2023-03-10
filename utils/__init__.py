import os
import sys

python = sys.executable
packages_names = ' '.join(['simpleaudio', 'pygame'])

def setup(debug=False):
    """Installs packages on the BrickPi where we expect them to be.
    
    either 
    ./utils/lib
    or
    ./utils/../lib (install packages from the lib folder next to utils/)
    or
    ./lib (install packages from the current folder)
    """
    code = 0

    if os.path.basename(os.getcwd()) == 'utils':
        os.chdir('..') # go to utils directory parent

    cwd = os.getcwd()

    if 'utils' in os.listdir() and 'lib' in os.listdir('utils'):
        os.chdir(os.path.join('utils', 'lib'))
    elif 'lib' in os.listdir():
        os.chdir(os.path.join('lib'))
    
    packages = ' '.join(os.listdir())
    
    print(f"+++ From directory {os.getcwd()}")
    print(f"+++ Attempting install of:\n{packages}")

    if not debug:
        code = os.system(f'{python} -m pip install {packages}')

    if code == 0:
        return

    # In case of failure of other things, try internet-based install
    print('+++ Local Installation Failed. Attempting Install from the Internet.')
    code = os.system(f'{python} -m pip install {packages_names}')

    if code != 0:
        print("+++ ERROR: installation of extra python packages has completely failed")

