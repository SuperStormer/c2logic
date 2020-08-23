# c2logic

Compiles C code to Mindustry logic. Still in beta, so compiled output may not be fully optimized.

# Usage

`python3 -m c2logic filename -O optimization_level`

where `filename` is a string and `optimization_level` is an integer.

See [examples](./examples) for API sample usage.

# Documentation

See `include/mindustry.h` for API definitions.

# Unsupported Features

-   drawing
-   getlink
-   memory cell read/write
-   actual functions
-   structs
-   enums

Some of these features may be worked around using `asm()`.
