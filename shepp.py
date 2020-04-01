"""A SHEll PreProcessor for POSIX shell scripts."""

import datetime

import shepp_lexer


class Shepp:
    """A SHEll PrePrcessor for POSIX shell scripts."""

    def __init__(self):
        self._macros = {}

        dt = datetime.datetime.now()
        self.define('__DATE__', f'{dt:%b} {dt:%d} {dt:%y}')
        self.define('__TIME__', f'{dt:%H}:{dt:%M}:{dt:%S}')

    def define(self, name, value):
        """Define a macro.

        Args:
            name (str): The name of the macro.
            value (str): The value of the macro.
        """

        self._macros[name] = value

    def preprocess(self, input):
        """Preprocess a Shepp script and print the result.

        Args:
            input (str): A Shepp script.
        """

        for tok in self._lex_preprocess(input):
            print(tok.value, end='')

    def _join_lines(self, tokens):
        """Joins lines after an escaped newline.

        Args:
            tokens (generator[LexTokens]): The stream of tokens to handle.

        Yields:
            LexTokens: The next token (with escaped newlines removed).
        """

        for tok in tokens:
            if tok.type == '\\':
                next_tok = next(tokens)

                if next_tok.type == 'WS' and next_tok.value[0] == '\n':
                    if len(next_tok.value) > 1:
                        next_tok.value = next_tok.value[1:]
                        yield next_tok
                else:
                    yield tok
                    yield next_tok

                continue

            yield tok

    def _lex_preprocess(self, input):
        """Preprocess a Shepp script and yield lexed tokens.

        Args:
            input (str): A Shepp script.

        Yields:
            LexTokens: The next preprocessed token.
        """

        lexer = shepp_lexer.SheppLexer()

        tokens = self._join_lines(lexer.lex(input))

        for tok in tokens:
            if tok.type == 'DEFINE':
                self._handle_define(tokens)
                continue
            elif tok.type == 'WORD':
                if tok.value in self._macros:
                    tok.value = self._macros[tok.value]

            yield tok

    def _handle_define(self, tokens):
        """Handle a define statement.

        Handle a define statement by consuming the relevant tokens from the stream.
        Should only be called after a DEFINE token has been consumed.

        Args:
            tokens (generator[LexTokens]): The stream of tokens being handled.
        """

        name = next(tokens)
        if name.type != 'PPID':
            raise Exception('Bad define.')  # TODO: improve.

        value = next(tokens)
        if value.type != 'PPID':
            raise Exception('Bad define.')  # TODO: improve.

        self.define(name.value, value.value)

        if next(tokens).type != 'WS':
            raise Exception('Bad define.')  # TODO: improve.
