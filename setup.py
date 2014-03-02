from distutils.core import setup, Extension

setup(
        name='AM2302-rpi',
        version='1.0',
        description='Drive an AM2302 temperature sensor with a raspberry pi.',
        author='Cameron Little',
        author_email='cameron@camlittle.com',
        url='https://github.com/apexskier/AM2302',
        py_modules=['temp_humid_sensor'],
        ext_modules=[Extension(
                'temp_humid_sensor',
                ['temp_humid_sensor.c'],
                libraries=['bcm2835']
            )]
    )
