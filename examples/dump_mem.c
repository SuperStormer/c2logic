#include "c2logic/builtins.h"
// prints the memory of a memory cell separated by spaces in a 8x8 grid
extern struct MindustryObject message1;
extern struct MindustryObject cell1;
void main(void) {
	for (int y = 0; y < 8; y++) {
		for (int x = 0; x < 8; x++) {
			printd(read(cell1, y * 8 + x));
			print(" ");
		}
		print("\n");
	}
	printflush(message1);
}
