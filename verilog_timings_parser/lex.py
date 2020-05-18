import ply.lex as lex
from ply.lex import TOKEN
import re
import sys


class Number(object):
    def __init__(self, size, typ, value):
        self.size = size
        self.typ = typ
        self.value = value

    def __str__(self):
        if (self.size == 32 and self.typ == 'd') or self.typ == 'f':
            return str(self.value)
        return "{}'{}{}".format(self.size, self.typ, format(self.value, self.typ if self.typ != 'h' else 'x'))

    def __add__(self, other):
        return Number(self.size, self.typ, self.value + other.value)

    def __sub__(self, other):
        return Number(self.size, self.typ, self.value - other.value)

    def __neg__(self):
        return Number(self.size, self.typ, -self.value)

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)


class SpecifyLexer(object):

    class InvalidNumberException(Exception):
        def __init__(self, line, value):
            self.message = 'Invalid number {} at line {}'.format(value, line)

        def __str__(self):
            if self.message:
                return self.message

    class TokenizeError(Exception):
        def __init__(self, message):
            self.message = message

        def __str__(self):
            if self.message:
                return self.message

    def __init__(self):
        self.logger = lex.PlyLogger(sys.stdout)
        self.lexer = lex.lex(module=self, errorlog=self.logger)
        self.input_data = ''

    reserved = {
        'specify': 'SPECIFY',
        'endspecify': 'ENDSPECIFY',
        'specparam': 'SPECPARAM',
        'posedge': 'POSEDGE',
        'negedge': 'NEGEDGE',
        'if': 'IF',
        'ifnone': 'IFNONE'
    }

    tokens = [
        'PLUS',
        'MINUS',
        'EQUALS',
        'AND',
        'EQ',
        'EXCL',
        'TILDA',
        'LPAR',
        'RPAR',
        'STRING',
        'EVAND',
        'SETUP',
        'HOLD',
        'SETUPHOLD',
        'SKEW',
        'RECOVERY',
        'PERIOD',
        'WIDTH',
        'RECREM',
        'COMMA',
        'SEMI',
        'COLON',
        'NAME',
        'NUMBER',
        'PATHTOKEN',
        ] + list(reserved.values())

    t_ignore = '[ \t]'
    t_PLUS = r'\+'
    t_MINUS = r'\-'
    t_AND = r'\&\&?'
    t_EQ = r'===?'
    t_EXCL = r'\!'
    t_TILDA = r'~'
    t_EQUALS = r'\='
    t_LPAR = r'\('
    t_RPAR = r'\)'
    t_STRING = r'".*"'
    t_EVAND = r'\&\&\&'
    t_SETUP = r'\$setup'
    t_HOLD = r'\$hold'
    t_SETUPHOLD = r'\$setuphold'
    t_SKEW = r'\$skew'
    t_RECOVERY = r'\$recovery'
    t_PERIOD = r'\$period'
    t_WIDTH = r'\$width'
    t_RECREM = r'\$recrem'
    t_COMMA = r','
    t_SEMI = r';'
    t_COLON = r':'

    def t_NAME(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_\$]*(\[[0-9]+\])?'
        t.type = self.reserved.get(t.value, 'NAME')
        return t

    def t_REAL(self, t):
        r'[-+]?[0-9]+\.[0-9]+'
        t.type = 'NUMBER'
        t.value = Number(32, 'f', float(t.value))
        return t

    def t_NUMBER(self, t):
        r'((?P<size>[0-9]+)?\'(?P<type>[bBoOhHdD])(?P<value>[0-9a-fA-F_]+)|(?P<dvalue>[0-9]+))'
        match = t.lexer.lexmatch
        size = 32
        typ = 'd'
        value = (match.group('dvalue') if match.group('dvalue')
                else match.group('value').lower())
        value = value.replace('_', '')
        digsize = {2: 1, 8: 3, 16: 4, 10: 4}

        def convert_value(regex, base):
            if (not re.match(regex, value) or
                    len(value) * digsize[base] > size):
                raise SpecifyLexer.InvalidNumberException(
                        t.lexer.lineno,
                        t.value)
            return int(value, base)

        if match.group('size'):
            size = int(match.group('size'))
        if match.group('type'):
            typ = match.group('type').lower()
        if typ == 'b':
            value = convert_value(r'[01]+', 2)
        elif typ == 'o':
            value = convert_value(r'[0-7]+', 8)
        elif typ == 'h':
            value = convert_value(r'[0-9a-f]+', 16)
        else:
            value = convert_value(r'[0-9]+', 10)
        t.value = Number(size, typ, value)
        return t

    def t_PATHTOKEN(self, t):
        r'(?P<pathtype>[\*=]>)'
        match = t.lexer.lexmatch
        parallel = match.group('pathtype') == '=>'
        t.value = parallel
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count('\n')

    def t_error(self, t):
        raise SpecifyLexer.TokenizeError(
                'Illegal character {} at line {}'.format(
                    t.value[0],
                    t.lexer.lineno))

    def test(self, data):
        self.lexer.input(data)
        while True:
            token = self.lexer.token()
            if token:
                print('{} : {}'.format(str(token), str(token.value)))
            else:
                break
