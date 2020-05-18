import argparse
from pathlib import Path
from . import extract_timings
from pprint import pprint as pp
from quicklogic_timings_importer import json_to_liberty


def convert_specify_to_libertyjson(libraryname, parsedentry):
    librarycontent = {}
    for key, entry in parsedentry.items():
        newname = key
        cell = "cell {}".format(newname)
        librarycontent[cell] = {}
        allpaths = entry['pathdelays']
        for paths in entry['ifstatements'].values():
            allpaths.extend(paths)
        for pathdelay in allpaths:
            pinname = 'pin {}'.format(pathdelay['output_port'])
            if not pinname in librarycontent[cell]:
                librarycontent[cell][pinname] = {}
            if not 'timing ' in librarycontent[cell][pinname]:
                librarycontent[cell][pinname]['timing '] = []
            timing = {}
            timing['related_pin'] = pathdelay['input_port']
            if pathdelay['cond']:
                timing['when'] = pathdelay['cond']
            if pathdelay['source']:
                if 'related_pin' in timing and pathdelay['source'] not in timing['related_pin'].split(' '):
                    timing['related_pin'] += ' {}'.format(pathdelay['source'])
            if pathdelay['inverted']:
                if 'when' in timing:
                    timing['when'] = '!{}&'.format(pathdelay['input_port']) + timing['when']
                else:
                    timing['when'] = '!{}'.format(pathdelay['input_port'])
            if pathdelay['edge'] == 'posedge':
                timing['timing_type'] = 'rising_edge'
            elif pathdelay['edge'] == 'negedge':
                timing['timing_type'] = 'falling_edge'
            if pathdelay['delaylist']['rise']:
                if float(pathdelay['delaylist']['rise'][0]) == float(pathdelay['delaylist']['rise'][2]):
                    timing['intrinsic_rise'] = pathdelay['delaylist']['rise'][0]
                else:
                    print(f'{pathdelay["delaylist"]["fall"][0]} {pathdelay["delaylist"]["fall"][2]}')
                    timing['intrinsic_rise_min'] = pathdelay['delaylist']['rise'][0]
                    timing['intrinsic_rise'] = pathdelay['delaylist']['rise'][1] if float(pathdelay['delaylist']['rise'][1]) > float(pathdelay['delaylist']['rise'][0]) else pathdelay['delaylist']['rise'][0]
                    timing['intrinsic_rise_max'] = pathdelay['delaylist']['rise'][2]
            if pathdelay['delaylist']['fall']:
                if float(pathdelay['delaylist']['fall'][0]) == float(pathdelay['delaylist']['fall'][2]):
                    timing['intrinsic_fall'] = pathdelay['delaylist']['fall'][0]
                else:
                    print(f'{pathdelay["delaylist"]["fall"][0]} {pathdelay["delaylist"]["fall"][2]}')
                    timing['intrinsic_fall_min'] = pathdelay['delaylist']['fall'][0]
                    timing['intrinsic_fall'] = pathdelay['delaylist']['fall'][1] if float(pathdelay['delaylist']['fall'][1]) > float(pathdelay['delaylist']['fall'][0]) else pathdelay['delaylist']['fall'][0]
                    timing['intrinsic_fall_max'] = pathdelay['delaylist']['fall'][2]
            if pathdelay['edge'] not in ['posedge', 'negedge']:
                timing['timing_type'] = 'rising_edge'
                librarycontent[cell][pinname]['timing '].append(timing.copy())
                timing['timing_type'] = 'falling_edge'
                librarycontent[cell][pinname]['timing '].append(timing)
            else:
                librarycontent[cell][pinname]['timing '].append(timing)
        for constraintcheck in entry['constraintchecks']:
            if constraintcheck['type'] in ['setup', 'hold', 'skew', 'recovery']:
                pinname = 'pin {}'.format(constraintcheck['data_event']['signals'][0])
                if not pinname in librarycontent[cell]:
                    librarycontent[cell][pinname] = {}
                if not 'timing ' in librarycontent[cell][pinname]:
                    librarycontent[cell][pinname]['timing '] = []
                timing = {}
                if constraintcheck['data_event']['edge'] == 'posedge':
                    if float(constraintcheck['limit'][0]) == float(constraintcheck['limit'][2]):
                        timing['intrinsic_rise'] = constraintcheck['limit'][0]
                    else:
                        timing['intrinsic_rise_min'] = constraintcheck['limit'][0]
                        timing['intrinsic_rise'] = constraintcheck['limit'][1] if float(constraintcheck['limit'][1]) > float(constraintcheck['limit'][0]) else constraintcheck['limit'][0]
                        timing['intrinsic_rise_max'] = constraintcheck['limit'][2]
                if constraintcheck['data_event']['edge'] == 'negedge':
                    if float(constraintcheck['limit'][0]) == float(constraintcheck['limit'][2]):
                        timing['intrinsic_fall'] = constraintcheck['limit'][0]
                    else:
                        timing['intrinsic_fall_min'] = constraintcheck['limit'][0]
                        timing['intrinsic_fall'] = constraintcheck['limit'][1] if float(constraintcheck['limit'][1]) > float(constraintcheck['limit'][0]) else constraintcheck['limit'][0]
                        timing['intrinsic_fall_max'] = constraintcheck['limit'][2]
                if len(constraintcheck['data_event']['signals']) > 1:
                    cond = '&'.join(constraintcheck['data_event']['signals'][1:])
                    timing['when'] = cond
                timing['timing_type'] = '{}_{}'.format(constraintcheck['type'], 'rising' if constraintcheck['reference_event']['edge'] == 'posedge' else 'falling')
                timing['related_pin'] = constraintcheck['reference_event']['signals'][0]
                librarycontent[cell][pinname]['timing '].append(timing)
            elif constraintcheck['type'] in ['setuphold', 'recrem']:
                pinname = 'pin {}'.format(constraintcheck['data_event']['signals'][0])
                if not pinname in librarycontent[cell]:
                    librarycontent[cell][pinname] = {}
                if not 'timing ' in librarycontent[cell]:
                    librarycontent[cell][pinname]['timing '] = []
                timing = {}
                timing['related_pin'] = constraintcheck['reference_event']['signals'][0]
                limit = 'setup_limit' if constraintcheck['type'] == 'setuphold' else 'recovery_limit'
                if constraintcheck['data_event']['edge'] == 'posedge':
                    if float(constraintcheck[limit][0]) == float(constraintcheck[limit][2]):
                        timing['intrinsic_rise'] = constraintcheck[limit][0]
                    else:
                        timing['intrinsic_rise_min'] = constraintcheck[limit][0]
                        timing['intrinsic_rise'] = constraintcheck[limit][1] if float(constraintcheck[limit][1]) > float(constraintcheck[limit][0]) else constraintcheck[limit][0]
                        timing['intrinsic_rise_max'] = constraintcheck[limit][2]
                if constraintcheck['data_event']['edge'] == 'negedge':
                    if float(constraintcheck[limit][0]) == float(constraintcheck[limit][2]):
                        timing['intrinsic_fall'] = constraintcheck[limit][0]
                    else:
                        timing['intrinsic_fall_min'] = constraintcheck[limit][0]
                        timing['intrinsic_fall'] = constraintcheck[limit][1] if float(constraintcheck[limit][1]) > float(constraintcheck[limit][0]) else constraintcheck[limit][0]
                        timing['intrinsic_fall_max'] = constraintcheck[limit][2]
                if len(constraintcheck['data_event']['signals']) > 1:
                    cond = '&'.join(constraintcheck['data_event']['signals'][1:])
                    timing['when'] = cond
                timing['timing_type'] = '{}_{}'.format(
                        'setup' if constraintcheck['type'] == 'setuphold' else 'recovery',
                        'rising' if constraintcheck['reference_event']['edge'] == 'posedge' else 'falling')
                librarycontent[cell][pinname]['timing '].append(timing)

                timing = {}
                timing['related_pin'] = constraintcheck['reference_event']['signals'][0]
                limit = 'hold_limit' if constraintcheck['type'] == 'setuphold' else 'removal_limit'
                if constraintcheck['data_event']['edge'] == 'posedge':
                    if float(constraintcheck[limit][0]) == float(constraintcheck[limit][2]):
                        timing['intrinsic_rise'] = constraintcheck[limit][0]
                    else:
                        timing['intrinsic_rise_min'] = constraintcheck[limit][0]
                        timing['intrinsic_rise'] = constraintcheck[limit][1] if float(constraintcheck[limit][1]) > float(constraintcheck[limit][0]) else constraintcheck[limit][0]
                        timing['intrinsic_rise_max'] = constraintcheck[limit][2]
                if constraintcheck['data_event']['edge'] == 'negedge':
                    if float(constraintcheck[limit][0]) == float(constraintcheck[limit][2]):
                        timing['intrinsic_fall'] = constraintcheck[limit][0]
                    else:
                        timing['intrinsic_fall_min'] = constraintcheck[limit][0]
                        timing['intrinsic_fall'] = constraintcheck[limit][1] if float(constraintcheck[limit][1]) > float(constraintcheck[limit][0]) else constraintcheck[limit][0]
                        timing['intrinsic_fall_max'] = constraintcheck[limit][2]
                if len(constraintcheck['data_event']['signals']) > 1:
                    cond = '&'.join(constraintcheck['data_event']['signals'][1:])
                    timing['when'] = cond
                timing['timing_type'] = '{}_{}'.format(
                        'hold' if constraintcheck['type'] == 'setuphold' else 'removal',
                        'rising' if constraintcheck['reference_event']['edge'] == 'posedge' else 'falling')
                librarycontent[cell][pinname]['timing '].append(timing)
            elif constraintcheck['type'] == 'period':
                pinname = 'pin {}'.format(constraintcheck['reference_event']['signals'][0])
                if not pinname in librarycontent[cell]:
                    librarycontent[cell][pinname] = {}
                if not 'minimum_period ' in librarycontent[cell]:
                    librarycontent[cell][pinname]['minimum_period '] = []
                period = {}

                if len(constraintcheck['reference_event']['signals']) > 1:
                    period['when'] = '&'.join(constraintcheck['reference_event']['signals'][1:])

                constraint_attr = 'constraint'
                limit = 'limit'
                period['{}_min'.format(constraint_attr)] = constraintcheck[limit][0]
                period['{}'.format(constraint_attr)] = constraintcheck[limit][1]
                period['{}_max'.format(constraint_attr)] = constraintcheck[limit][2]
                librarycontent[cell][pinname]['minimum_period '].append(period)
            else:
                pinname = 'pin {}'.format(constraintcheck['reference_event']['signals'][0])
                if not pinname in librarycontent[cell]:
                    librarycontent[cell][pinname] = {}
                limit = 'width_limit'
                librarycontent[cell][pinname]['min_pulse_width_low'] = constraintcheck[limit][0]
                librarycontent[cell][pinname]['min_pulse_width_high'] = constraintcheck[limit][2]

        if len(librarycontent[cell]) == 0:
            del librarycontent[cell]
    if len(librarycontent) > 0:
        library = {'library {}'.format(libraryname): librarycontent}
        return library
    else:
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input",
        help="Input Verilog file",
        type=Path)
    parser.add_argument(
        "library_name",
        help="Library name for Liberty file",
        type=str)
    parser.add_argument(
        "output",
        help="Output Liberty file",
        type=Path)
    parser.add_argument(
        "--print",
        help="Prints additional info",
        action="store_true")

    args = parser.parse_args()

    with open(args.input, 'r') as f:
        veriloglines = f.readlines()
    extractor = extract_timings.VerilogSpecifyExtractor(veriloglines)
    extractor.parse()
    if args.print:
        print('-------------------')
        print(''.join(veriloglines))
        print('-------------------')
        for module, parsedentry in extractor.parsedspecifyblocks.items():
            print('-------------------')
            print('Module: {}'.format(module))
            print('-------------------')
            print('Specparams')
            for param, value in parsedentry["specparams"].items():
                pp('{} = {}'.format(param, value))
            print('-------------------')
            print('Constraint checks')
            for c in parsedentry["constraintchecks"]:
                pp(c)
            print('-------------------')
            print('Path delays')
            for p in parsedentry["pathdelays"]:
                pp(p)
            print('-------------------')
            print('Conditioned path delays')
            for v in parsedentry["ifstatements"].values():
                for e in v:
                    pp(e)

    if len(extractor.parsedspecifyblocks) > 0:
        jsonliberty = convert_specify_to_libertyjson(args.library_name, extractor.parsedspecifyblocks)
        if jsonliberty:
            liblines = json_to_liberty.JSONToLibertyWriter.convert_json_to_liberty(jsonliberty)
            if liblines:
                with open(args.output, 'w') as outputlib:
                    outputlib.write('\n'.join(liblines))
        else:
            print('No timings data in specify block')
    else:
        print('No specify block')

if __name__ == '__main__':
    main()
