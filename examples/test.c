#include "mindustry.h"
extern struct MindustryObject message1;
extern struct MindustryObject swarmer1;
extern struct MindustryObject conveyor1;
void main(void) {
	/*double i = 0;
	while (i < 10) {
		print(i);
		printflush(message1);
		i += 1;
	}*/
	struct MindustryObject player = radar(swarmer1, "player", "any", "any", "distance", 0);
	double x = sensor(player, "x");
	double y = sensor(player, "y");
	printd(x);
	print("\n");
	printd(y);
	printflush(message1);
	enable(conveyor1, x < 10);
	shoot(swarmer1, 0, 0, x > 10);
}