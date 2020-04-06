import sys
from dialogparser import Parser

if len(sys.argv) < 2:
    raise ValueError('Please supply the filename.')


with open(sys.argv[1], 'r') as f:
    text = f.read()

tango_parser = Parser(text)

