#!/usr/bin/python3

import glob
from os.path import basename, dirname, isfile

import importlib
import pkgutil
# This is for importlib.import_module("extractor.<something>")

from phyllo import extractors
from phyllo.phyllo_logger import logger


def main():
    """Extract all the data parameters and create the database."""

    error_count = 0
    prefix = "phyllo.extractors."
    for importer, modname, ispackage in pkgutil.iter_modules(extractors.__path__, prefix):
        # Ignore the templates
        if not modname.startswith(prefix+"0_"):
            print(modname)
            m = importlib.import_module(modname)
            try:
                m.main()
            except:
                error_count += 1
                logger.error("Error extracting from {} -- {}".format(modname),
                             sys.exc_info()[0])

    logger.info("Extraction Complete. Error count: {}".format(error_count))

if __name__ == '__main__':
    main()
