#!/usr/bin/env python2.7

from collections import Counter, defaultdict

CONSULT_DIR = '/admin/consult/'
DATA_DIR = CONSULT_DIR + 'data/'
# { warning_name: (short_name, short_flag, file_path) }
WARNING_METADATA = {
    'food-warnings': ('food', 'f', DATA_DIR + 'food-warnings'),
    'printer-warnings': ('print', 'p', DATA_DIR + 'printer-warnings')
}

def main():
    warnings = defaultdict(dict)
    for name, (_, _, file_path) in WARNING_METADATA.iteritems():
        for (consultant, num_warned) in count_warnings(file_path).iteritems():
            warnings[consultant][name] = num_warned
    print_warnings(WARNING_METADATA, warnings)

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
