#include "c2logic/builtins.h"
extern struct MindustryObject message1;
void a(int i) {
	for (int j = 0; j < 4; j++) {
		printd(i + j);
		print("\n");
	}
}
void main(void) {
	for (int i = 0; i < 4; i++) {
		a(i);
	}
	printflush(message1);
}
