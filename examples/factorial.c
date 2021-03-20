#include "c2logic/builtins.h"
extern struct MindustryObject message1;
double factorial(int x) {
	if (x < 2) {
		return 1;
	}
	int ret = 1;
	for (int i = 2; i <= x; i++) {
		ret *= i;
	}
	return ret;
}

void main(void) {
	for (int i = 0; i < 10; i++) {
		printd(factorial(i));
		print("\n");
	}
	printflush(message1);
}
