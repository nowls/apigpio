apigpio
=======

apigpio - an asyncio-based python client for pigpio

Fork history:
- Originally forked from https://github.com/PierreRust/apigpio by missionpinball because it is kind of unmaintained.
They added some more feature (I2C) and fixed Python 3.7 support.
- Forked from https://github.com/missionpinball by neildavis. They added support for a few more useful PWM related functions.
- Forked from https://github.com/neildavis/apigpio to add support for waveform functions.

`pigpio <http://abyz.co.uk/rpi/pigpio/pigpiod.html>`_ provides a very 
convenient `pigpiod` daemon which can be used through a pipe or socket interface
to access GPIOs on the Raspberry Pi. 

`apigpio` is a python client library that uses asyncio to access the `pigpiod` 
daemon. It's basically a (incomplete) port of the original python client provided with pigpio.

Installation
============

Not yet on Pypi or available from pip

To install it from sources:
 
::

  git clone https://github.com/nowls/apigpio.git
  cd apigpio
  python3 -m pip install .
    
    
Usage
=====

See the examples in the `samples` directory.
