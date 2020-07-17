#!/usr/bin/env python3
"""A SHEll PreProcessor for POSIX shell scripts."""

import argparse
import datetime
from pathlib import Path
import sys
from typing import Optional, Iterator, Iterable, List, Dict

from ply.lex import LexToken

import shepp_lexer


class Shepp:
    """A SHEll PrePrcessor for POSIX shell scripts."""
    def __init__(self, path: Optional[Iterable[Path]] = None):
        self.path: List[Path] = [Path('.')]
        self._macros: Dict[str, str] = {}

        if path:
            self.path.extend(path)

        date = datetime.datetime.now()
        self.define('__DATE__', f'{date:%b} {date:%d} {date:%y}')
        self.define('__TIME__', f'{date:%H}:{date:%M}:{date:%S}')

    def define(self, name: str, value: str):
        """Define a macro.

        Args:
            name: The name of the macro.
            value: The value of the macro.
        """

        self._macros[name] = value

    def preprocess(self, script: str) -> Iterator[str]:
        """Preprocess a Shepp script and yield the result.

        Args:
            script: A Shepp script.

        Yields:
            Processed tokens.
        """

        for tok in type(self)._remove_empty_lines(
                self._lex_preprocess(script)):
            yield tok.value

    @staticmethod
    def _join_lines(tokens: Iterable[LexToken]) -> Iterator[LexToken]:
        """Joins lines after an escaped newline.

        Args:
            tokens: The stream of tokens to handle.

        Yields:
            The next token (with escaped newlines removed).
        """

        for tok in tokens:
            if tok.type == 'CHAR' and tok.value == '\n':
                continue

            yield tok

    @staticmethod
    def _remove_empty_lines(tokens: Iterable[LexToken]) -> Iterator[LexToken]:
        """Removes empty lines from a token stream.

        Args:
            tokens: The stream of tokens to handle.

        Yields:
            The next token (with empty newlines removed).
        """

        last_newline = False

        for tok in tokens:
            if tok.type == 'WS' and '\n' in tok.value:
                tok.value = '\n'

                if not last_newline:
                    yield tok

                last_newline = True
            else:
                yield tok
                last_newline = False

    def _lex_preprocess(self, script: str) -> Iterator[LexToken]:
        """Preprocess a Shepp script and yield lexed tokens.

        Args:
            script: A Shepp script.

        Yields:
            The next preprocessed token.
        """

        lexer = shepp_lexer.SheppLexer()

        tokens = type(self)._join_lines(lexer.lex(script))

        for tok in tokens:
            if tok.type == 'DEFINE':
                self._handle_define(tokens)
                continue

            if tok.type == 'INCLUDE':
                yield from self._handle_include(tokens)
                continue

            if tok.type == 'WORD':
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

    def _handle_include(self,
                        tokens: Iterator[LexToken]) -> Iterator[LexToken]:
        """Handle an include statement.

        Handle an include statement by consuming the relevant tokens from the stream and yielding
        the tokens from the included file.
        Should only be called after an INCLUDE token has been consumed.

        Args:
            tokens: The stream of tokens being handled.

        Yields:
            The next token from the included file.
        """

        try:
            include_tok = next(tokens)
        except StopIteration:
            raise Exception('Bad include.')  # TODO: improve

        if include_tok.type != 'PP_WORD':
            raise Exception('Bad include.')  # TODO: improve.

        include_name = Path(include_tok.value)

        for path in self.path:
            include_file = path / include_name

            if include_file.is_file():
                break
        else:
            raise Exception('Include file not found')  # TODO: improve.

        with open(include_file, 'rt') as file:
            script = file.read()

        yield from self._lex_preprocess(script)


def main(infile: Optional[Path] = None,
         outfile: Optional[Path] = None,
         path: Optional[Iterable[Path]] = None):
    """Preprocess a POSIX shell script.

    Args:
        infile: The path of the file to process, defaults to stdin.
        outfile: The output path of the processing result, defaults to stdout.
        path: An iterable of paths to search for includes.
    """

    if infile:
        with open(infile, 'rt') as file:
            script = file.read()
    else:
        script = sys.stdin.read()

    out = open(outfile, 'wt') if outfile else sys.stdout

    try:
        for tok in Shepp(path=path).preprocess(script):
            out.write(tok)
    finally:
        if outfile:
            out.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='SHEPP - A SHEll PreProcessor for POSIX scripts.')
    parser.add_argument('-i',
                        '--infile',
                        type=Path,
                        nargs='?',
                        help='The input path, defaults to stdin')
    parser.add_argument('-o',
                        '--outfile',
                        type=Path,
                        nargs='?',
                        help='The output path, defaults to stdout')
    parser.add_argument('-I',
                        '--include',
                        type=Path,
                        action='append',
                        help='A directory to search for includes')

    args = parser.parse_args()
    main(args.infile, args.outfile, args.include)
