# c2logic

Compiles C code to Mindustry logic. Still in beta, so compiled output may not be fully optimized.

# Installation

`pip install git+https://github.com/SuperStormer/c2logic`

# Usage

Run the command line tool using:

`c2logic filename -O optimization_level`

where `filename` is a string and `optimization_level` is an optional integer
Optimization Level:

0. completely unoptimized
1. the default
    - modify variables without using a temporary
2. turns on some potentially unsafe optimizations
    - augmented assignment and pre/postincrement/decrement don't modify \_\_rax
    - returning from main becomes equivalent to `end`

Locals are rewritten as _<varname>_<func_name>. Globals are unchanged.

Special Variables:

-   \_\_rax: similar to x86 rax
-   \_\_rbx: stores left hand side of binary ops to avoid clobbering by the right side
-   \__retaddr_\*: stores return address of func call

When developing your script, you can include `c2logic/builtins.h` located in the python include directory(location depends on system, mine is at `~/.local/include/python3.8/`)

See [examples](./examples) for API sample usage.

# Documentation

See `include/builtins.h` for API definitions.

# Unsupported Features

-   drawing
-   getlink
-   memory cell read/write
-   actual functions
-   structs
-   enums

Some of these features may be worked around using `asm()`.
