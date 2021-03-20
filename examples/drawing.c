#include "c2logic/builtins.h"
extern struct MindustryObject display1;
void main(void) {
	drawcolor(128, 128, 0);
	drawpoly(40, 40, 6, 10, 0);
	drawcolor(0, 128, 128);
	drawpoly(40, 40, 3, 10, 180);
	drawflush(display1);
}
