from .core.standalones.classes.nil import Nil
from .core.synamic import Synamic


import builtins

# add Nil to builtins
builtins.Nil = Nil
