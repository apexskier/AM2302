CC=gcc
CFLAGS=-l bcm2835 -Wall

temp_humid_sensor: temp_humid_sensor.o
	$(CC) temp_humid_sensor.o $(CFLAGS) -o temp_humid_sensor
