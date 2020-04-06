import re
from core import Concept, ConceptLibrary, Response, DialogNode

rule_pattern = re.compile(r'\s*u\s*(?P<num>[0-9]+)?\s*:\s*\((?P<input>[\[\]a-z0-9\s\"\'~?!.,\-]+)\)\s*?:\s*(?P<pred>[\[\]a-z0-9\s\"\'~?!.,\-]+)\s*$', re.I)

proposal_pattern = re.compile(r'\s*&\s*p\s*:\s*(?P<pred>[\[\]a-z0-9\s\"\'~?!.,\-]+)\s*$', re.I)

concept_pattern = re.compile(r'\s*~\s*(?P<name>[a-z0-9]+)\s*:\s*(?P<pred>[\[\]a-z0-9\s\"\'~?!.,\-]+)\s*$', re.I)

token_pattern = re.compile(r'("[^"]+"|[^\s"]+)')

list_pattern = re.compile(r'\s*\[\s*([\[\]a-z0-9\s\"\'~?!.,\-]+)\s*\]\s*')

single_token_pattern = re.compile(r'\s*([\w\"\'~?!.,\-]+)\s*$', re.I)


def get_int(thing):
    try:
        return int(thing)
    except:
        return None


class Parser:
    def __init__(self, file_text: str):
        self.raw = file_text

        segments = file_text.split('\n')

        # root can be null except for scope
        self.root = DialogNode(level=-1)
        current_node = self.root
        parent_node = None

        self.concept_lib = ConceptLibrary()

        self.proposal = None

        for line, segment in enumerate(segments):
            # Ignore comments
            if '#' in segment:
                if segment.startswith('#'):
                    continue
                else:
                    segment = segment.split('#', 1)[0]

            # Matching a rule pattern
            match = re.match(rule_pattern, segment)
            if match:
                # Build new rule
                new_rule = match.groupdict()
                level = get_int(new_rule['num']) or 0
                triggers = self.get_options(new_rule['input'])
                if not triggers:
                    self.error('Found no user input content', segment, line)

                response_opts = self.get_options(new_rule['pred'])
                if not response_opts:
                    self.error('Found no response content', segment, line)

                response = Response(response_opts)

                new_node = DialogNode(triggers=triggers, response=response, level=level)

                if level > current_node.level:
                    if (level - current_node.level) > 1:
                        self.error(
                            "Can't add level u{} before u{}".format(level or '', current_node.level+1 or ''),
                            segment,
                            line)
                    else:
                        current_node.add_node(new_node)
                        new_node.parent = current_node
                        current_node = new_node
                else:
                    # Traverse up tree till node with scope level is found or root
                    while current_node.level > level and current_node.level > -1:
                        current_node = current_node.parent

                    current_node.add_node(new_node)
                    new_node.parent = current_node
                    current_node = new_node

            else:
                # Concept matching
                match = re.match(concept_pattern, segment)
                if match:
                    # Build new concept
                    new_concept = match.groupdict()
                    name = new_concept['name']
                    options = self.get_options(new_concept['pred'])
                    if not options:
                        self.error('No options found for concept', segment, line)

                    self.concept_lib.add(name, options)
                else:
                    # Proposal matching
                    match = re.match(proposal_pattern, segment)
                    if match:
                        if self.proposal:
                            self.error('Proposal count exceeds 1', segment, line)

                        # Build new proposal
                        new_proposal = match.groupdict()
                        options = self.get_options(new_proposal['predicate'])

                        response = Response(options)
                        new_node = DialogNode(response=response, level=0, proposal=True)

                        self.proposal = new_node
                        self.root.add_node(new_node)
                        new_node.parent = self.root
                        current_node = new_node

                    else:
                        self.error('Unrecognized pattern', segment, line)

            print(match.groupdict())

    @staticmethod
    def error(text: str, segment: str, line: int):
        segment = ' '.join(segment.split())  # Remove surrounding whitespace
        print('Parser Error (line {}): {} at "{}"'.format(line, text, segment))
        exit(1)

    @staticmethod
    def get_options(text):
        match = re.match(list_pattern, text)
        if match:
            return re.findall(token_pattern, match.group(1))
        else:
            return [' '.join(text.split())]


