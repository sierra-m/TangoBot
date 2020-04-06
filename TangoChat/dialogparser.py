import re
from core import Concept, ConceptLibrary, Response, DialogNode

rule_pattern = re.compile(r'\s*u\s*(?P<num>[0-9]+)?\s*:\s*\((?P<input>[\[\]a-z0-9\s\"\'~?!.,\-]+)\)\s*?:\s*(?P<pred>[\[\]a-z0-9\s\"\'~?!.,\-]+)\s*$', re.I)

proposal_pattern = re.compile(r'\s*&\s*p\s*:\s*(?P<pred>[\[\]a-z0-9\s\"\'~?!.,\-]+)\s*$', re.I)

concept_pattern = re.compile(r'\s*~\s*(?P<name>[a-z0-9]+)\s*:\s*(?P<pred>[\[\]a-z0-9\s\"\'~?!.,\-]+)\s*$', re.I)

token_pattern = re.compile(r'("[^"]+"|[^\s"]+)')


class Parser:
    def __init__(self, file_text: str):
        self.raw = file_text

        segments = file_text.split('\n')

        # root can be null except for scope
        self.root = DialogNode(level=-1)

        for line, segment in enumerate(segments):
            if '#' in segment:
                if segment.startswith('#'):
                    continue
                else:
                    segment = segment.split('#', 1)[0]

            match = re.match(rule_pattern, segment)
            if not match:
                match = re.match(concept_pattern, segment)
                if not match:
                    match = re.match(proposal_pattern, segment)
                    if not match:
                        self.error('Unrecognized pattern', segment, line)
                        exit(1)

            print(match.groupdict())

    @staticmethod
    def error(text: str, segment: str, line: int):
        segment = ' '.join(segment.split())  # Remove surrounding whitespace
        print('Parser Error (line {}): {} at "{}"'.format(line, text, segment))


