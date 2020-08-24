#ifndef MINDUSTRY_H
#define MINDUSTRY_H
struct MindustryObject {};
// void _asm(char* code);
// builtin instructions
void print(char* s);
void printd(double s);
void printflush(struct MindustryObject msg_block);

struct MindustryObject radar(struct MindustryObject obj, char* target1, char* target2,
							 char* target3, char* sort, double index);
double sensor(struct MindustryObject obj, char* prop);
void enable(struct MindustryObject obj, double enabled);
void shoot(struct MindustryObject obj, double x, double y, double shoot);
void end();
// builtin binary operators
double pow(double x, double y);
double max(double x, double y);
double min(double x, double y);
double atan2(double x, double y);
double dst(double x, double y);
// builtin unary operators
double abs(double x);
double log(double x);
double log10(double x);
double sin(double x);
double cos(double x);
double tan(double x);
double floor(double x);
double ceil(double x);
double sqrt(double x);
double rand(double x);
#endif