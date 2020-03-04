import json
import argparse
from pathlib import Path
import re
from collections import defaultdict

from .yacc import Parser

class SpecifyParserError(Exception):
    def __init__(self, lineno, line):
        self.message = 'Error at line {}: {}'.format(lineno, line + 1)

    def __str__(self):
        if self.message:
            return self.message

class VerilogSpecifyExtractor(object):
    def __init__(self, veriloglines):
        self.moduletimings = []
        self.inmodule = False
        self.inspecify = False
        self.currmodulename = ''
        self.veriloglines = veriloglines
        self.specifyblocks = None
        self.parsedspecifyblocks = None

    def clear_verilog(self):
        # join all lines into single string
        fullfile = ''.join(self.veriloglines)

        # remove comments (C/C++ style)
        fullfile = re.sub(r'(?:\/\*(.*?)\*\/)|(?:\/\/(.*?)(?=\n))', '',
                          fullfile, flags=re.DOTALL)

        # remove line breaks
        fullfile = re.sub(r'\\[\s\r\t]*\n', '', fullfile, flags=re.DOTALL)

        # replace all tabs with single space
        fullfile = fullfile.replace('\t', ' ')

        # replace multiple spaces with one
        fullfile = re.sub(' +', ' ', fullfile)

        self.veriloglines = fullfile.split('\n')

    def extract_specify_blocks(self):
        specifyblocks = defaultdict(list)
        isspecify = 0
        modulename = None
        # XXX: assumption here that the crucial information of ifdef is stored in else part
        # XXX: except for SC_USE_PG_PIN
        ifdef = False
        remodule = re.compile(r'^\s*module\s*(?P<name>[a-zA-Z_][a-zA-Z0-9_\$]+)')
        respecify = re.compile(r'^\s*specify')
        reendspecify = re.compile(r'^\s*endspecify')
        for num, line in enumerate(self.veriloglines):
            modulematch = remodule.match(line)
            if modulematch:
                if isspecify == 1:
                    raise SpecifyParserError(num, line)
                modulename = modulematch.group('name')
                isspecify = 0
            elif respecify.match(line):
                if isspecify != 0:
                    raise SpecifyParserError(num, line)
                isspecify = 1
                if modulename is None:
                    raise SpecifyParserError(num, line)
                specifyblocks[modulename].append(line)
            elif reendspecify.match(line):
                if isspecify != 1:
                    raise SpecifyParserError(num, line)
                isspecify = 2
                specifyblocks[modulename].append(line)
            elif '`ifdef' in line:
                if not 'SC_USE_PG_PIN' in line:
                    ifdef = True
            elif '`ifndef' in line:
                pass
            elif '`else' in line:
                ifdef = False
            elif '`endif' in line:
                ifdef = False
            else:
                if isspecify == 1 and not ifdef:
                    specifyblocks[modulename].append(line)
        self.specifyblocks = specifyblocks

    def parse_specify_blocks(self):
        parsedspecifyblocks = dict()
        if self.specifyblocks is None:
            return None
        for module, specifyblock in self.specifyblocks.items():
            try:
                p = Parser()
                p.parse('\n'.join(specifyblock))
                parsedspecifyblocks[module] = {
                    'specparams': p.specparams,
                    'constraintchecks': p.constraintchecks,
                    'pathdelays': p.pathdelays,
                    'ifstatements': p.ifstatements
                }
            except Exception as ex:
                print('---------------')
                print('Module: {}'.format(module))
                print('---------------')
                for i, line in enumerate(specifyblock):
                    print('{:06d}: {}'.format(i+1, line))
                print('---------------')
                print(ex)
                print('---------------')
                raise ex
        self.parsedspecifyblocks = parsedspecifyblocks

    def parse(self):
        self.clear_verilog()
        self.extract_specify_blocks()
        self.parse_specify_blocks()

    def convert_timings_to_lib_json(self):
        pass
