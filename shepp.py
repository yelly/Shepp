"""A SHEll PreProcessor for POSIX shell scripts."""

import datetime

import shepp_lexer


class Shepp:
    """A SHEll PrePrcessor for POSIX shell scripts."""

    def __init__(self):
        self._lexer = shepp_lexer.SheppLexer()

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
        """Preprocess a Shepp script.

        Args:
            input (str): A Shepp script.

        Returns:
            str: A preprocessed POSIX shell script.
        """

        toks = self._lexer.lex(input)

        i = 0
        while i < len(toks):
            tok = toks[i]

            if tok.type == 'DEFINE':
                if not (toks[i + 1].type == 'PPID' and
                        toks[i + 2].type == 'PPID' and
                        toks[i + 3].type == 'WS'):
                    raise Exception('Bad define.')  # TODO: improve.

                toks.pop(i)
                self.define(toks.pop(i).value, toks.pop(i).value)
            elif tok.type == 'WORD':
                if tok.value in self._macros:
                    tok.value = self._macros[tok.value]

            i += 1

        for tok in toks:
            print(tok.value, end='')
