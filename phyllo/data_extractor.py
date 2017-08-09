#!/usr/bin/python3
""" This loads every module and extracts all data.
"""


import glob
from os.path import basename, dirname, isfile
from multiprocessing import Pool

import importlib
import pkgutil


from phyllo import extractors
from phyllo.phyllo_logger import logger


def main_old():
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


def worker(module_name):
    # Get the module to load
    m = importlib.import_module(module_name)
    try:
        # Load the module (this is time consuming)
        m.main()
    except:
        try:
            logger.error("Error extracting from {} -- {}".format(module_name),
                         sys.exc_info()[0])
        except:
            logger.error("Error retrieving the broken module info from {}".format(module_name))
        finally:
            return 1

    return 0


def main():

    error_count = 0
    prefix = "phyllo.extractors."
    modules = (m for _, m, _
               in pkgutil.iter_modules(extractors.__path__, prefix)
               if not m.startswith(prefix+"0_"))
    with Pool(1) as p:
        error_count = sum(p.imap_unordered(worker, modules))

    logger.info("Extraction Complete. Error count: {}".format(error_count))


if __name__ == '__main__':
    main()
