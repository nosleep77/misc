#!/usr/bin/env python3

import os
import re


def main():
    in_file_names = load_file(open('in.txt').read())
    for in_file_name in in_file_names:
        print('-' * 40)
        
        # ./18321/ACQ767068IAAA.80.8 -> 18321/ACQ767068IAAA.80.8
        dot_slash_removed = re.sub(r'^\./', '', in_file_name)
        print(dot_slash_removed)

        # spec /var/COOL/arscache1/odwmprod/migr/18321/ACQ767068IAAA.80.0
        #  act /var/COOL/arscache1/odwmprod/migr/18321/ACQ767068IAAA.80.8
        migr_path = os.path.join('/var/COOL/arscache1/odwmprod/migr/', dot_slash_removed)
        print(migr_path)

        # >>> re.search('(?<=/)([A-Z]{3})(\w+)', '18321/ACQ767068IAAA.80.8').groups()
        # ('ACQ', '767068IAAA')
        three_letters, rest_alnum = re.search('(?<=/)([A-Z]{3})(\w+)', dot_slash_removed).groups()
        print(f"{migr_path} -> {three_letters}, {rest_alnum}")

        # spec /var/COOL/arscache1/odwmprod/retr/ACQ/DOC/767068IAAA
        #  act /var/COOL/arscache1/odwmprod/retr/ACQ/DOC/767068IAAA
        at_retr_path = os.path.join(
            '/var/COOL/arscache1/odwmprod/retr/',
            three_letters,
            'DOC',
            rest_alnum
        )
        print(at_retr_path)

        # /var/COOL/arscache1/odwmprod/retr/ACQ/DOC/744FAAA
        # /var/COOL/arscache1/odwmprod/retr/OQN/DOC/744FAAA
        if not os.path.lexists(at_retr_path):
            print(f"ERROR {at_retr_path} - doesn't exist")
            continue

        if not os.path.islink(at_retr_path):
            print(f"ERROR {at_retr_path} - not symlink")
            continue

        if not os.path.exists(at_retr_path):
            print(f"ERROR {at_retr_path} - broken symlink")
            continue

        retr_resolved_path = os.path.realpath(at_retr_path)
        print(f"{at_retr_path} -> {retr_resolved_path}")

        if 'cache_migr' in retr_resolved_path:
            # ... then delete the related migr dir (NOT the retr)
            print(f"DELETING {migr_path}")
            if os.path.islink(migr_path) or (not os.path.isdir(migr_path)):
                print(f"ERROR {migr_path} - not a directory. or it's a symlink itself")
                continue

            # uncomment this to actually delete, or we can add --dry-run option:
            # shutil.rmtree(migr_path)

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


if __name__ == "__main__":
    main()
