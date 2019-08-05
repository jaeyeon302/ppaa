import sys
import os

CURRENT_DIR = os.getcwd()
sys.stdout = sys.stderr
sys.path.insert(0,CURRENT_DIR)

from ppap import create_app
application = create_app()
