#!/usr/bin/env python2.7

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

def main():
    args = set_and_parse_args(WARNING_METADATA)
    sort_order = get_sort_order(args, WARNING_METADATA)
    warnings = defaultdict(dict)
    for name, (_, _, file_path) in WARNING_METADATA.iteritems():
        for (consultant, num_warned) in count_warnings(file_path).iteritems():
            warnings[consultant][name] = num_warned
    print_warnings(WARNING_METADATA, warnings)

def set_and_parse_args(metadata):
    parser = ArgumentParser()
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

    Counts warnings from the given file, expecting the file to be of format:

        warned_user timestamp consultant comment

    where warned_user = the user who was warned
          timestamp = the unix timestamp at the time of the warning
          consultant = the consultant who warned the user
          comment = the string submitted for the reason of the warning

    """
    warnings = Counter()
    with open(file_path) as f:
        for line in f:
            warned_user, timestamp, consultant, comment = line.split(' ', 3)
            warnings[consultant] += 1
    return warnings

def print_warnings(metadata, warnings):
    pass

if __name__ == '__main__':
    main()
