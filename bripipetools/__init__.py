__author__ = 'James A. Eddy; Mario G. Rosasco'
__email__ = 'james.a.eddy@gmail.com; m.g.rosasco@gmail.com'
__version__ = '0.6.0'

from . import util

# parsing depends on util
from . import parsing

from . import io

# model depends on util, parsing
from . import model

# database depends on util, model
from . import database

# qc depends on io
from . import qc

# annotation depends on util, parsing, io, model, database, qc
from . import annotation

# dbification depends on util, database, annotation
from . import dbification

# postprocessing depends on util, parsing, io
from . import postprocessing

from . import monitoring

from . import submission
