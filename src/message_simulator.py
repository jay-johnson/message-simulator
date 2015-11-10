# System Imports
import os, sys, json, inspect, uuid, argparse, datetime, logging, copy, imp, glob
from time import sleep

# Local Imports
from src.logger                     import Logger
from src.utils                      import *
from src.rabbit_message_publisher   import RabbitMessagePublisher


class MessageSimulator:

    def __init__(self, json, logger=None, debug=False):

        # Load Params:
        self.m_config       = json
        self.m_log          = logger
        self.m_debug        = debug

        # Init Members:
        self.m_cur_time     = datetime.datetime.now()
        self.m_is_done      = False
        self.m_sleep_timer  = 1.000
        self.m_pause_timer  = 10.0
        self.m_state        = "Startup"

        # Assign from Config:
        self.m_name         = self.m_config["Simulation"]["Name"]
        self.m_pause_file   = self.m_config["Simulation"]["PauseFile"]
        self.m_stop_file    = self.m_config["Simulation"]["StopFile"]

    # end of __init__

    def lg(self, msg, level=6):

        # log it to syslog
        if self.m_log != None:
            # concat them
            full_msg = self.m_name + ": " + msg

            # In debug mode printouts go to terminal stdout as well
            if self.m_debug:
                print(full_msg)

            self.m_log.log(full_msg, level)

        else:
            print "There is no logger for message(" + msg + ")"

        return None
    # end of lg


    def dlg(self, msg, level=6):

        if self.m_debug:
            self.lg(msg, level)

        return None
    # end of dlg

    
    def get_connection(self, debug=False):

        try:

            if self.m_config["Simulation"]["Type"] == "Rabbit":
                self.m_broker_app   = RabbitMessagePublisher(self.m_config["Simulation"], self.m_log, debug)
            else:
                self.lg("ERROR: Unsupported Message Simulation Type(" + str(self.m_config["Simulation"]["Type"]) + ")", 0)

            if self.m_broker_app is not None:
                self.m_broker_app.connect()

        except Exception,e:
            err_msg             = "Failed to Connect with Ex(" + str(e) + ")"
            self.lg("ERROR: " + str(err_msg), 0)
            self.m_broker_app   = None
            self.m_state        = "Done"

    # end of get_connection


    def disconnect(self, debug):

        try:

            if self.m_broker_app is not None:
                self.m_broker_app.disconnect()

        except Exception,e:
            err_msg             = "Failed to Disconnect with Ex(" + str(e) + ")"
            self.lg("ERROR: " + str(err_msg), 0)
            self.m_broker_app   = None
            self.m_state        = "Done"

    # end of disconnect


    ############################################################################
    #
    # State Handlers:
    # 
    ############################################################################

    
    def handle_initialize_core(self):

        self.dlg("Initializing Core", 6)

        # Load up connectors:
        self.m_state        = "Process"
        debug               = self.m_debug

        # boot up: 
        self.get_connection()

    # end of handle_initialize_core


    def handle_shutdown(self, debug=False):
        
        self.dlg("Shutting Down Core", 6)

        # boot up: 
        if self.m_broker_app is not None:
            self.m_broker_app.stop()

    # end of handle_shutdown


    def handle_process(self, debug=False):
        
        self.dlg("Processing", 6)

        self.m_broker_app.run()

        self.m_state    = "Done"

    # end of handle_process


    def handle_sleep(self, debug=False):
        self.dlg("Sleeping", 6)

        if self.m_sleep_timer >= 1:
            sleep(self.m_sleep_timer)

        self.m_state    = "Check Pause"
    # end of handle_sleep


    def handle_check_pause(self, debug=False):
        self.dlg("Checking Pause", 6)

        if os.path.exists(self.m_pause_file) == True:
            self.lg("Pausing(" + str(self.m_pause_timer) + ") seconds", 6)
            self.m_state        = "Check Pause"
            sleep(self.m_pause_timer)
        else:
            self.m_state        = "Check Stop"
        
    # end of handle_check_pause
    

    def handle_check_stop(self, debug=False): 
        self.dlg("Checking Stop", 6)

        if os.path.exists(self.m_stop_file) == True:
            self.lg("Stopping for Action Hook", 6)
            self.m_state        = "Done"
        else:
            self.m_state        = "Check Jobs"
    # end of handle_check_stop


    def run_states(self):
        
        self.m_cur_time = datetime.datetime.now()

        if   self.m_state == "Startup":
            self.lg("Startup", 6)
            self.handle_initialize_core()

        elif self.m_state == "Process":
            self.handle_process(self.m_debug)

        elif self.m_state == "Sleep":
            self.handle_sleep(self.m_debug)

        elif self.m_state == "Check Pause":
            self.handle_check_pause(self.m_debug)

        elif self.m_state == "Check Stop":
            self.handle_check_stop(self.m_debug)

        elif self.m_state == "Done":
            self.lg("Done", 6)
            self.handle_shutdown(self.m_debug)
            self.m_is_done  = True

        else:
            self.lg("ERROR: Unknown State(" + str(self.m_state) + ")", 0)

        return self.m_is_done
    # end of run_states

# end of MessageSimulator
