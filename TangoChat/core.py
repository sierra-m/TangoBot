from typing import List
import random
import re


class Concept:
    def __init__(self, name: str, options: List[str]):
        self.name = name.lower()
        self.options = options

    def next(self):
        return random.choice(self.options)

    def render_to(self, template):
        return [template.format(option) for option in self.options]

    def __iter__(self):
        i = 0
        while i < len(self.options):
            yield self.options[i]
            i += 1


class ConceptLibrary:
    def __init__(self, concepts : List[Concept] = []):
        self.concepts = concepts

    def add(self, name: str, options: List[str]):
        self.concepts.append(Concept(name, options))

    def get(self, term):
        term = term.lower()
        for concept in self.concepts:
            if concept.name == term:
                return concept


class Response:
    def __init__(self, choices: List[str]):
        self.choices = choices
        self.iter = 0

    def next(self, concepts: ConceptLibrary):
        choice = self.choices[self.iter]

        self.iter += 1
        if self.iter >= len(self.choices):
            self.iter = 0

        matches = re.findall(r'~([a-z0-9]+)\b', choice, re.I)
        if matches:
            for match in matches:
                valid_concept = concepts.get(match)
                if valid_concept:
                    choice = re.sub('~{}'.format(match), valid_concept.next(), choice, flags=re.I)
                    break  # out of match loop

        return choice


class DialogNode:
    def __init__(self, **kwargs):
        self.triggers = kwargs.get('triggers', [])
        self.response = kwargs.get('response', None)
        self.proposal = kwargs.get('proposal', False)
        self.level = kwargs.get('level', None)
        self.scope = []  # type:List[DialogNode]
        self.parent = None

        self.triggers = [t.lower() for t in self.triggers]

    def triggers_on(self, phrase: str, concepts: ConceptLibrary):
        for node in self.scope:  # type:DialogNode
            if phrase.lower() in node.triggers:
                return node

    def render_triggers(self, concepts: ConceptLibrary):
        possible = []

        for trigger in self.triggers:
            matches = re.findall(r'~([a-z0-9]+)\b', trigger, re.I)
            if matches:
                for match in matches:
                    valid_concept = concepts.get(match)
                    if valid_concept:
                        template = trigger.replace('~{}'.format(match), '{}')
                        possible.extend(valid_concept.render_to(template))
            else:
                possible.append(trigger)

        self.triggers = possible

    def add_node(self, node):
        self.scope.append(node)
