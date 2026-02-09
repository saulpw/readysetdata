import sys

debug = '--debug' in sys.argv

from .utils import *
from .download import *
from .http_unzip import *
from .output import *

for k in list(globals().keys()):
    if k.startswith('parse_'):
        globals()[k.replace('parse_', 'load_')] = globals()[k]
