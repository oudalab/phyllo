#!/usr/bin/python3

# Code to download data from the Latin Libary .com
from phyllo.extractors import abelardDB
from phyllo.extractors import ammianusDB
from phyllo.extractors import apuleiusDB
from phyllo.extractors import augustusDB
from phyllo.extractors import aureliusDB
from phyllo.extractors import caesarDB
from phyllo.extractors import cassiodorusDB
from phyllo.extractors import catoElderDB
from phyllo.extractors import catullusDB
from phyllo.extractors import ciceroDB
from phyllo.extractors import claudianDB
from phyllo.extractors import curtiusDB
from phyllo.extractors import enniusDB
from phyllo.extractors import eutropiusDB
from phyllo.extractors import florusDB
from phyllo.extractors import frontinusDB
from phyllo.extractors import gestafrancDB
from phyllo.extractors import horaceDB
from phyllo.extractors import hugoDB
from phyllo.extractors import justinDB
from phyllo.extractors import juvenalDB
from phyllo.extractors import livyDB
from phyllo.extractors import lucanDB
from phyllo.extractors import lucretiusDB
from phyllo.extractors import martialDB
from phyllo.extractors import neposDB
from phyllo.extractors import ovidDB
from phyllo.extractors import persiusDB
from phyllo.extractors import petroniusDB
from phyllo.extractors import phaedrusDB
from phyllo.extractors import plinymaiorDB
from phyllo.extractors import plinyminorDB
from phyllo.extractors import propertiusDB
from phyllo.extractors import quintilianDB
from phyllo.extractors import sallustDB
from phyllo.extractors import statiusDB
from phyllo.extractors import wtyreDB

import phyllo.phyllo_logger
from phyllo.phyllo_logger import logger


def main():
    """Extract all the data parameters and create the database."""
    logger.info("Extracting belardDB.")
    abelardDB.main()
    ammianusDB.main()
    apuleiusDB.main()
    augustusDB.main()
    aureliusDB.main()
    caesarDB.main()
    cassiodorusDB.main()
    catoElderDB.main()
    catullusDB.main()
    ciceroDB.main()
    claudianDB.main()
    curtiusDB.main()
    enniusDB.main()
    eutropiusDB.main()
    florusDB.main()
    frontinusDB.main()
    gestafrancDB.main()
    horaceDB.main()
    hugoDB.main()
    justinDB.main()
    juvenalDB.main()
    livyDB.main()
    lucanDB.main()
    lucretiusDB.main()
    martialDB.main()
    neposDB.main()
    ovidDB.main()
    persiusDB.main()
    petroniusDB.main()
    phaedrusDB.main()
    plinymaiorDB.main()
    plinyminorDB.main()
    propertiusDB.main()
    quintilianDB.main()
    sallustDB.main()
    statiusDB.main()
    wtyreDB.main()


if __name__ == '__main__':
    main()
