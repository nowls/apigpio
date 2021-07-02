from setuptools import setup, find_packages


with open('README.rst', 'r') as f:
    README = f.read()


setup(name='apigpio-nowls',
      version='0.0.6',
      description='asyncio-based python client for pigpiod',
      long_description=README,
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",

          "License :: OSI Approved :: MIT License",

          "Operating System :: OS Independent",
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',

          "Topic :: System :: Hardware :: Hardware Drivers",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      author='Pierre Rust',
      author_email='pierre.rust@gmail.com',
      url='https://github.com/nowls/apigpio',
      keywords=['gpio', 'pigpio', 'asyncio', 'raspberry'],
      packages=find_packages()
      )
