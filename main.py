#!/usr/bin/env python3

# CSCI 384

import sys
import pathlib
from pprint import pprint
import subprocess
import shutil
from typing import Union, Optional, Tuple

from parser import Definition


def eval_all(src: str) -> Definition:
    """ eval src and print out evaluation result

    :param src: string of source code
    :return: None
    """
    df = Definition(src)
    print('parsed: ')
    pprint(df.parse())
    print('tokens: ')
    print(df.tokens)
    print('main: ')
    pprint(df.formatted_main)

    return df


def read_and_eval(file_name: pathlib.Path) -> Definition:
    """ read files or files in directories and eval them

    :param file_name: a path-like object
    :return: None
    """
    with open(file_name, 'r') as f:
        print(f'file_name: {file_name}')
        df = eval_all(f.read())

    return df


_SML_RD_FN = 'norReduce'


def write_main(df: Definition, file_name: pathlib.Path, verbose: bool = False) -> tuple:
    out_path = pathlib.Path(f'{file_name}.out')
    sml_out_path = pathlib.Path(f'{file_name}.sml')
    with open(out_path, 'w') as f:
        f.write(str(df.formatted_main))
    with open(sml_out_path, 'w') as f:
        f.write(f'val main_ = {_SML_RD_FN} ({df.formatted_main}) {"true" if verbose else "false"};')

    return out_path, sml_out_path


_SML_SUPPORT_CODE = pathlib.Path('reducer.sml')

with open(_SML_SUPPORT_CODE, 'r') as _sml_f:
    _SUPPORT_CODE = _sml_f.read()


def run_sml(sml: Union[pathlib.Path, str]) -> Optional[str]:
    has_sml = shutil.which('sml')
    has_sosml = shutil.which('sosml')

    sml_bin = has_sml or has_sosml or None

    if sml_bin:
        if isinstance(sml, str):
            _SML_SRC = sml
        elif isinstance(sml, pathlib.Path):
            with open(sml, 'r') as src_f:
                _SML_SRC = src_f.read()
        else:
            raise Exception('Unknown sml src data')

        s = subprocess.Popen([sml_bin], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        output, _ = s.communicate((_SUPPORT_CODE + _SML_SRC).encode())
    else:
        print('no sml compiler')
        return None

    return output.decode()


def extract_sml_output(sml_output: str) -> Optional[Tuple]:
    sl = list(i for i in sml_output.split('\n') if i)
    r_index = tuple(i for i in range(len(sl)) if sl[i].startswith('val norReduce'))[0] + 1
    o_index = tuple(i for i in range(r_index, len(sl)) if sl[i].startswith('val main_'))[0]
    if o_index < len(sl):
        output = '\n'.join(
            sl[r_index:-1]
        )
        result = '\n'.join(sl[o_index:])
        return output, result
    else:
        return None


def run_all(src_file_path, verbose: bool = False):
    _, sml_code_path = write_main(read_and_eval(src_file_path), src_file_path, verbose)
    out = run_sml(sml_code_path)
    stdout, res = extract_sml_output(out)

    if verbose:
        print('verbose: ')
        print(stdout)
    print('reduced result: ')
    print(res)
    print('================')
    print()


def main() -> None:
    """ main function that read command line input or arguments

    :return: None
    """
    if len(sys.argv) > 1:
        for file_name in sys.argv[1:]:
            file_path = pathlib.Path(file_name)
            if file_path.is_dir():
                for src_file_path in file_path.glob('*.lc'):
                    run_all(src_file_path)
            elif file_path.is_file():
                run_all(file_path)
            else:
                raise ValueError('Unsupported file type as input. Only accepts folders or files.')
    else:
        print("Enter an expression:")
        eval_all(input())


if __name__ == '__main__':
    main()
