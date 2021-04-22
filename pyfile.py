#!/usr/bin/env python3

import os
import re
import sys
import shutil

def main():
    in_file_names = load_file(open('in.txt').read())

    save_migr_dir = '/v/region/na/appl/ilink/wmcmod/data/archive01/SAVE-migr'

    for in_file_name in in_file_names:
        print('-' * 40)
        migr_path = in_file_name
        migr_fname = splitall(migr_path)[-1] # ACQ767068IAAA.80.0

        # >>> re.search('([A-Z]{3})(\w+)', 'ACQ767068IAAA.80.0').groups()
        # ('ACQ', '767068IAAA')
        three_letters, rest_alnum = re.search('([A-Z]{3})(\w+)', migr_fname).groups()
        print(f"{migr_path} -> {three_letters}, {rest_alnum}")

        # /var/COOL/arscache1/odwmprod/retr/ACQ/DOC/767068IAAA
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
        print(f"{retr_path} resolves to {retr_resolved_path}")


        if 'cache_migr' in retr_resolved_path:
            # ... then delete the related migr dir (NOT the retr)
            print(f"MOVING {migr_path}")


            if not os.path.exists(migr_path):
                print(f"ERROR {migr_path} - migr doesn't exist")
                continue

            if not os.path.islink(migr_path):
                print(f"ERROR {migr_path} - migr is expected to be a symlink")
                continue

            move_into_dir(migr_path, save_migr_dir)

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


def move_into_dir(src, dst_dir):
    if not os.path.exists(dst_dir):
        raise Exception(f"{dst_dir} doesn't exist")

    if not os.path.isdir(dst_dir):
        raise Exception(f"{dst_dir} is not a directory")

    if not os.path.exists(src):
        raise Exception(f"{src} doesn't exist")

    src_last_component = ([c for c in splitall(src) if c != ''])[-1]

    # /v/region/na/appl/ilink/wmcmod/data/archive01/SAVE-migr/ACQ767068IAAA.80.0
    expected_full_dst_path = os.path.join(dst_dir, src_last_component)

    print(f"MOVING {src} to {expected_full_dst_path}")

    # uncomment this to perform the action

    # if os.path.exists(expected_full_dst_path):
    #     os.remove(expected_full_dst_path)
    # shutil.copy(src, dst_dir, follow_symlinks=False)
    # os.unlink(src)


if __name__ == "__main__":
    main()
