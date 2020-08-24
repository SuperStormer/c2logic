#include "c2logic/builtins.h"
/*expected output:
5678
0246
0 is not 3
*/
extern struct MindustryObject message1;
void main(void) {
	int i;
	for (i = 5; i < 9; i++) {
		printd(i);
	}
	i = 0;
	print("\n");
	do {
		if (i % 2 == 1) {
			i++;
			continue;
		}
		printd(i);
		if (i == 6) {
			break;
		}
		++i;
	} while (i < 10);
	print("\n");
	i = 0;
	printd(i);
	if (i == 3) {
		print(" is 3");
	} else {
		print(" is not 3");
	}
	print("\n");
	printflush(message1);
}