import os
import sys

python = sys.executable
packages_names = ' '.join(['simpleaudio', 'pygame'])

def setup():
    if 'utils' in os.listdir() and os.path.isdir('utils'):
        os.chdir(os.path.join('utils', 'lib'))
        
        packages = ' '.join(os.listdir())
        
        code = os.system(f'{python} -m pip install {packages}')
        if code != 0:
            print('+++ Local Installation Failed. Attempting Install from the Internet.')
            os.system(f'{python} -m pip install {packages_names}')

