#ifndef MINDUSTRY_H
#define MINDUSTRY_H
struct MindustryObject {};
void _asm(char* code);
void print(char* s);
void printd(double s);
void printflush(struct MindustryObject);

struct MindustryObject radar(struct MindustryObject obj, char* target1, char* target2,
							 char* target3, char* sort, double index);
double sensor(struct MindustryObject obj, char* prop);
void enable(struct MindustryObject obj, double enabled);
void shoot(struct MindustryObject obj, double x, double y, double shoot);
void end();
#endif