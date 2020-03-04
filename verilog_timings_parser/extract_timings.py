import json
import argparse
from pathlib import Path
import re
from collections import defaultdict

from .yacc import Parser

class SpecifyParserError(object):
    def __init__(self, lineno, line):
        self.message = 'Error at line {}: {}'.format(lineno, line)

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
            else:
                if isspecify == 1:
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
                print(module)
                print('---------------')
                print('\n'.join(specifyblock))
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "input",
            help="JSON file containing mappings from cell to Verilog files",
            type=Path)
    parser.add_argument(
            "outputdir",
            help="The output directory that will contain extracted timings",
            type=Path)

    args = parser.parse_args()

    with open(args.input, 'r') as verilog:
        veriloglines = verilog.readlines()

    # print(veriloglines)

    extractor = VerilogSpecifyExtractor(veriloglines)
    extractor.parse()
    for module, parsedentry in extractor.parsedspecifyblocks.items():
        print('-------------------')
        print('Module: {}'.format(module))
        print('-------------------')
        print('Specparams')
        for param, value in parsedentry.specparams:
            print('{} = {}'.format(param, value))
        print('-------------------')
        print('Constraint checks')
        for c in parsedentry.constraintchecks:
            print(c)
        print('-------------------')
        print('Path delays')
        for p in parsedentry.pathdelays:
            print(p)
        print('-------------------')
        print('Conditioned path delays')
        for v in parsedentry.ifstatements.values():
            for e in v:
                print(e)

    # with open(args.outputdir, 'w') as out:
    #     out.write('\n'.join(extractor.veriloglines))

    # with open(args.input, 'r') as infile:
    #     celltolibs = json.load(infile)

    # numprint = 0
    # maxnumprint = 10
    # for cell, veriloglist in celltolibs.items():
    #     for verilogname in veriloglist:
    #         with open(verilogname, 'r') as verilog:
    #             lines = verilog.readlines()
    #         toprint = False
    #         for line in lines:
    #             if line.strip() == 'specify':
    #                 toprint = True
    #             # if toprint:
    #             #     print(line, end='')
    #             if line.strip() == 'endspecify':
    #                 toprint = False
    #                 numprint += 1
    #         if toprint:
    #             print('{} {}: unfinished specify block'.format(cell, verilogname))
    #         # if numprint >= maxnumprint:
    #         #     break
    #     if numprint >= maxnumprint:
    #         break
