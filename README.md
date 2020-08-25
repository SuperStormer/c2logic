# c2logic

Compiles C code to Mindustry logic. Still in beta, so compiled output may not be fully optimized.

# Installation

`pip install git+https://github.com/SuperStormer/c2logic`

# Documentation

Run the command line tool using:

`c2logic filename -O optimization_level`

where `filename` is a string and `optimization_level` is an optional integer.

Optimization Level:

0. completely unoptimized.
1. the default
    - modify variables without using a temporary
2. turns on some potentially unsafe optimizations
    - augmented assignment and pre/postincrement/decrement don't modify `__rax`
    - returning from main becomes equivalent to `end`

Locals are rewritten as `_<varname>_<func_name>`. Globals are unchanged.

Special Variables:

-   `__rax`: similar to x86 rax
-   `__rbx`: stores left hand side of binary ops to avoid clobbering by the right side
-   `__retaddr__<func_name>`: stores return address of func call

When writing your code, you must include `c2logic/builtins.h`, which is located in the python include directory (location depends on system, mine is at `~/.local/include/python3.8/`).

See [include/builtins.h](./include/builtins.h) for API definitions and [examples](./examples) for API sample usage.

# Supported Features

-   all Mindustry instructions as of BE
-   all control flow structures except goto
-   functions
-   local/global variables

# Unsupported Features

-   structs - split it into multiple variables
-   enums - use an int plus macros
-   block scoped variables - just use locals
-   typedefs - use macros
-   pointers - don't use them
-   goto - don't use it
