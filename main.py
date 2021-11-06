
# CSCI 384
import sys
from pprint import pprint

from parser import Definition


def eval_all(src: str):
    df = Definition(src)
    print('parsed: ')
    pprint(df.parse())
    print('tokens: ')
    pprint(df.tokens)
    print('main: ')
    pprint(df.formatted_main)
    print('defs: ')
    pprint(df.defs)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        for file_name in sys.argv[1:]:
            with open(file_name, 'r') as f:
                print(f'file_name: {file_name}')
                eval_all(f.read())
                print('===========')
                print()
    else:
        print("Enter an expression:")
        eval_all(input())
