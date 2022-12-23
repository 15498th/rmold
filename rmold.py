#!/usr/bin/env python3

import argparse
import glob
import logging
import os
from pathlib import Path
import re
import shutil

BASE_DIR = '/media/motion/**/**/'
ITEM_PATTERN = r'\d{4}\d{2}\d{2}'
SORT_BY = 'time'

get_attr = {
        'time': os.path.getmtime,
        'name': os.path.basename
        }

def set_logger(log_level):
    log_format = '%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s'
    datefmt = '%Y/%m/%d %H:%M:%S'
    logging.basicConfig(level=log_level, format=log_format, datefmt=datefmt)

def get_size(path):
    '''return total size of files and directories in given path, don't follow symlinks
    (on some python versions will fail if symlink pointing to itself encountered,
    see https://bugs.python.org/issue36035)'''
    return sum(item.lstat().st_size for item in Path(path).glob('**/*'))

def parse_size(text):
    base = 1000
    units = {'K': base**1, 'M': base**2, 'G': base**3, 'T': base**4}
    pattern = r'(\d+)\s*({})'.format('|'.join(units.keys()))
    if text.isdecimal():
        return int(text)
    match = re.fullmatch(pattern, text)
    if match is not None:
        value, unit = match.groups()
        return int(value) * units[unit]
    error_message = 'failed to parse size: must me integer with possible modifiers [{}]'
    raise ValueError(error_message.format(', '.join(units.keys())))

def remove_dir(path):
    if not os.access(path, os.W_OK):
        # don't try to delete non-writeable to reduce log spam
        logging.warn(f'no write access to {path}, skipping')
        return
    def log_rmtree_error(_, path, exc_info):
        (_, e, _) = exc_info
        logging.warn(e)
    shutil.rmtree(path, onerror=log_rmtree_error)

def expand_base_dir(base_dir):
    target_directories = glob.glob(base_dir)
    logging.debug(f'expanding {base_dir} to {target_directories}')
    return target_directories

def select_directories(base_dir, pattern):
    working_directory = Path(base_dir)
    items = []
    for item in working_directory.iterdir():
        if re.fullmatch(pattern, item.name):
            items.append(item)
    logging.debug(f'found {len(items)} matches for {pattern} in {base_dir}')
    return items

def remove_directories(directories):
        for item in directories:
            logging.debug('remove %s' % item)
            remove_dir(item)

def split_by_total_size(directories, size):
    position = 0
    cumulative = 0
    while cumulative <= size:
        if position < len(directories):
            cumulative += get_size(directories[position])
            position += 1
        else:
            break
    return directories[:position], directories[position:]

def main():
    info = {}
    description = 'Remove oldest directories with specified pattern in name.'
    parser = argparse.ArgumentParser(description=description)
    info['v'] = 'output additional debug messages, use -vv for more details'
    parser.add_argument('--verbose', '-v', action='count', default=0, help=info['v'])
    info['p'] = 'root directory to search and remove within. Accepts windcards'
    parser.add_argument('-p', '--path', required=True, metavar='BASE_DIR', help=info['p'])
    info['r'] = 'regexp pattern for directories to include in sorting and deleting, default is %(default)s'
    parser.add_argument('-r', '--pattern', default=ITEM_PATTERN, help=info['r'])
    criteria = parser.add_mutually_exclusive_group(required=True)
    info['k'] = 'how many newest directories to keep'
    criteria.add_argument('-k', '--keep_last', type=int, metavar='ITEMS_TO_KEEP', help=info['k'])
    info['m'] = 'keep newest directories with total size up to given amount\n'
    criteria.add_argument('-m', '--max_size', type=parse_size, help=info['m'])
    info['s'] = 'what attribute directories should be ordered by before deleting'
    parser.add_argument('-s', '--sort_by', choices=get_attr.keys(), default=SORT_BY, help=info['s'])
    args = parser.parse_args()

    if args.verbose > 1:
        log_level = logging.DEBUG
    elif args.verbose > 0:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING
    set_logger(log_level)

    base_path = args.path
    pattern = args.pattern
    items_to_keep = args.keep_last
    size_to_keep = args.max_size
    sort_key = get_attr[args.sort_by]

    for base_dir in expand_base_dir(base_path):
        items = select_directories(base_dir, pattern)
        items_total = len(items)
        items.sort(key=sort_key, reverse=False)
        if items_to_keep is not None:
            to_be_removed = items[:items_to_keep]
        elif size_to_keep is not None:
            to_keep, to_be_removed = split_by_total_size(items, size_to_keep)
            logging.debug('keep %d items with size of %.0fM' % (len(to_keep), sum(get_size(path) for path in to_keep)/1000**2))
        else:
            raise Exception('either size or number of directories to keep should be specified')

        logging.info('remove {}/{} items in {}'.format(len(to_be_removed), items_total, base_dir))
        remove_directories(to_be_removed)


if __name__ == '__main__':
    main()
