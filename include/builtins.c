struct MindustryObject {};
// builtin instructions
void print(char* s) {
	asm("print {s}");
}
void printd(double s) {
	asm("print {s}");
}
void printflush(struct MindustryObject message) {
	asm("printflush {message}");
}
struct MindustryObject radar(struct MindustryObject obj, char* target1, char* target2,
							 char* target3, char* sort, double index) {
	asm("radar {target1} {target2} {target3} {sort} {obj} {index} {dest}");
}
double sensor(struct MindustryObject obj, char* prop) {
	asm("sensor {dest} {obj} @{prop}");
}
void enable(struct MindustryObject obj, double enabled) {
	asm("control enabled {obj} {enabled} 0 0 0");
}
void configure(struct MindustryObject obj, char* configure) {
	asm("control configure {obj} {configure} 0 0 0");
}
void setcolor(struct MindustryObject obj, double r, double g, double b) {
	asm("control color {obj} {r} {g} {b} 0");
}
void shoot(struct MindustryObject obj, double x, double y, double shoot) {
	asm("control shoot {obj} {x} {y} {shoot} 0");
}
void shootp(struct MindustryObject obj, double unit, double shoot) {
	asm("control shootp {obj} {unit} {shoot} 0 0");
}
struct MindustryObject get_link(double index) {
	asm("getlink {dest} {index}");
}
double read(struct MindustryObject cell, double index) {
	asm("read {dest} {cell} {index}");
}
void write(double val, struct MindustryObject cell, double index) {
	asm("write {val} {cell} {index}");
}
void drawclear(double r, double g, double b) {
	asm("draw clear {r} {g} {b}");
}
void drawcolor(double r, double g, double b, double a) {
	asm("draw color {r} {g} {b} {a}");
}
void drawstroke(double width) {
	asm("draw stroke {width}");
}
void drawline(double x1, double y1, double x2, double y2) {
	asm("draw line {x1} {y1} {x2} {y2}");
}
void drawrect(double x, double y, double w, double h) {
	asm("draw rect {x} {y} {w} {h}");
}
void drawlinerect(double x, double y, double w, double h) {
	asm("draw lineRect {x} {y} {w} {h}");
}
void drawpoly(double x, double y, double sides, double radius, double rotation) {
	asm("draw poly {x} {y} {sides} {radius} {rotation}");
}
void drawlinepoly(double x, double y, double sides, double radius, double rotation) {
	asm("draw linePoly {x} {y} {sides} {radius} {rotation}");
}
void drawtriangle(double x1, double y1, double x2, double y2, double x3, double y3) {
	asm("draw triangle {x1} {y1} {x2} {y2} {x3} {y3}");
}
void drawimage(double x, double y, char* image, double size, double rotation) {
	asm("draw image {x} {y} {image} {size} {rotation} 0");
}

void drawflush(struct MindustryObject display) {
	asm("drawflush {display}");
}
void end() {
	asm("end");
}
// unit commands (not complete; don't know how to return multiple values)
void ubind(char* type) {
	asm("ubind @{type}");
}
void unit_move(double x, double y) {
	asm("ucontrol move {x} {y} 0 0 0");
}
void unit_idle() {
	asm("ucontrol idle 0 0 0 0 0");
}
void unit_stop() {
	asm("ucontrol stop 0 0 0 0 0");
}
void unit_approach(double x, double y, double radius) {
	asm("ucontrol approach {x} {y} {radius} 0 0");
}
void unit_boost(double enable) {
	asm("ucontrol boost {enable} 0 0 0 0");
}
void unit_pathfind() {
	asm("ucontrol pathfind 0 0 0 0 0");
}
void unit_target(double x, double y, double shoot) {
	asm("ucontrol target {x} {y} {shoot} 0 0");
}
void unit_targetp(double unit, double shoot) {
	asm("ucontrol targetp {unit} {shoot} 0 0 0");
}
void unit_itemDrop(struct MindustryObject obj, double amount) {
	asm("ucontrol itemDrop {obj} {amount} 0 0 0");
}
void unit_itemTake(struct MindustryObject obj, char* item, double amount) {
	asm("ucontrol itemTake {obj} {item} {amount} 0 0");
}
void unit_payDrop() {
	asm("ucontrol payDrop 0 0 0 0 0");
}
void unit_payTake(double takeUnits) {
	asm("ucontrol payTake {takeUnits} 0 0 0 0");
}
void unit_mine(double x, double y) {
	asm("ucontrol mine {x} {y} 0 0 0");
}
void unit_flag(double value) {
	asm("ucontrol flag {value} 0 0 0 0");
}
void unit_build(double x, double y, char* block, double rotation, char* configure) {
	asm("ucontrol build {x} {y} {block} {rotation} {configure}");
}
double unit_within(double x, double y, double radius) {
	asm("ucontrol within {x} {y} {radius} {dest} 0");
}
struct MindustryObject unit_radar(char* target1, char* target2, char* target3, char* sort, double order) {
	asm("uradar {target1} {target2} {target3} {sort} 0 {order} {dest}");
}
