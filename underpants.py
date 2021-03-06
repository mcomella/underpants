#!/usr/bin/env python2.7

"""
"underpants" is a leaderboard to supplement the Brown CS consultant hours
leaderboard known as "pants". While pants handles hours exclusively, underpants
handles any other statistics that can be found on a leaderboard such as food
warnings and printer warnings given out.

A warning that mantains a data file with the generic line format,

    warned_user timestamp consultant comment

where warned_user = the user who was warned
      timestamp = the unix timestamp at the time of the warning
      consultant = the consultant who warned the user
      comment = the string submitted for the reason of the warning

can be easily added to the output by adding an appropriate entry into the
WARNING_METADATA dict.

"""
from argparse import ArgumentParser
from collections import Counter, defaultdict

CONSULT_DIR = '/admin/consult/'
DATA_DIR = CONSULT_DIR + 'data/'
# { warning_name: (short_name, short_flag, file_path) }
WARNING_METADATA = {
    'food-warnings': ('food', 'f', DATA_DIR + 'food-warnings'),
    'printer-warnings': ('print', 'p', DATA_DIR + 'printer-warnings')
}
DEFAULT_SORT_COL = 'food-warnings'

ACTIVE_CONSULTANT_FILE = DATA_DIR + 'sched/sched.consultnicks'
# Consultant names to be excluded that are read from ACTIVE_CONSULTANT_FILE.
ACTIVE_CONSULTANT_EXCLUSION = set(['FREE', 'HOLIDAY', 'CLOSED'])

def main():
    args = set_and_parse_args(WARNING_METADATA)
    sort_order = get_sort_order(args, WARNING_METADATA)
    warnings = defaultdict(dict)
    for name, (_, _, file_path) in WARNING_METADATA.iteritems():
        for (consultant, num_warned) in count_warnings(file_path).iteritems():
            warnings[consultant][name] = num_warned
    print_warnings(args, WARNING_METADATA, sort_order, warnings)

def set_and_parse_args(metadata):
    parser = ArgumentParser()
    parser.add_argument('-a', '--all', action='store_true',
            help='Show all consultants')
    sort_group = parser.add_mutually_exclusive_group()
    # Add sort arg for each element in metadata generically.
    for warning_name, (short_name, short_flag, _) in metadata.iteritems():
        help_str = '(default sort)' if warning_name == DEFAULT_SORT_COL else \
                None
        sort_group.add_argument('-' + short_flag, '--sort-' + short_name,
                action='store_true', help=help_str)
    return parser.parse_args()

def get_sort_order(args, metadata):
    """Returns an list of warning names written in the order to be sorted."""
    # Set leading column.
    out = []
    for flag_name, flag_is_provided in vars(args).iteritems():
        if 'sort' not in flag_name: continue
        if flag_is_provided:
            flag_name = flag_name[5:] # Remove 'sort_'.
            # Find the full warning name from the flag name.
            for warning_name, (short_name, _, _) in metadata.iteritems():
                if short_name == flag_name:
                    out.insert(0, warning_name)
                    break
            else: assert False
    if len(out) == 0: out.append(DEFAULT_SORT_COL)

    # Insert remaining columns.
    return out + filter(lambda key: key != out[0], metadata.iterkeys())

def count_warnings(file_path):
    """Returns a Counter object with the number of warnings per consultant.

    Counts warnings from the given file, with the expected format given in the
    introductory docstring.

    """
    warnings = Counter()
    with open(file_path) as f:
        for line in f:
            warned_user, timestamp, consultant, comment = line.split(' ', 3)
            warnings[consultant] += 1
    return warnings

def print_warnings(args, metadata, sort_order, warnings):
    # Print header.
    print # Blank.
    out_fmt = ' {:>5} ' * len(sort_order) + ' {}'
    # Fill col_names with warning short_names.
    col_names = map(lambda warning_name: metadata[warning_name][0], sort_order)
    col_names.append('who')
    print out_fmt.format(*tuple(col_names))
    print ' ----- ' * len(sort_order) + ' ---'

    # Print sorted consultant scores.
    if not args.all: warnings = remove_inactive_consultants(warnings)
    sort_col = sort_order[0]
    sorted_warnings = sorted(warnings.iteritems(), reverse=True,
            key=lambda (k, v): v.get(sort_col, 0))
    for consultant, warning_to_num in sorted_warnings:
        # Get the number warned for each warning type for this consultant.
        col_vals = map(lambda warning_name: warning_to_num.get(warning_name,
                0), sort_order)
        col_vals.append(consultant)
        print out_fmt.format(*tuple(col_vals))
    print # Blank.

def remove_inactive_consultants(consultants):
    """Takes {consultant: val} dict and removes inactive consultants.

    Returns a new dict without those inactive consultants.

    """
    active_consultants = set()
    with open(ACTIVE_CONSULTANT_FILE) as f:
        for line in f: active_consultants.add(line.split()[1])
    active_consultants -= ACTIVE_CONSULTANT_EXCLUSION
    consultants = filter(lambda (key, value): key in active_consultants,
            consultants.iteritems())
    return dict(consultants)

if __name__ == '__main__':
    main()
