# CIR Sale Sniper


[![pypi](https://img.shields.io/pypi/v/cir-sniper.svg)](https://pypi.org/project/cir-sniper/)
[![python](https://img.shields.io/pypi/pyversions/cir-sniper.svg)](https://pypi.org/project/cir-sniper/)
[![Build Status](https://github.com/michaeltoohig/cir-sniper/actions/workflows/dev.yml/badge.svg)](https://github.com/michaeltoohig/cir-sniper/actions/workflows/dev.yml)
[![codecov](https://codecov.io/gh/michaeltoohig/cir-sniper/branch/main/graphs/badge.svg)](https://codecov.io/github/michaeltoohig/cir-sniper)



A bespoke J2Store sale sniper.


## TODO

* Use specified wishlist item quantity values to refrain from adding additional items to cart when quantity is reached from repeated runs of the script
* Use quantity value automatically 

## Usage

Activate the local environment (gives access to installed packages required for this tool to work)

    poetry shell

For help, run:

    poetry run cir-sniper --help

## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:

    cd cir-sniper
    poetry shell
    poetry install -E test

To run the tests:

    pytest

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [michaeltoohig/click-cli-boilerplate](https://github.com/michaeltoohig/click-cli-boilerplate) project template.
