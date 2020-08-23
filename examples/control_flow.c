#include "../include/mindustry.h"
extern struct MindustryObject message1;
void main(void) {
	int i = 0;
	while (i < 10) {
		if (i % 2 == 1) {
			continue;
		}
		printd(i);
		i++;
		if (i == 4) {
			break;
		}
	}
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