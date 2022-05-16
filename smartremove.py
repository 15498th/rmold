#!/usr/bin/env python3

import argparse
import logging
import glob
import os
import re
from pathlib import Path
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

def remove_dir(path):
    if not os.access(path, os.W_OK):
        # don't try to delete non-writeable to reduce log spam
        logging.warn(f'no write access to {path}, skipping')
        return
    def log_rmtree_error(_, path, exc_info):
        (_, e, _) = exc_info
        logging.warn(e)
    shutil.rmtree(path, onerror=log_rmtree_error)

def remove_oldest(base_dir, pattern, items_to_keep, sort_key):
    target_directories = glob.glob(base_dir)
    logging.debug(f'expanding {base_dir} to {target_directories}')
    logging.debug(f'search pattern: {pattern}')
    for working_directory in target_directories:
        working_directory = Path(working_directory)
        items = []
        for item in working_directory.iterdir():
            if re.fullmatch(pattern, item.name):
                items.append(item)
        items.sort(key=sort_key, reverse=True)
        to_be_removed = items[items_to_keep:]
        logging.debug('remove {}/{} items in {}'.format(len(to_be_removed), len(items), working_directory))
        for item in to_be_removed:
            logging.info('remove %s' % item)
            remove_dir(item)

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
    info['k'] = 'how many newest directories to keep'
    parser.add_argument('-k', '--keep_last', required=True, type=int, metavar='ITEMS_TO_KEEP', help=info['k'])
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
    
    base_dir = args.path
    pattern = args.pattern
    keep_last_k = args.keep_last
    sort_key = get_attr[args.sort_by]

    remove_oldest(base_dir, pattern, keep_last_k, sort_key)


if __name__ == '__main__':
    main()
