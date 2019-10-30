from setuptools import setup, find_packages


with open('README.rst', 'r') as f:
    README = f.read()


setup(name='apigpio-mpf',
      version='0.0.3',
      description='asyncio-based python client for pigpiod',
      long_description=README,
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",

          "License :: OSI Approved :: MIT License",

          "Operating System :: OS Independent",
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',

          "Topic :: System :: Hardware :: Hardware Drivers",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      author='Pierre Rust',
      author_email='pierre.rust@gmail.com',
      url='https://github.com/missionpinball/apigpio',
      keywords=['gpio', 'pigpio', 'asyncio', 'raspberry'],
      packages=find_packages()
      )
