# c2logic

Compiles C code to Mindustry logic. Still in beta, so compiled output may not be fully optimized. Requirements are the `pycparser` package and the C preprocessor (`cpp`).

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
2. more optimizations
    - remove uncalled functions
    - constant folding
3. turns on some potentially unsafe optimizations
    - augmented assignment and pre/postincrement/decrement don't modify `__rax`
    - returning from main becomes equivalent to `end`

Locals are rewritten as `_<varname>_<func_name>`. Globals are unchanged.

Special Variables:

-   `__rax`: similar to x86 rax
-   `__rbx`: stores left hand side of binary ops to avoid clobbering by the right side
-   `__retaddr__<func_name>`: stores return address of func call

When writing your code, you must include `c2logic/builtins.h`, which is located in the python include directory (location depends on system, mine is at `~/.local/include/python3.8/`).
A quick way to find this is `python3 -c "from c2logic.compiler import get_include_path; print(get_include_path())"` (use `python` if you are using windows).

See [include/builtins.h](./include/builtins.h) for API definitions and [examples](./examples) for API sample usage.

# Supported Features

-   all Mindustry instructions as of BE 20879 with single data returns (nothing that sets both outx and outy for example)
-   all C control flow structures except switch
-   functions
-   local/global variables

# Unsupported Features

-   defining global variables outside of functions - define it in main
-   recursive calls - use iteration
-   structs - split it into multiple variables
-   enums - use an int plus macros
-   block scoped variables - just use locals
-   typedefs - use macros
-   pointers - don't use them
-   switch - use if-else chains
