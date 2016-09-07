"""
Utility classes and methods for basic operations with strings and files
as well as user interaction.
"""
from .strings import (matchdefault, to_camel_case, to_snake_case)
from .files import (locate_root_folder, swap_root, SystemFile)
from .ui import (prompt_raw, list_options, input_to_int, input_to_int_list)
