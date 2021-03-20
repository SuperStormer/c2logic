#include "c2logic/builtins.h"
extern struct MindustryObject message1;
void main(void) {
	goto b;
a:
	goto e;
b:
	goto d;
c:
	goto a;
d:
	goto c;
e:
	print("end");
	printflush(message1);
}
