import json
import argparse
from pathlib import Path
import re


class VerilogSpecifyExtractor(object):
    def __init__(self, veriloglines):
        self.moduletimings = []
        self.inmodule = False
        self.inspecify = False
        self.currmodulename = ''
        self.veriloglines = veriloglines

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

    def extract_timings(self):
        identifier = r'([a-zA-Z_][a-zA-Z0-9_\$]+|(?<=\\).*(?=\s))'
        logicvalue = r'[01zZxX]'
        literalintb = r'[0-9]+\'[bB][01xXzZ?_]+'
        literalinto = r'[0-9]+\'[oO][0-7xXzZ?_]+'
        literalinth = r'[0-9]+\'[hH][0-7=9a-fA-FxXzZ?_]+'
        literalintd = r'((?P<size>[0-9])+\'[dD])?[0-7xXzZ?_]+'

        module = re.compile(
                r'^\s*module\s*(?P<modulename>{identifier})'.format(identifier)
                )
        endmodule = re.compile(r'^\s*endmodule')
        specify = re.compile(r'^\s*specify')
        endspecify = re.compile(r'^\s*endspecify')

        literalint = pass
        for line in self.veriloglines:

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
    extractor.clear_verilog()
    with open(args.outputdir, 'w') as out:
        out.write('\n'.join(extractor.veriloglines))

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
