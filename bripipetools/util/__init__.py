"""
Includes convenience methods related to handling and manipulating
strings (``util.strings``), file paths (``util.files``), as well as
user interactions via the command line (``util.ui``). Methods are used
throughout other packages to streamline common operations.
"""
from .dicts import (flatten_dict)
from .strings import (matchdefault, matchlastdefault, to_camel_case, to_snake_case)
from .files import (locate_root_folder, swap_root)
