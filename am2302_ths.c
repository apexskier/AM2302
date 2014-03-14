#include <Python.h>
//  How to access GPIO registers from C-code on the Raspberry-Pi
//  Example program
//  15-January-2012
//  Dom and Gert
//
//  Modified by Cameron Little 24-January-2014
//  Obtained from http://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/software-install

// Access from ARM Running Linux

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

int read_ths(int data[], int pin) {
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
        return 1;
    } else {
        return 0;
    }
}

static PyObject *ths_humid(PyObject *self, PyObject *args) {
    int pin;
    if (!PyArg_ParseTuple(args, "i", &pin)) return NULL;

    int data[100];
    int ret;
    ret = read_ths(&data[0], pin);
    if (ret < 0) return NULL;
    if (ret == 0) return Py_None;

    // yay!
    float h;
    h = data[0] * 256 + data[1];
    h /= 10;
    return Py_BuildValue("f", h);
}

static PyObject *ths_temp(PyObject *self, PyObject *args) {
    int pin;
    if (!PyArg_ParseTuple(args, "i", &pin)) return NULL;

    int data[100];
    int ret;
    ret = read_ths(&data[0], pin);
    if (ret < 0) return NULL;
    if (ret == 0) return Py_None;

    // yay!
    float f;
    f = (data[2] & 0x7F)* 256 + data[3];
    f /= 10.0;
    if (data[2] & 0x80) f *= -1;
    return Py_BuildValue("f", f);
}

static PyMethodDef Am2302_thsMethods[] = {
    {"get_temperature", ths_temp, METH_VARARGS, "Get the temperature from a pin."},
    {"get_humidity", ths_humid, METH_VARARGS, "Get the humidity from a pin."},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initam2302_ths(void) {
    if (!bcm2835_init()) return; // Need the BCM2835 library

    PyObject *m;

    m = Py_InitModule("am2302_ths", Am2302_thsMethods);
    if (m == NULL) return;
}
