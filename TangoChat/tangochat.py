import sys
from dialogparser import Parser
import random


i_dont_know = ["I'm afraid I don't understand", "I'm not sure what you mean", "Please rephrase that"]

if len(sys.argv) < 2:
    raise ValueError('Please supply the filename.')


with open(sys.argv[1], 'r') as f:
    text = f.read()

parser = Parser(text)
# parser.print_tree()
# parser.print_concepts()

print('Beginning chat. Type "exit" to leave.')

if parser.proposal:
    print('(Tango): {}'.format(parser.proposal.next_response(parser.concept_lib)))
    current_node = parser.proposal
else:
    current_node = parser.root

while True:
    print('You: ', end='')
    phrase = input().replace('\n', '')

    if phrase == 'exit':
        print('(Tango): Goodbye!')
        break

    found_match = parser.get_trigger_match(phrase, current_node)

    if found_match:
        current_node = found_match
        print('(Tango): {}'.format(found_match.next_response(parser.concept_lib)))
    else:
        print('(Tango): {}'.format(random.choice(i_dont_know)))
