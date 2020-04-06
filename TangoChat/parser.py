import sys
import re


if len(sys.argv) < 2:
    raise ValueError('Please supply the filename.')


with open(sys.argv[1], 'r') as f:
    text = f.read()

segments = text.split('\n')

rule_pattern = re.compile(r'\s*u\s*(?P<num>[0-9]+)\s*:\s*\((?P<input>[\[\]a-z0-9\s\"\'~?!.\-]+)\)\s*?:\s*(?P<pred>[\[\]a-z0-9\s\"\'~?!.\-]+)\s*$', re.I)

proposal_pattern = re.compile(r'\s*&\s*p\s*:\s*(?P<pred>[\[\]a-z0-9\s\"\'~?!.\-]+)\s*$', re.I)

concept_pattern = re.compile(r'\s*~\s*(?P<name>[a-z0-9]+)\s*:\s*(?P<pred>[\[\]a-z0-9\s\"\'~?!.\-]+)\s*$', re.I)

token_pattern = re.compile(r'("[^"]+"|[^\s"]+)')


