# c2logic

Compiles C code to Mindustry logic. Still in beta, so compiled output may not be fully optimized.

# Installation

`pip install git+https://github.com/SuperStormer/c2logic`

# Usage

Run the command line tool using:

`c2logic filename -O optimization_level`

where `filename` is a string and `optimization_level` is an integer.

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
