"""
Custom logging set up, with handlers for writing to .log file and console.

The _handler.setLevel determines the logging level to write to file or console.
Logging levels are:

Level	Numeric value
CRITICAL	50
ERROR	    40
WARNING	    30
INFO	    20
DEBUG	    10
NOTSET	    0
"""
import logging
import os

log = logging.getLogger('reopt_api')
log.setLevel(logging.DEBUG)

logfile = os.path.join(os.getcwd(), "log", "reopt_api.log")

file_handler = logging.FileHandler(filename=logfile, mode='a')
file_formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(filename)s::%(funcName)s line:%(lineno)s %(message)s')
file_handler.setFormatter(file_formatter)
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(name)-12s %(levelname)-8s %(filename)s %(funcName)s %(lineno)s %(message)s')
console_handler.setFormatter(console_formatter)
console_handler.setLevel(logging.DEBUG)

log.addHandler(file_handler)
log.addHandler(console_handler)