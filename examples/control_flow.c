#include "mindustry.h"
extern struct MindustryObject message1;
void main(void) {
	double i = 0;
	while (i < 10) {
		if (i == 3) {
			print("is 3");
		} else {
			print("not 3");
		}
	}
	printd(i);
	print("\n");
	printflush(message1);
}