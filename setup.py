from distutils.core import setup, Extension

setup(
        name='AM2302-rpi',
        version='1.1.2',
        description='Drive an AM2302 temperature sensor with a raspberry pi.',
        author='Cameron Little',
        author_email='cameron@camlittle.com',
        url='https://github.com/apexskier/AM2302',
        py_modules=['am2302_rpi'],
        ext_modules=[Extension(
                'am2302_ths',
                define_macros = [('BCM2708_PERI_BASE', '0x20000000'),
                                 ('GPIO_BASE',         '(BCM2708_PERI_BASE + 0x200000)'),
                                 ('MAXTIMINGS',        100)],
                sources=['am2302_ths.c'],
                library_dirs=['/usr/local/lib'],
                libraries=['bcm2835'],
                include_dirs=['/usr/local/include']
            )]
    )
