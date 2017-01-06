# Python DHT-Raspberry Pi module

This module enables access to the [AM2302 wired digital temperature and
humidity sensor](https://www.adafruit.com/products/393) from a Raspberry Pi.
It's been adapted from [Adafruit's C
code](http://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/software-install).

It may work with both the DHT11 and DHT22 sensors as well, though this is
untested.

Get it with `pip install am2302_rpi`. The [BCM2835 C
Library](http://www.open.com.au/mikem/bcm2835/index.html) is required and the
root user must be used to access the GPIO pins.

## am2302_ths

Both methods return floats, or None if the sensor can't be read. The sensor
can only be read once every few seconds.

### `get_temperature(pin)`

Reads the current temperature from a sensor attached to the specified pin.

### `get_humidity(pin)`

Reads the current humidity from a sensor attached to the specified pin.

## am2302_rpi

This module provides a class *Sensor* which periodically polls the sensor
to keep track of the current temperature without waiting for it.

It has the following methods available.

### `__init__(pin)`

Create a new sensor object instance with `s = am2302_rpi.Sensor(4)`.

### `get(data="temp")`

Get the last read values.

`data`: what data to read. `"temp"` for temperature, `"humid"` for humidity and `"both"` for a tuple of both values.

### `get_last_time()`

Get the time of the last successful read.

### `off()`

Turn the timer off by cancelling it's internal ticker. Make sure you call this
before exiting.


## TODO

Clean up the sensor object properly.
