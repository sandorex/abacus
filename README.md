# Abacus
[![PyPI version](https://badge.fury.io/py/abacus-icalc.svg)](https://badge.fury.io/py/abacus-icalc)

*Powerful interactive calculator made in Python using Python with Python support*

## Installation
To install Abacus run the following command with pip installed

```shell
python -m pip install abacus-icalc[ipython]
```

### Latest
Another option is to install the latest version from master branch
```shell
python -m pip install abacus-icalc[ipython]@https://github.com/sandorex/abacus.git
```

For other branches append `@branch` to the url like so
```shell
python -m pip install abacus-icalc[ipython]@git+https://github.com/sandorex/abacus.git@branch
```

## IPython or not
IPython is currently recommended way of using Abacus as it has all the features, i am planning making many features available without it too but it requires a lot of effort and time so it will have to wait

## Project goals
The project is meant to be an interactive algebra calculator with scripting support

There are plenty of things i wanted to add (or may add in the future) like:
- Unit support / conversion, this is kinda supported using sympy units but is not very intuitive and easy to use
- GUI, this is planned but i am putting it off as its not a priority

## Python support
Python is considered first class citizen and should always be supported in Abacus, if you encounter python code that doesn't run cause of syntax errors that is a bug and please report it

## Alternatives
TODO
