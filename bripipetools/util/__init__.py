"""
Includes convenience methods related to handling and manipulating
strings (``util.strings``), file paths (``util.files``), as well as
user interactions via the command line (``util.ui``). Methods are used
throughout other modules to streamline common operations.
"""
from .strings import (matchdefault, to_camel_case, to_snake_case)
from .files import (locate_root_folder, swap_root)
from .ui import (prompt_raw, list_options, input_to_int, input_to_int_list)
