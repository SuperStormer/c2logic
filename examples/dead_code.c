#include "c2logic/builtins.h"
// expected output on -O2 is only d should be in the compiled output
void a(void);
void b(void);
void c(void);
void d(void);
void a(void) {
	print("a");
	b();
}
void b(void) {
	print("b");
	c();
	a();
	d();
}
void c(void) {
	print("c");
}
void d(void) {
	print("d");
}
void main(void) {
	d();
}
