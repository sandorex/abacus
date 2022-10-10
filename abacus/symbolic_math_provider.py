# this is probably not the solution

try:
    import symengine
except ImportError:
    # define it as None so it can be checked for
    symengine = None

# lazy load sympy
from .util import lazy_sympy as sympy
