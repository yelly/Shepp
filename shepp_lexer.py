"""A lexer for POSIX shells to be used with the SHEll PreProcessor."""

from ply.lex import TOKEN

import lexer


class SheppLexer(lexer.Lexer):
    """A lexer for POSIX shells to be used with the SHEll PreProcessor."""

    states = (('pp', 'exclusive'),)

    PP_RESERVED = {
        'include': 'INCLUDE',
        'define': 'DEFINE',
    }

    tokens = ('WS', 'WORD', 'PPID') + tuple(PP_RESERVED.values())

    t_WORD = r'[\w-]+'

    @TOKEN(r'\s+')
    def t_WS(self, t):
        """A whitespace token.

        Can include any number of whitespace charachters.
        """

        self._lexer.lineno += t.value.count('\n')
        return t

    def t_error(self, t):
        """Handling of unmatched tokens."""

        t.type = t.value[0]
        t.value = t.value[0]
        self._lexer.skip(1)

        return t

    @TOKEN(r'\#\$')
    def t_begin_pp(self, t):
        """Entering the PreProcessor state."""

        self._lexer.push_state('pp')

    @TOKEN(r'\s+')
    def t_pp_WS(self, t):
        """A whitespace token in PreProcessor state.

        Can include any number of whitespace charachters.
        If a newline is encountered, ends PreProcessor state.
        """

        if '\n' in t.value:
            self._lexer.pop_state()
            self._lexer.lineno += t.value.count('\n')
            t.value = '\n'
            return t

    @TOKEN(r'\w+')
    def t_pp_PPID(self, t):
        """PrePrecessor identifiers."""

        t.type = type(self).PP_RESERVED.get(t.value, 'PPID')

        return t
