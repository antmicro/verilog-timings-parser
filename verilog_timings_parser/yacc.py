import ply.yacc as yacc
import sys
from pprint import pprint as pp

from .lex import SpecifyLexer
from collections import defaultdict


class Parser:

    class SpecparamRedefinitionError(Exception):
        def __init__(self, line, specparamname):
            self.message = 'Specparam redefinition "{}" at line {}'.format(
                    specparamname, line)

        def __str__(self):
            if self.message:
                return self.message

    class SpecparamNotDeclared(Exception):
        def __init__(self, line, specparamname):
            self.message = 'Specparam "{}" at line {} is not declared'.format(
                    specparamname, line)

        def __str__(self):
            if self.message:
                return self.message

    class IfnoneError(Exception):
        def __init__(self, line):
            self.message = 'Ifnone at line {} is corresponding to nonexistent delay path'.format(line)

        def __str__(self):
            if self.message:
                return self.message

    tokens = SpecifyLexer.tokens

    precedence = (
        ('left', 'PLUS', 'MINUS'),
        ('left', 'AND'),
        ('left', 'EQ'),
        ('right', 'UMINUS', 'UPLUS', 'EXCL'),
    )

    def __init__(self):
        self.lexer = SpecifyLexer()
        self.specparams = {}
        self.constraintchecks = []
        self.pathdelays = []
        self.ifstatements = defaultdict(list)
        self.logger = yacc.PlyLogger(sys.stdout)
        self.parser = yacc.yacc(module=self, errorlog=self.logger, debuglog=self.logger, write_tables=False)

    def p_specify_block(self, p):
        '''specifyblock : SPECIFY specdecl constraintchecks pathdelays ifstatements ENDSPECIFY'''
        # '''specify_block : SPECIFY specdecl constraintchecks pathdelays ENDSPECIFY
        #                  | SPECIFY specdecl pathdelays ENDSPECIFY
        #                  | SPECIFY pathdelays ENDSPECIFY
        #                  | SPECIFY constraintchecks pathdelays ENDSPECIFY
        #                  | SPECIFY specdecl ENDSPECIFY''' # FIXME: remove this one
        print('PARSED file')
        pp(self.specparams, indent=3)
        pp(self.constraintchecks, indent=3)
        pp(self.pathdelays, indent=3)
        pp(self.ifstatements, indent=3)

    # SPECPARAM block
    # ---------------

    def p_specdecl_block(self, p):
        '''specdecl : specparam
                    | specdecl specparam'''
        p[0] = p[1]

    def p_specparam_assign(self, p):
        'specparam : SPECPARAM NAME EQUALS expression SEMI'
        if p[2] in self.specparams:
            raise self.SpecparamRedefinitionError(p.lineno(2), p[2])
        else:
            self.specparams[p[2]] = p[4]

    # CONSTRAINTCHECK block
    # ---------------------

    def p_constraintchecks_block(self, p):
        '''constraintchecks : constraintcheck
                            | constraintchecks constraintcheck'''
        p[0] = p[1]

    def p_constraintcheck_group(self, p):
        '''constraintcheck : setup
                           | hold
                           | setuphold
                           | skew
                           | recovery
                           | period
                           | width'''
        p[0] = p[1]

    def p_setup_entry(self, p):
        '''setup : SETUP LPAR event COMMA event COMMA delval COMMA NAME RPAR SEMI
                 | SETUP LPAR event COMMA event COMMA delval RPAR SEMI'''
        constraint = {
            'type': 'setup',
            'data_event': p[3],
            'reference_event': p[5],
            'limit': p[7],
            'notifier': p[9] if len(p) == 11 else None
        }
        self.constraintchecks.append(constraint)

    def p_hold_entry(self, p):
        '''hold : HOLD LPAR event COMMA event COMMA delval COMMA NAME RPAR SEMI
                | HOLD LPAR event COMMA event COMMA delval RPAR SEMI'''
        constraint = {
            'type': 'hold',
            'reference_event': p[3],
            'data_event': p[5],
            'limit': p[7],
            'notifier': p[9] if len(p) == 11 else None
        }
        self.constraintchecks.append(constraint)

    def p_setuphold_entry(self, p):
        '''setuphold : SETUPHOLD LPAR event COMMA event COMMA delval COMMA delval COMMA NAME RPAR SEMI
                     | SETUPHOLD LPAR event COMMA event COMMA delval COMMA delval RPAR SEMI'''
        constraint = {
            'type': 'setuphold',
            'reference_event': p[3],
            'data_event': p[5],
            'setup_limit': p[7],
            'hold_limit': p[9],
            'notifier': p[11] if len(p) == 13 else None
        }
        self.constraintchecks.append(constraint)

    def p_skew_entry(self, p):
        '''skew : SKEW LPAR event COMMA event COMMA delval COMMA NAME RPAR SEMI
                | SKEW LPAR event COMMA event COMMA delval RPAR SEMI'''
        constraint = {
            'type': 'skew',
            'reference_event': p[3],
            'data_event': p[5],
            'limit': p[7],
            'notifier': p[9] if len(p) == 11 else None
        }
        self.constraintchecks.append(constraint)

    def p_recovery_entry(self, p):
        '''recovery : RECOVERY LPAR event COMMA event COMMA delval COMMA NAME RPAR SEMI
                    | RECOVERY LPAR event COMMA event COMMA delval RPAR SEMI'''
        constraint = {
            'type': 'recovery',
            'reference_event': p[3],
            'data_event': p[5],
            'limit': p[7],
            'notifier': p[9] if len(p) == 11 else None
        }
        self.constraintchecks.append(constraint)

    def p_period_entry(self, p):
        '''period : PERIOD LPAR event COMMA delval COMMA NAME RPAR SEMI
                  | PERIOD LPAR event COMMA delval RPAR SEMI'''
        constraint = {
            'type': 'period',
            'reference_event': p[3],
            'limit': p[5],
            'notifier': p[7] if len(p) == 9 else None
        }
        self.constraintchecks.append(constraint)

    def p_width_entry(self, p):
        '''width : WIDTH LPAR event COMMA delval COMMA delval COMMA NAME RPAR SEMI
                 | WIDTH LPAR event COMMA delval COMMA delval RPAR SEMI'''
        constraint = {
            'type': 'width',
            'reference_event': p[3],
            'width_limit': p[5],
            'width_threshold': p[7],
            'notifier': p[9] if len(p) == 11 else None
        }
        self.constraintchecks.append(constraint)

    # PATHDELAYS block
    # ----------------

    def p_pathdelays_block(self, p):
        '''pathdelays : pathdelay
                      | pathdelays pathdelay'''
        p[0] = p[1]
        self.pathdelays.append(p[len(p) - 1])

    def p_pathdelay_simple(self, p):
        '''pathdelay : LPAR NAME PATHTOKEN NAME RPAR EQUALS delaylist SEMI
                     | LPAR NAME PLUS PATHTOKEN NAME RPAR EQUALS delaylist SEMI
                     | LPAR NAME MINUS PATHTOKEN NAME RPAR EQUALS delaylist SEMI
        '''
        if str(p[3]) not in '+-':
            pathdelay = {
                'cond': None,
                'edge': None,
                'input_port': p[2],
                'parallel': p[3],
                'output_port': p[4],
                'inverted': False,
                'source': None,
                'delaylist': p[7]
            }
        else:
            pathdelay = {
                'cond': None,
                'edge': None,
                'input_port': p[2],
                'parallel': p[4],
                'output_port': p[5],
                'inverted': p[3],
                'source': None,
                'delaylist': p[8]
            }
        p[0] = pathdelay

    def p_pathdelay_edge(self, p):
        '''pathdelay : LPAR edge NAME PATHTOKEN LPAR NAME RPAR RPAR EQUALS delaylist SEMI
                     | LPAR edge NAME PATHTOKEN LPAR NAME COLON NAME RPAR RPAR EQUALS delaylist SEMI
                     | LPAR edge NAME PATHTOKEN LPAR NAME PLUS COLON NAME RPAR RPAR EQUALS delaylist SEMI
                     | LPAR edge NAME PATHTOKEN LPAR NAME MINUS COLON NAME RPAR RPAR EQUALS delaylist SEMI
        '''
        if p[7] == ')':
            pathdelay = {
                'cond': None,
                'edge': p[2],
                'input_port': p[3],
                'parallel': p[4],
                'output_port': p[6],
                'inverted': False,
                'source': None,
                'delaylist': p[10]
            }
        elif p[7] == ':':
            pathdelay = {
                'cond': None,
                'edge': p[2],
                'input_port': p[3],
                'parallel': p[4],
                'output_port': p[6],
                'inverted': False,
                'source': p[8],
                'delaylist': p[12]
            }
        else:
            pathdelay = {
                'cond': None,
                'edge': p[2],
                'input_port': p[3],
                'parallel': p[4],
                'output_port': p[6],
                'inverted': p[7] == '-',
                'source': p[9],
                'delaylist': p[13]
            }
        p[0] = pathdelay

    # DELAY IF STATEMENTS
    # -------------------

    def _getifkey(self, condpathdelay):
        key = (
            condpathdelay['input_port'],
            condpathdelay['output_port'])
        #     condpathdelay['parallel'],
        #     condpathdelay['inverted'],
        #     condpathdelay['source'])
        return key

    def p_ifstatement_oneline(self, p):
        '''ifstatement : IF LPAR cond RPAR pathdelay'''
        condpathdelay = p[5]
        condpathdelay['cond'] = p[3]
        p[0] = condpathdelay

    def p_ifstatement_ifnone(self, p):
        '''ifstatement : IFNONE pathdelay'''
        condpathdelay = p[2]
        key = self._getifkey(condpathdelay)
        if key not in self.ifstatements:
            raise self.IfnoneError(p.lineno(1))
        fincond = []
        for delaypath in self.ifstatements[key]:
            fincond.append('!({})'.format(delaypath['cond']))
        fincond = '&'.join(fincond)
        condpathdelay['cond'] = fincond
        p[0] = condpathdelay

    def p_ifstatement_multiline(self, p):
        '''ifstatements : ifstatement
                        | ifstatements ifstatement'''
        p[0] = p[1]
        pif = p[len(p) - 1]
        key = self._getifkey(pif)
        self.ifstatements[key].append(pif)

    # DELAY VALUES
    # ------------

    def p_delval_mintypmax(self, p):
        '''delval : expression COLON expression COLON expression'''
        p[0] = [int(p[1]), int(p[3]), int(p[5])]

    def p_delval_simple(self, p):
        '''delval : expression'''
        val = int(p[1])
        p[0] = [val, val, val]

    def p_delaylist_1(self, p):
        '''delaylist : delval'''
        p[0] = {
            'rise': p[1],
            'fall': p[1],

            '0->Z': p[1],
            'Z->1': p[1],
            '1->Z': p[1],
            'Z->0': p[1],

            '0->X': p[1],
            'X->1': p[1],
            '1->X': p[1],
            'X->0': p[1],
            'X->Z': p[1],
            'Z->X': p[1],
        }

    def p_delaylist_1_par(self, p):
        '''delaylist : LPAR delval RPAR'''
        p[0] = {
            'rise': p[2],
            'fall': p[2],

            '0->Z': p[2],
            'Z->1': p[2],
            '1->Z': p[2],
            'Z->0': p[2],

            '0->X': p[2],
            'X->1': p[2],
            '1->X': p[2],
            'X->0': p[2],
            'X->Z': p[2],
            'Z->X': p[2],
        }

    def p_delaylist_2(self, p):
        '''delaylist : LPAR delval COMMA delval RPAR'''
        p[0] = {
            'rise': p[2],
            'fall': p[4],

            '0->Z': p[2],
            'Z->1': p[2],
            '1->Z': p[4],
            'Z->0': p[4],

            '0->X': p[2],
            'X->1': p[2],
            '1->X': p[4],
            'X->0': p[4],
            'X->Z': max(p[2], p[4]),
            'Z->X': min(p[2], p[4]),
        }

    def p_delaylist_3(self, p):
        '''delaylist : LPAR delval COMMA delval COMMA delval RPAR'''
        p[0] = {
            'rise': p[2],
            'fall': p[4],

            '0->Z': p[6],
            'Z->1': p[2],
            '1->Z': p[6],
            'Z->0': p[4],

            '0->X': min(p[2], p[6]),
            'X->1': p[2],
            '1->X': min(p[4], p[6]),
            'X->0': p[4],
            'X->Z': p[6],
            'Z->X': min(p[2], p[4]),
        }

    def p_delaylist_6(self, p):
        '''delaylist : LPAR delval COMMA delval COMMA delval COMMA delval COMMA delval COMMA delval RPAR'''
        p[0] = {
            'rise': p[2],
            'fall': p[4],

            '0->Z': p[6],
            'Z->1': p[8],
            '1->Z': p[10],
            'Z->0': p[12],

            '0->X': min(p[2], p[6]),
            'X->1': max(p[2], p[8]),
            '1->X': min(p[4], p[10]),
            'X->0': max(p[4], p[12]),
            'X->Z': max(p[6], p[10]),
            'Z->X': min(p[8], p[12]),
        }

    def p_delaylist_12(self, p):
        '''delaylist : LPAR delval COMMA delval COMMA delval COMMA delval COMMA delval COMMA delval COMMA delval COMMA delval COMMA delval COMMA delval COMMA delval COMMA delval RPAR'''
        p[0] = {
            'rise': p[2],
            'fall': p[4],

            '0->Z': p[6],
            'Z->1': p[8],
            '1->Z': p[10],
            'Z->0': p[12],

            '0->X': p[14],
            'X->1': p[16],
            '1->X': p[18],
            'X->0': p[20],
            'X->Z': p[22],
            'Z->X': p[24],
        }

    # SIMPLE EXPRESSIONS
    # ------------------

    def p_edge_entry(self, p):
        '''edge : POSEDGE
                | NEGEDGE'''
        p[0] = p[1]

    def p_event_entry(self, p):
        '''event : edge NAME
                 | edge evand'''
        p[0] = {
            'edge': p[1],
            'signals': p[2] if type(p[2]) is list else [p[2]]
        }

    def p_evand_expr(self, p):
        ''' evand : NAME EVAND NAME
                  | evand EVAND NAME'''
        if type(p[1]) is list:
            p[0] = p[1].extend(p[3])
        else:
            p[0] = [p[1], p[3]]

    def p_expression_op(self, p):
        '''expression : expression PLUS expression
                      | expression MINUS expression'''
        if p[2] == '+':
            p[0] = p[1] + p[3]
        elif p[2] == '-':
            p[0] = p[1] - p[3]

    def p_expression_unary(self, p):
        '''expression : MINUS expression %prec UMINUS
                      | PLUS expression %prec UPLUS'''
        if p[1] == '+':
            p[0] = p[2]
        elif p[1] == '-':
            p[0] = -p[2]

    def p_expression_parenthesis(self, p):
        'expression : LPAR expression RPAR'
        p[0] = p[2]

    def p_expression_number(self, p):
        'expression : NUMBER'
        p[0] = p[1]

    def p_expression_name(self, p):
        'expression : NAME'
        if not p[1] in  self.specparams:
            raise self.SpecparamNotDeclared(p.lineno(1), p[1])
        else:
            p[0] = self.specparams[p[1]]

    # IF CONDITIONS
    # -------------

    def p_cond_number(self, p):
        'cond : NUMBER'
        p[0] = str(p[1])

    def p_cond_name(self, p):
        'cond : NAME'
        if p[1] in self.specparams:
            p[0] = str(self.specparams[p[1]])
        else:
            p[0] = p[1]

    def p_cond_and(self, p):
        '''cond : cond AND cond
                | cond EQ cond'''
        p[0] = '{}{}{}'.format(p[1],p[2],p[3])

    def p_cond_par(self, p):
        '''cond : LPAR cond RPAR'''
        p[0] = '{}{}{}'.format(p[1],p[2],p[3])

    def p_cond_inv(self, p):
        '''cond : EXCL cond'''
        p[0] = '{}{}'.format(p[1],p[2])

    # ERROR HANDLING
    # --------------

    def p_error(self, p):
        if p:
            print('Syntax error at "{}" (line {})'.format(p.value, p.lineno))
        else:
            print('Syntax error at EOF')

    # PARSING SCRIPT
    # --------------

    def parse(self, s):
        self.lexer.input_data = s
        return self.parser.parse(self.lexer.input_data)
