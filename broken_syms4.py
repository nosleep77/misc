#!/usr/bin/env python3

import os
import shutil

MIGR_PATHS_INP_FILE_NAME = 'in.txt'
RETR_BASE_DIR = '/var/COOL/arscache1/odwmprod/retr/'
MIGR_SAVE_DIR = '/v/region/na/appl/ilink/wmcmod/data/archive01/SAVE-migr'
LOG_DIR = '/var/tmp/migr_move_output/'


def handle_migr(migr_path):
    log(f"checking migr {migr_path}")

    # if this link does not exist then move to next symlink in file
    if not os.path.lexists(migr_path):
        log(f"skip migr {migr_path}: migr path doesn't exist")
        return

    # if this is NOT a symlink then move to next symlink in file
    if not os.path.islink(migr_path):
        log(f"skip migr {migr_path}: migr is not a symlink")
        return

    # if this link is NOT broken then move to next symlink in file
    if link_is_valid_not_brk(migr_path):
        # good link, but we are after dangling ones
        log(f"skip migr {migr_path}: migr is valid symlink")
        return
    else:
        log(f"migr {migr_path} is broken link, continuing")

    # now we know migr is link and it is broken

    # check where this broken link resolves to has DOC or RES
    brk_migr_targ = resolve_to_abs_non_recusive(migr_path)
    log(f"migr {migr_path} resolves to {brk_migr_targ}")
    spl = splitall(brk_migr_targ)
    doc_or_res = next((x for x in spl if x in ('DOC', 'RES')), None)
    if doc_or_res is None:
        log(f"skip migr {migr_path}: no DOC or RES in migr targ path")
        return
    else:
        log(f"migr targ includes {doc_or_res}")

    retr_path = retr_path_by_broken_migr_targ(brk_migr_targ)
    log(f"checking retr {retr_path}")

    # if the retr link does not exist then move to next migr
    # symlink in file (print reason)
    if not os.path.lexists(retr_path):
        log(f"skip migr {migr_path}: retr {retr_path} does not exists")
        return

    # if the retr link is not a symlink then move to next migr
    # symlink in file (print reason)
    if not os.path.islink(retr_path):
        log(f"skip migr {migr_path}: retr {retr_path} is not symlink")
        return

    retr_targ = resolve_to_abs_non_recusive(retr_path)

    log(f"retr {retr_path} resolves to {retr_targ}")

    # if it [retr] does NOT resolve to a valid path ... move to next migr
    if not link_is_valid_not_brk(retr_path):
        log(f"skip migr {migr_path}: retr {retr_path} is broken symlink")
        return

    cache_migr_substr = '/cache_migr/'
    # if ... the path [it resolves to] doesn't contain 'cache_migr' then move to next migr
    if not cache_migr_substr in retr_targ:
        log(
            f"skip migr {migr_path}: retr_targ {retr_targ} does not include '{cache_migr_substr}'")
        return

    log(f"retr {retr_path} resolves to path which includes '{cache_migr_substr}'")

    move_into_dir(migr_path, MIGR_SAVE_DIR)


def retr_path_by_broken_migr_targ(broken_migr_targ):
    """
    takes   /d/ny042nas01/d56/arscache206/odwmprod/19008/ACQ/DOC/804509IAAA
    returns /var/COOL/arscache1/odwmprod/retr/ACQ/DOC/804509IAAA
    essentially it's RETR_BASE_DIR + /ACQ/DOC/804509IAAA
    """
    # last_three_components: ['ACQ', 'DOC', '804509IAAA']
    last_three_components = splitall(broken_migr_targ)[-3:]

    if last_three_components[1] not in ('RES', 'DOC'):
        raise Exception("last_three_components[1] not in ('RES', 'DOC')")

    return os.path.join(RETR_BASE_DIR, *last_three_components)


def get_file_name(path):
    return os.path.split(path)[1]


