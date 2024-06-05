import sys

from . import ParserManager


def main():
    p = ParserManager()

    for filename in sys.argv[1:]:
        print(f"{filename}: {p.parse(filename)}\n")


if __name__ == "__main__":
    main()
