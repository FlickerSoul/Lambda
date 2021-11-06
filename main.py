#!/usr/bin/env python3

# CSCI 384

import sys
import pathlib
from pprint import pprint

from parser import Definition


def eval_all(src: str) -> None:
    df = Definition(src)
    print('parsed: ')
    pprint(df.parse())
    print('tokens: ')
    print(df.tokens)
    print('main: ')
    pprint(df.formatted_main)


def read_and_eval(file_name: pathlib.Path) -> None:
    with open(file_name, 'r') as f:
        print(f'file_name: {file_name}')
        eval_all(f.read())
        print('===========')
        print()


def main() -> None:
    if len(sys.argv) > 1:
        for file_name in sys.argv[1:]:
            file_path = pathlib.Path(file_name)
            if file_path.is_dir():
                for src_file_path in file_path.glob('*.lc'):
                    read_and_eval(src_file_path)
            elif file_path.is_file():
                assert file_path.name.endswith('.lc')
                read_and_eval(file_path)
            else:
                raise ValueError('Unsupported file type as input. Only accepts folders or files.')
    else:
        print("Enter an expression:")
        eval_all(input())


if __name__ == '__main__':
    main()
