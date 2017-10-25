from .window import NeovimWindow
from .application import NeovimApplication

__all__ = ('NeovimWindow', 'NeovimApplication')


def main():
    import sys
    NeovimApplication(__package__, __path__).run(sys.argv[1:])
