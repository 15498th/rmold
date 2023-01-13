Script to clean up old files created by other programs to prevent them from filling up all disk space.

### What is it for

There are programs used for things like making backups, recording survaliance camera footage or logging some kind of events, that produce output files with noticeable size on regular basics. In order to prevent used disk space from growing up indefinitely, older data should be regularly removed.

This script designed to work with directories, that are created automatically within root directory (set by `--path`) and have specific pattern in name, that can be expressed using regexp (`--pattern` argument). Out of all matching directories found within root it will keep most recent, up to either certain amount of directories (decided with `--keep_last`) or total size (set by `--max_size` argument). 

In order to allow running in multiple root directories containing single pattern at once `--path` argument will expand wildcards.

### Example

Assuming there is a backup job that runs daily and creates folder with name `snapshot-YYYYmmdd` in `/media/backups/`, in order to keep space usage under 10Gb the following arguments could be used:
```bash
rmold.py --path "/media/backups/" --pattern "snapshot-\d{4}\d{2}\d{2}" --max_size 10G
```

[//]: # "autogenerated output begin"

### Usage
```bash
usage: rmold.py [-h] [--verbose] -p PATH [-r PATTERN]
                (-k ITEMS_TO_KEEP | -m MAX_SIZE) [-s {time,name}] [-d]

Remove oldest directories with specified pattern in name.

optional arguments:
  -h, --help            show this help message and exit
  --verbose, -v         output additional debug messages, use -vv for more
                        details
  -p PATH, --path PATH  root directory to search and remove within. Accepts
                        windcards
  -r PATTERN, --pattern PATTERN
                        regexp pattern for directories to include in sorting
                        and deleting, default is \d{4}\d{2}\d{2}
  -k ITEMS_TO_KEEP, --keep-last ITEMS_TO_KEEP
                        how many newest directories to keep
  -m MAX_SIZE, --max-size MAX_SIZE
                        keep newest directories with total size up to given
                        amount
  -s {time,name}, --sort-by {time,name}
                        what attribute directories should be ordered by before
                        deleting
  -d, --dry-run         print directories instead of deleting them
```

[//]: # "autogenerated output end"

