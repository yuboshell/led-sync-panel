// Simplest blink — drives one external LED on GP15.
// Circuit: GP15 (pin 20) -> 240 ohm -> LED long leg(+); LED short leg(-) -> jumper -> GND.
#include "pico/stdlib.h"

#define LED 15            // GP15

int main() {
    gpio_init(LED);
    gpio_set_dir(LED, GPIO_OUT);
    while (true) {
        gpio_put(LED, 1);
        sleep_ms(250);
        gpio_put(LED, 0);
        sleep_ms(250);
    }
}
