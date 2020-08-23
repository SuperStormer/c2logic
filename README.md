# c2logic

Compiles C code to Mindustry logic.

# Usage

`python3 -m c2logic filename -O optimization_level`

where `filename` is a string and `optimization_level` is an int

See [examples](./examples) for API sample usage.

# Documentation

TODO

See `include/mindustry.h`.

# Unsupported Features

-   drawing
-   getlink
-   memory cell read/write
-   do-while
-   continue
-   goto
-   actual functions
-   structs
-   enums

Some of these features may be worked around using `_asm()`.
