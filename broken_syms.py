#!/usr/bin/env python3

import os
import re


def main():
    in_file_names = load_file(open('in.txt').read())
    for in_file_name in in_file_names:
        print('-' * 40)
        migr_path = in_file_name
        migr_fname = splitall(migr_path)[-1] # ACQ767068IAAA.80.0

        # >>> re.search('([A-Z]{3})(\w+)', 'ACQ767068IAAA.80.0').groups()
        # ('ACQ', '767068IAAA')
        three_letters, rest_alnum = re.search('([A-Z]{3})(\w+)', migr_fname).groups()
        print(f"{migr_path} -> {three_letters}, {rest_alnum}")

        # spec /var/COOL/arscache1/odwmprod/retr/ACQ/DOC/767068IAAA
        #  act /var/COOL/arscache1/odwmprod/retr/ACQ/DOC/767068IAAA
        retr_path = os.path.join(
            '/var/COOL/arscache1/odwmprod/retr/',
            three_letters,
            'DOC',
            rest_alnum
        )
        print(retr_path)

        # /var/COOL/arscache1/odwmprod/retr/OQN/DOC/744FAAA
        if not os.path.lexists(retr_path):
            print(f"ERROR {retr_path} - doesn't exist")
            continue

        if not os.path.islink(retr_path):
            print(f"ERROR {retr_path} - not symlink")
            continue

        if not os.path.exists(retr_path):
            print(f"ERROR {retr_path} - broken symlink")
            continue

        retr_resolved_path = os.path.realpath(retr_path)
        print(f"{retr_path} -> {retr_resolved_path}")

        if 'cache_migr' in retr_resolved_path:
            # ... then delete the related migr dir (NOT the retr)
            print(f"DELETING {migr_path}")

            if not os.path.islink(migr_path):
                print(f"ERROR {migr_path} - migr is expected to be a symlink")
                continue

            # uncomment this to actually delete, or we can add --dry-run option:
            # os.remove(migr_path)

        else:
            print(f"SKIP {migr_path}")


def load_file(file_data):
    lines = []
    for line in file_data.splitlines():
        stripped = line.strip()
        if stripped == "":
            continue
        lines.append(stripped)
    return lines


def splitall(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts


if __name__ == "__main__":
    main()
