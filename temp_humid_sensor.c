//  How to access GPIO registers from C-code on the Raspberry-Pi
//  Example program
//  15-January-2012
//  Dom and Gert
//
//  Modified by Cameron Little 24-January-2014
//  Obtained from http://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/software-install

// Access from ARM Running Linux

#define BCM2708_PERI_BASE        0x20000000
#define GPIO_BASE                (BCM2708_PERI_BASE + 0x200000) /* GPIO controller */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <dirent.h>
#include <fcntl.h>
#include <assert.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <bcm2835.h>
#include <unistd.h>

#define MAXTIMINGS 100

//#define DEBUG

/* Prototypes */
int readDHT(int pin);

int main(int argc, char **argv)
{
    if (!bcm2835_init()) return 1; // Need the BCM2835 library

    if (argc != 2) {
	    printf("usage: %s GPIOpin#\n", argv[0]);
	    printf("example: %s 4 - Read from GPIO #4\n", argv[0]);
	    return 2;
    }
    int dhtpin = atoi(argv[1]);

    if (dhtpin <= 0) {
        printf("Please select a valid GPIO pin #\n");
        return 3;
    }

    int ret = 0;
    ret = readDHT(dhtpin);
    return ret;
}

int readDHT(int pin) {
    int data[100];

    int counter = 0;
    int laststate = HIGH;
    int i = 0, j = 0;

    // Set GPIO pin to output
    bcm2835_gpio_fsel(pin, BCM2835_GPIO_FSEL_OUTP);

    bcm2835_gpio_write(pin, HIGH);
    usleep(500000);  // 500 ms
    bcm2835_gpio_write(pin, LOW);
    usleep(20000);

    bcm2835_gpio_fsel(pin, BCM2835_GPIO_FSEL_INPT);

    data[0] = data[1] = data[2] = data[3] = data[4] = 0;

    // wait for pin to drop?
    while (bcm2835_gpio_lev(pin) == 1) usleep(1);

    // read data!
    for (i = 0; i < MAXTIMINGS; i++) {
        counter = 0;
        while ( bcm2835_gpio_lev(pin) == laststate) {
            counter++;
            if (counter == 1000) break;
        }
        laststate = bcm2835_gpio_lev(pin);
        if (counter == 1000) break;

        if ((i > 3) && (i % 2 == 0)) {
            // shove each bit into the storage bytes
            data[j / 8] <<= 1;
            if (counter > 200) data[j / 8] |= 1;
            j++;
        }
    }

    if ((j >= 39) && (data[4] == ((data[0] + data[1] + data[2] + data[3]) & 0xFF))) {
        // yay!
        float f, h;
        h = data[0] * 256 + data[1];
        h /= 10;

        f = (data[2] & 0x7F)* 256 + data[3];
        f /= 10.0;
        if (data[2] & 0x80) f *= -1;
        printf("%f,%f", f, h);
        return 0;
    } else {
        printf("err");
        return -1;
    }
}
