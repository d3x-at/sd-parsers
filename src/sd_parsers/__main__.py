import sys

from . import ParserManager

p = ParserManager()

if __name__ == "__main__":
    for filename in sys.argv[1:]:
        print(p.parse(filename))
