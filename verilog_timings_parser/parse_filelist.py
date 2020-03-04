import argparse
import json
from pathlib import Path
from specify_parser import extract_timings
from termcolor import colored

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input",
        help="JSON file containing cell names and Liberty filenames",
        type=Path)
    parser.add_argument(
        "outputdir",
        help="The directory that will contain the output",
        type=Path)
    parser.add_argument(
        "--path-prefix-to-remove",
        help="The substring that needs to be removed before generating subdirectories for Liberty files",
        type=Path)
    # parser.add_argument(
    #     "--num-jobs",
    #     help="Number of jobs to process files",
    #     type=int,
    #     default=1)

    args = parser.parse_args()

    with open(args.input, 'r') as infile:
        celltolibs = json.load(infile)

    toprocess = []
    
    for cell, files in celltolibs.items():
        celldir = args.outputdir / cell
        # celldir.mkdir(parents=True, exist_ok=True)
        for f in files:
            dirprefix = str(Path(f).parent)
            if args.path_prefix_to_remove:
                dirprefix = dirprefix.replace(str(args.path_prefix_to_remove), '')
            findir = celldir / ('./' + str(dirprefix))
            # findir.mkdir(parents=True, exist_ok=True)
            toprocess.append((f, cell, findir))

    allfilescount = len(toprocess)

    numfailed = 0

    errortypes = set()

    for num, data in enumerate(toprocess):
        print('{}  :  {}'.format(data[0], data[1]))
        with open(data[0], 'r') as f:
            veriloglines = f.readlines()
        try:
            extractor = extract_timings.VerilogSpecifyExtractor(veriloglines)
            extractor.parse()
            print(colored('[{:05d}/{:05d},failed={:05d}] {} : {} | DONE'.format(num + 1, allfilescount, numfailed, data[1], data[0]), 'green'))
        except Exception as ex:
            print(colored('[{:05d}/{:05d},failed={:05d}] {} : {} | ERROR : {}'.format(num + 1, allfilescount, numfailed, data[1], data[0], type(ex).__name__), 'red'))
            errortypes.add(type(ex).__name__)
            numfailed += 1
    print('{} out of {} failed'.format(numfailed, allfilescount))
    print('Error types:')
    print(errortypes)
