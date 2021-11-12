#!/usr/bin/env python3

# CSCI 384
# usage: ./lc.py [-h] [-v] [*.lc files or folders containing *.lc files or nothing to enter cmd input mode]

from __future__ import annotations

import pathlib
from pprint import pprint
import subprocess
import shutil
import argparse
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


# _SML_RD_FN = 'norReduce'
_SML_RD_FN = 'reducer'
_SML_SUPPORT_CODE = pathlib.Path('reducer.sml')
# _SML_SUPPORT_CODE = pathlib.Path('2_reducer.sml')


with open(_SML_SUPPORT_CODE, 'r') as _sml_f:
    _SUPPORT_CODE = _sml_f.read()


def _format_sml_exec_stream(df: Definition, verbose: bool = False) -> str:
    """ format definition into sml executable string

    :param df: parsed lambda definition
    :param verbose: verbose flag
    :return: executable sml terms
    """
    return f'val start_ = ();\n ' \
           f'val main_ = {_SML_RD_FN} ({df.formatted_main}) {"true" if verbose else "false"};'


def write_main(df: Definition, file_name: pathlib.Path, verbose: bool = False) -> tuple:
    """ write definition to the files

    :param df: parsed lambda definition
    :param file_name: file name to be written to
                      <file_name>.out is the parsed definition
                      <file_name>.sml is the sml executable of the parsed definition
    :param verbose: verbose flag
    :return: the Path object for .out and .sml files
    """
    out_path = pathlib.Path(f'{file_name}.out')
    sml_out_path = pathlib.Path(f'{file_name}.sml')
    with open(out_path, 'w') as f:
        f.write(str(df.formatted_main))
    with open(sml_out_path, 'w') as f:
        f.write(_format_sml_exec_stream(df, verbose))

    return out_path, sml_out_path


def run_sml(sml: Union[pathlib.Path, str]) -> Optional[str]:
    """ run sml using sml/nj or sosml

    :param sml: the sml code file path or parsed sml code of the lc definition
    :return: sml output in str or None if there is no sml executables
    """
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
    """ extract sml from the output got from run_sml

    :param sml_output: sml output text in str
    :return: reduction step and reduction result in a tuple or None if the execution fails
    """
    sl = list(i for i in sml_output.split('\n') if i)

    try:
        r_index = tuple(i for i in range(len(sl)) if sl[i].startswith('val start_'))[0] + 1
    except IndexError:
        print('source code does not follow the api')
        return
    try:
        o_index = tuple(i for i in range(r_index, len(sl)) if sl[i].startswith('val main_'))[0]
    except IndexError:
        print('cannot find main_ evaluation, possibly due to error')
        return

    if o_index < len(sl):
        output = '\n'.join(
            sl[r_index:-1]
        )
        result = '\n'.join(sl[o_index:])
        return output, result
    else:
        return None


def run_all(src: Union[pathlib.Path, str], verbose: bool = False) -> None:
    """ run src and print output

    :param src: src path obj or src str
    :param verbose: verbose flag
    :return: None
    """
    if isinstance(src, pathlib.Path):
        _, sml_code_path = write_main(read_and_eval(src), src, verbose)
    elif isinstance(src, str):
        f = pathlib.Path(src)
        if f.is_file() and src.endswith('.lc'):
            _, sml_code_path = write_main(read_and_eval(f), f, verbose)
        else:
            sml_code_path = _format_sml_exec_stream(eval_all(src), verbose)
    else:
        raise Exception('unknown file type')

    out = run_sml(sml_code_path)
    stdout, res = extract_sml_output(out)

    if verbose:
        print('verbose: ')
        print(stdout)
    print('reduced result: ')
    print(res)
    print('================')
    print()


def arg() -> Tuple:
    """ parse args

    :return: files arg and verbose flag in tuple
    """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('files', nargs='*', type=pathlib.Path, help='lc file path(s)')
    arg_parser.add_argument('-verbose', '-v', type=bool, default=False, required=False, help='verbose')

    parsed = arg_parser.parse_args()

    return getattr(parsed, 'files'), getattr(parsed, 'verbose')


def main() -> None:
    """ main function that read command line input or arguments

    :return: None
    """
    file_name, verbose = arg()

    if file_name:
        for file_name in file_name:
            file_path = pathlib.Path(file_name)
            if file_path.is_dir():
                for src_file_path in file_path.glob('*.lc'):
                    run_all(src_file_path, verbose=verbose)
            elif file_path.is_file():
                run_all(file_path, verbose=verbose)
            else:
                raise ValueError('Unsupported file type as input. Only accepts folders or *.lc files.')
    else:
        print("Enter an expression with Ctrl-D or Ctrl-Z to end: ")
        content = []
        while True:
            try:
                content.append(input())
            except EOFError:
                break
        run_all('\n'.join(content), verbose=verbose)


if __name__ == '__main__':
    main()
