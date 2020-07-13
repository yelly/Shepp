#!/usr/bin/env python3
"""A SHEll PreProcessor for POSIX shell scripts."""

import argparse
import datetime
from pathlib import Path
import sys
from typing import *

from ply.lex import LexToken

import shepp_lexer


class Shepp:
    """A SHEll PrePrcessor for POSIX shell scripts."""

    def __init__(self, path: Optional[Iterable[Path]]=None):
        self.path: List[Path] = [Path('.')]
        self._macros: Dict[str, str] = {}

        if path:
            self.path.extend(path)

        dt = datetime.datetime.now()
        self.define('__DATE__', f'{dt:%b} {dt:%d} {dt:%y}')
        self.define('__TIME__', f'{dt:%H}:{dt:%M}:{dt:%S}')

    def define(self, name: str, value: str):
        """Define a macro.

        Args:
            name: The name of the macro.
            value: The value of the macro.
        """

        self._macros[name] = value

    def preprocess(self, input: str) -> Iterator[str]:
        """Preprocess a Shepp script and yield the result.

        Args:
            input: A Shepp script.

        Yields:
            Processed tokens.
        """

        for tok in self._lex_preprocess(input):
            yield tok.value

    def _join_lines(self, tokens: Iterable[LexToken]) -> Iterator[LexToken]:
        """Joins lines after an escaped newline.

        Args:
            tokens: The stream of tokens to handle.

        Yields:
            The next token (with escaped newlines removed).
        """

        for tok in tokens:
            if tok.type == 'CHAR' and tok.value == '\\\n':
                continue

            yield tok

    def _lex_preprocess(self, input: str) -> Iterator[LexToken]:
        """Preprocess a Shepp script and yield lexed tokens.

        Args:
            input: A Shepp script.

        Yields:
            The next preprocessed token.
        """

        lexer = shepp_lexer.SheppLexer()

        tokens = self._join_lines(lexer.lex(input))

        for tok in tokens:
            if tok.type == 'COMMENT':
                continue
            if tok.type == 'DEFINE':
                self._handle_define(tokens)
                continue
            elif tok.type == 'WORD':
                if tok.value in self._macros:
                    tok.value = self._macros[tok.value]

            yield tok

    def _handle_define(self, tokens: Iterator[LexToken]):
        """Handle a define statement.

        Handle a define statement by consuming the relevant tokens from the stream.
        Should only be called after a DEFINE token has been consumed.

        Args:
            tokens: The stream of tokens being handled.
        """

        name = next(tokens)
        if name.type != 'PP_WORD':
            raise Exception('Bad define.')  # TODO: improve.

        value = next(tokens)
        if value.type != 'PP_WORD':
            raise Exception('Bad define.')  # TODO: improve.

        self.define(name.value, value.value)

        if next(tokens).type != 'WS':
            raise Exception('Bad define.')  # TODO: improve.

    def _handle_include(self, tokens: Iterable[LexToken]) -> LexToken:
        """Handle an include statement.

        Handle an include statement by consuming the relevant tokens from the stream and yielding
        the tokens from the included file.
        Should only be called after an INCLUDE token has been consumed.

        Args:
            tokens: The stream of tokens being handled.

        Yields:
            The next token from the included file.
        """

        pass


def main(infile: Optional[Path]=None, outfile: Optional[Path]=None, path: Optional[Iterable[Path]]=None):
    """Preprocess a POSIX shell script.

    Args:
        infile: The path of the file to process, defaults to stdin.
        outfile: The output path of the processing result, defaults to stdout.
        path: An iterable of paths to search for includes.
    """

    if infile:
        with open(infile, 'rt') as f:
            input = f.read()
    else:
        input = sys.stdin.read()

    out = open(outfile, 'wt') if outfile else sys.stdout

    try:
        for tok in Shepp(path=path).preprocess(input):
            out.write(tok)
    finally:
        if outfile:
            out.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SHEPP - A SHEll PreProcessor for POSIX scripts.')
    parser.add_argument('-i', '--infile', type=Path, nargs='?', help='The path of a file to process, defaults to stdin')
    parser.add_argument('-o', '--outfile', type=Path, nargs='?', help='The output path, defaults to stdout')
    parser.add_argument('-I', '--include', type=Path, action='append', help='A directory to search for includes')

    args = parser.parse_args()
    main(args.infile, args.outfile, args.include)
