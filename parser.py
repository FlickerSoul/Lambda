# CSCI 384 parser for Lambda Calculus

"""
<term> ::= fn <name> => <term>
<term> ::= <term> <term>
<term> ::= <name> | ( <term> )
<def>  ::= <name> := <term>;
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Optional, Mapping, List, Iterable

from tokenizer import TokenStream


_VARIABLE = 'Variable'
_ABSTRACTION = 'Abstraction'
_APPLICATION = 'Application'

_MAIN_ENTRY = 'main'


def _read_supporting_code(ps: Iterable[Path]) -> str:
    content = []
    for p in ps:
        with open(p, 'r') as f:
            content.append(f.read())
    return '\n'.join(content)


class ASTBase:
    """ AST Base class """
    def __init__(self, label: str, *args):
        self.label = label
        self.args = args

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str([self.label, *self.args])


class Variable(ASTBase):
    """ Variable class """
    def __init__(self, var_name: str):
        super().__init__(_VARIABLE, var_name)
        self.var_name = var_name

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'VA"{self.var_name}"'


class Abstraction(ASTBase):
    """ Abstraction class """
    def __init__(self, var: str, term: ASTBase):
        super().__init__(_ABSTRACTION, var, term)
        self.var = var
        self.body = term

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'LM("{str(self.var)}",{str(self.body)})'


class Application(ASTBase):
    """ Application class """
    def __init__(self, term1: ASTBase, term2: ASTBase):
        super().__init__(_APPLICATION, term1, term2)
        self.applier = term1
        self.appliee = term2

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'AP({str(self.applier)},{str(self.appliee)})'


class Definition:
    """ Definition class
    The definition class handles lambda calculus source code parsing
    and the final main clause formatting
    """
    _LC_SUPPORT_CODES = [Path('fundaments.lc')]
    _SUPPORTING_CODE = _read_supporting_code(_LC_SUPPORT_CODES)

    def __init__(self, src: str) -> None:
        self._src: str = src
        self._tokens: Optional[TokenStream] = None
        self._defs = {}
        self._main: Optional[ASTBase] = None

    @property
    def formatted_main(self) -> Optional[ASTBase]:
        if self._main is not None:
            return self._main

        if _MAIN_ENTRY not in self._defs:
            return None

        main_clause: ASTBase = self._defs[_MAIN_ENTRY]
        for definition, term in list(reversed(self._defs.items()))[1:]:
            # reverse the definition dictionary and make it a list
            # omit the first entry which the main and begin wrapping 
            main_clause = Application(
                Abstraction(definition, main_clause), term
            )

        self._main = main_clause
        return main_clause

    @property
    def src(self) -> str:
        return self._SUPPORTING_CODE + '\n' + self._src

    @property
    def defs(self) -> dict:
        return self._defs

    @property
    def tokens(self) -> List:
        return self._tokens.tokens if self._tokens is not None else None

    def init(self) -> None:
        """ init parser internals """
        self._defs = {}
        self._tokens = None
        self._main = None

    def parse(self) -> Mapping[str, ASTBase]:
        """ tokenizes the src and parses it """
        self.init()
        print(self.src)
        self._tokens = TokenStream(self.src)
        self.parse_term(deepcopy(self._tokens))
        if _MAIN_ENTRY not in self.defs:
            print('Warning: main is not defined')
        return self.defs

    def parse_term(self, tokens: TokenStream, is_app=False) -> Optional[ASTBase]:
        """ The parsing helper """
        if tokens.next() == "fn":
            tokens.eat('fn')
            name = tokens.eatName()
            tokens.eat('=>')
            term = self.parse_term(tokens)
            r = Abstraction(name, term)

        elif tokens.next() == "(":
            tokens.eat("(")
            term = self.parse_term(tokens)
            tokens.eat(")")
            r = term

        elif tokens.nextIsName():
            name = tokens.eatName()
            r = Variable(name)
            if tokens.next() == ':=':
                tokens.eat(':=')
                term = self.parse_term(tokens)
                if term is None:
                    raise SyntaxError('Empty Definition')
                self._defs[r.var_name] = term
                tokens.eat(';')

                return self.parse_term(tokens)

        elif tokens.next() == "eof":
            return None

        else:
            raise SyntaxError("Unexpected token. Expected eof. Saw ''" + tokens.next()+"''.")

        if not is_app:
            try:
                next_term = self.parse_term(tokens, True)
                while next_term is not None:
                    r = Application(r, next_term)
                    next_term = self.parse_term(tokens, True)
            except SyntaxError:
                pass

        return r