def move_into_dir(migr, save_dir):
    #log(f"moving migr {migr} to dir {MIGR_SAVE_DIR}")

    check_save_dir(save_dir)
    if not os.path.islink(migr):
        raise Exception(f"ERROR {migr} - migr is expected to be a symlink")

    migr_filename_only = get_file_name(migr)
    expected_full_save_path = os.path.join(save_dir, migr_filename_only)

    if os.path.lexists(expected_full_save_path):
        # something was already saved in save_dir
        migr_targ = resolve_to_abs_non_recusive(migr)
        existing_f_in_savedir_is_link = os.path.islink(expected_full_save_path)
        if existing_f_in_savedir_is_link:
            existing_f_in_savedir_targ = resolve_to_abs_non_recusive(expected_full_save_path)
            # check if it resolves to same path as migr resolves to
            if existing_f_in_savedir_targ == migr_targ:
                log(f"equivalent link already exists in save dir: {expected_full_save_path}")
                # delete migr_link
                if do_work:
                    os.unlink(migr)
                log(f"deleted migr {migr}", dry_run_prefix=True)
            else:
                log(f"ERROR: save_path {expected_full_save_path} already "
                    f"exists, it's symlink (non equivalent to migr)")
                log(
                    f"ERROR: save_path {expected_full_save_path} resolves "
                    f"to {existing_f_in_savedir_targ}")
                log(f"ERROR: migr {migr} resolves to {migr_targ}")
        else:
            log(f"ERROR: {expected_full_save_path} already exists, not link")
    else:
        if do_work:
            shutil.move(migr, save_dir)
        log(f"migr moved {migr} new path: {expected_full_save_path}", dry_run_prefix=True)


def check_save_dir(save_dir):
    if not os.path.exists(save_dir):
        m = f"save_dir {save_dir} doesn't exist"
        log(m)
        err_halt(m)

    if not os.path.isdir(save_dir):
        m = f"save_dir {save_dir} is not a directory"
        log(m)
        err_halt(m)


def splitall(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path:  # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts


def link_is_valid_not_brk(path, recursive=False):
    import os
    if not os.path.lexists(path):
        raise ValueError("path doesn't exist")

    if not os.path.islink(path):
        raise ValueError("path is not symlink")

    if recursive:
        # for links, os.path.exists() checks if link is resolvable
        # to existing path.
        # but os.path.exists() does this recursively.
        return os.path.exists(path)
    else:
        readlink_r_abs = resolve_to_abs_non_recusive(path)
        return os.path.lexists(readlink_r_abs)


def resolve_to_abs_non_recusive(path):
    import os
    readlink_result = os.readlink(path)
    if not os.path.isabs(readlink_result):
        readlink_result_abs = os.path.join(os.path.dirname(path), readlink_result)
    else:
        readlink_result_abs = readlink_result

    return readlink_result_abs


def log(msg, dry_run_prefix=False, timestamp=False):
    if dry_run_prefix:
        prefix = 'dry-run: ' if (not do_work) else 'action: '
        msg = prefix + msg

    if timestamp:
        import datetime
        ts = datetime.datetime.now().astimezone().isoformat(timespec='seconds', sep=' ')
        msg = f"{ts} {msg}"
    print(msg)
    log_file.write(msg + "\n")
    log_file.flush()


def err_halt(m):
    import sys
    sys.stderr.write(str(m) + "\n")
    sys.exit(1)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", help="dry-run", action='store_true')
    group.add_argument("--do-work", help="made changes", action='store_true')
    args = parser.parse_args()

    global do_work
    do_work = args.do_work

    import datetime
    log_file_dt_str = datetime.datetime.now().astimezone().strftime('%Y_%m_%d_%I_%M_%S%p')
    if not os.path.exists(LOG_DIR):
        err_halt(f"{LOG_DIR} does not exist")
    log_path = os.path.join(LOG_DIR, log_file_dt_str)
    global log_file
    log_file = open(log_path, 'w')

    print(f"log_path: {log_path}")
    log('-' * 40)
    log('started', timestamp=True)
    if not do_work:
        log('dry-run mode')

    check_save_dir(MIGR_SAVE_DIR)
    in_file = open(MIGR_PATHS_INP_FILE_NAME)
    while (line := in_file.readline()) != "":
        line = line.strip()
        if line.strip() == "":
            continue
        log('-' * 40)
        handle_migr(line)
    log('-' * 40)
    log('finished', timestamp=True)


if __name__ == "__main__":
    main()
