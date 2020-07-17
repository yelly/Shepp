"""A useful ply lexer class."""

from pathlib import Path
from typing import *

from ply import lex
from ply.lex import LexToken


class LexingError(Exception):
    """An exception raised when an error is encountered during lexing."""
    def __init__(self, token: LexToken):
        """
        Args:
            token: The token which caused the error.
        """

        super().__init__()

        self._token = token

    @property
    def token(self) -> LexToken:
        """The token which caused the error."""

        return self._token

    def __str__(self) -> str:
        return f'Unrecognised character {self.token.value[0]} encountered at position {self.token.lexpos} on line {self.token.lineno}.'


class Lexer:
    """A useful ply lexer class."""
    def __init__(self, **kwargs):
        """Initialize the lexer.

        All arguments are passed as is to lex.lex.
        """

        self._lexer = lex.lex(module=self, **kwargs)

    def t_ANY_error(self, t: LexToken):
        """General error handling."""

        raise LexingError(t)

    def set_input(self, input: str):
        """Sets the lexer input.

        Args:
            input: The input to the lexer.
        """

        self._lexer.input(input)

    def lex_tokens(self) -> Iterator[LexToken]:
        """A generator that yields tokens parsed from the input.

        Yields:
            The next token lexed from the input.
        """

        while True:
            tok = self._lexer.token()
            if not tok:
                break

            yield tok

    def lex(self, input: str) -> Iterator[LexToken]:
        """Lex an input string.

        Args:
            input: A string to lex.

        Returns:
            A generator of lexed tokens.
        """

        self.set_input(input)
        return self.lex_tokens()

    def lex_file(self, path: Path) -> Iterator[LexToken]:
        """Lex the contents of a file.

        Args:
            path: The path of the file to lex.

        Returns:
            A generator of the tokens lexed from the file.
        """

        with open(path, 'rt') as f:
            input = f.read()

        return self.lex(input)
