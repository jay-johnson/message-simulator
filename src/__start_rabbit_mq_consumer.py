#!/usr/bin/python

# System Imports
import os, sys, json, inspect, uuid, argparse, datetime, logging, copy
from time import sleep

# Local Imports
from logger                     import Logger
from utils                      import *
from rabbit_message_consumer    import RabbitMessageConsumer


#####################################################################
#
# Start Arg Processing:
#
action              = "Run Rabbit Consumer"
parser              = argparse.ArgumentParser(description="Parser for: " + str(action))
parser.add_argument('-f', '--consumerfile', required=True, dest='simfile', help='Run Consumer')
parser.add_argument('-d', '--debug',    help='Debug Flag')
args                = parser.parse_args()

path_to_test        = "./NOTREAL"
debug               = True

if args.simfile:
    path_to_test    = str(args.simfile)

if args.debug:
    debug = True
#
# End Arg Processing
#
#####################################################################


if os.path.isfile(path_to_test) == False:
    lg("\nERROR: Did not find Consumer File at Path(" + str(path_to_test) + ")\n", 0)
    sys.exit(1) 

else:
    lg("", 6)
    lg("Running RabbitConsumer(" + str(path_to_test) + ")", 5)
    lg("", 6)

    test_config         = json.loads(open(path_to_test, "r").read())
    exit_status         = 1
    summary_report      = {}
    debug               = False
    logger              = None
    logger              = Logger("RC", "/dev/log", logging.DEBUG)
    consumer            = RabbitMessageConsumer(test_config["Simulation"], logger, debug)

    consumer.run()

    lg("Done RabbitConsumer(" + str(path_to_test) + ")", 6)
    lg("", 6)

    sys.exit(exit_status)
# end of processing










