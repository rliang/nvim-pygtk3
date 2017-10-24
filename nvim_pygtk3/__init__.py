import sys
from .application import NeovimApplication


def main():
    NeovimApplication(__package__, __file__).run(sys.argv[1:])


if __name__ == '__main__':
    main()
