"""A useful ply lexer class."""

from ply import lex


class LexingError(Exception):
    """An exception raised when an error is encountered during lexing."""

    def __init__(self, token):
        """
        Args:
            token (LexTokens): The token which caused the error.
        """

        super().__init__()

        self._token = token

    @property
    def token(self):
        """The token which caused the error (LexTokens)."""

        return self._token

    def __str__(self):
        return f'Unrecognised character {self.token.value[0]} encountered at position {self.token.lexpos} on line {self.token.lineno}.'


class Lexer:
    """A useful ply lexer class."""

    def __init__(self, **kwargs):
        """Initialize the lexer.

        All arguments are passed as is to lex.lex.
        """

        self._lexer = lex.lex(module=self, **kwargs)

    def t_ANY_error(self, t):
        """General error handling."""

        raise LexingError(t)

    def set_input(self, input):
        """Sets the lexer input.

        Args:
            input (str): The input to the lexer.
        """

        self._lexer.input(input)

    def lex_tokens(self):
        """A generator that yields tokens parsed from the input.

        Yields:
            LexTokens: The next token lexed from the input.
        """

        while True:
            tok = self._lexer.token()
            if not tok:
                break

            yield tok

    def lex(self, input):
        """Lex an input string.

        Args:
            input (str): A string to lex.

        Returns:
            list[LexTokens]: A list of lexed tokens.
        """

        self.set_input(input)
        return [tok for tok in self.lex_tokens()]

    def lex_file(self, path):
        """Lex the contents of a file.

        Args:
            path (str): The path of the file to lex.

        Returns:
            list[LexTokens]: A list of the tokens lexed from the file.
        """

        with open(path, 'rt') as f:
            input = f.read()

        return self.lex(input)
