#!/usr/bin/python3

import glob
from os.path import basename, dirname, isfile

# Code to download data from the Latin Libary .com
from phyllo.phyllo_logger import logger


def main():
    """Extract all the data parameters and create the database."""

    modules = glob.glob(dirname('/Users/cgrant/projects/phyllo/phyllo/extractors/')+"/*.py")
    __all__ = [
        basename(f)[:-3]
        for f in modules
        if isfile(f)
        and not f.endswith('__init__.py')
        and not basename(f).startswith('0')
    ]
    logger.info(__all__)

    # TODO: run all moduless


if __name__ == '__main__':
    main()
