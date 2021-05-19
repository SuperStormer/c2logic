#ifndef MINDUSTRY_H
#define MINDUSTRY_H
struct MindustryObject {};

// builtin instructions
void print(char* s);
void printd(double s);
void printflush(struct MindustryObject message);

struct MindustryObject radar(struct MindustryObject obj, char* target1, char* target2,
							 char* target3, char* sort, double index);
double sensor(struct MindustryObject obj, char* prop);
void enable(struct MindustryObject obj, double enabled);
void configure(struct MindustryObject obj, char* configure);
void setcolor(struct MindustryObject obj, double r, double g, double b);
void shoot(struct MindustryObject obj, double x, double y, double shoot);
void shootp(struct MindustryObject obj, double unit, double shoot);

struct MindustryObject get_link(double index);
double read(struct MindustryObject cell, double index);
void write(double val, struct MindustryObject cell, double index);

void drawclear(double r, double g, double b);
void drawcolor(double r, double g, double b, double a);
void drawstroke(double width);
void drawline(double x1, double y1, double x2, double y2);
void drawrect(double x, double y, double w, double h);
void drawlinerect(double x, double y, double w, double h);
void drawpoly(double x, double y, double sides, double radius, double rotation);
void drawlinepoly(double x, double y, double sides, double radius, double rotation);
void drawtriangle(double x1, double y1, double x2, double y2, double x3, double y3);
void drawimage(double x, double y, char* image, double size, double rotation);
void drawflush(struct MindustryObject display);

void end();

// unit commands (not complete; don't know how to return multiple values)
void ubind(char* type);
void unit_move(double x, double y);
void unit_idle();
void unit_stop();
void unit_approach(double x, double y, double radius);
void unit_boost(double enable);
void unit_pathfind();
void unit_target(double x, double y, double shoot);
void unit_targetp(double unit, double shoot);
void unit_item_drop(struct MindustryObject obj, double amount);
void unit_item_take(struct MindustryObject obj, char* item, double amount);
void unit_pay_drop();
void unit_pay_take(double takeUnits);
void unit_mine(double x, double y);
void unit_flag(double value);
void unit_build(double x, double y, char* block, double rotation, char* configure);
double unit_within(double x, double y, double radius);
struct MindustryObject unit_radar(char* target1, char* target2, char* target3, char* sort,
								  double order);

// builtin binary operators
double pow(double x, double y);
double max(double x, double y);
double min(double x, double y);
double angle(double x, double y);
double len(double x, double y);
double land(double x, double y);
double idiv(double x, double y);
double strictEqual(void* x, void* y);
double noise(double x, double y);

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
