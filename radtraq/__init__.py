from . import proc
from . import utils
from . import plotting
from . import tests
from ._version import get_versions

# Version for source builds
vdict = get_versions()
__version__ = vdict["version"]
