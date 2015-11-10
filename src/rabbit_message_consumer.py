# System Imports
import pika, os, sys, json, inspect, uuid, argparse, datetime, logging, copy, imp, glob, time, subprocess
from time import sleep

# Local Imports
from logger         import Logger
from utils          import *


class RabbitMessageConsumer:
    
    """This is an Async Rabbit Message Consumer that will handle unexpected interactions
    with RabbitMQ such as channel and connection closures.

    If RabbitMQ closes the connection, it will reopen it. You should
    look at the output, as there are limited reasons why the connection may
    be closed, which usually are tied to permission related issues or
    socket timeouts.

    It uses delivery confirmations and illustrates one way to keep track of
    messages that have been sent and if they've been confirmed by RabbitMQ.

    """

    def __init__(self, cur_job_dict, logger=None, debug=False):

        # Load Params:
        self.m_config           = cur_job_dict
        self.m_log              = logger
        self.m_debug            = debug

        # Init Members:
        self.m_status           = "Not Connected"

        # Assign from Config:
        self.m_app_config       = self.m_config["Rabbit"]
        self.m_consumer_config  = self.m_config["Consumer"]

        self.m_name             = str(self.m_app_config["Name"])
        self.m_host_list        = str(self.m_app_config["BrokerAddress"][0])
        self.m_url              = str(self.m_app_config["BrokerURL"])

        # Determine the total messages to receive
        self.m_num_amqp_msgs    = int(self.m_consumer_config["NumberMessages"])
        self.m_queue            = str(self.m_consumer_config["Queue"])
        self.m_reply_to         = str(self.m_consumer_config["ReplyToQueue"])
        self.m_consumer_tag     = None

        if "ConsumerTag" in self.m_consumer_config:
            self.m_consumer_tag     = str(self.m_consumer_config["ConsumerTag"])

        self.m_debug_received   = True
        self.m_debug_reconnect  = False

        self.m_sent_messages    = {}
        self.m_recv_messages    = {}
        self.m_cur_message      = {}
        
        self.m_connection       = None
        self.m_channel          = None
        self.m_deliveries       = []
        self.m_acked            = 0
        self.m_nacked           = 0
        self.m_message_number   = 0
        self.m_active_bindings  = 0
        self.m_cur_msg_count    = 0

        self.m_publish_interval = float(self.m_config["Interval"])
        self.m_wait_interval    = float(self.m_config["CheckDone"])
        self.m_stopping         = False
        self.m_closing          = False
        self.m_run_summary      = True
        self.m_message_type     = "AMQP"
        self.m_number_to_send   = 0
        self.m_cur_count        = 0
    
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


    def elg(self, err_msg, print_to_stdout=False):

        if print_to_stdout:
            lg("ERROR: " + str(err_msg), 0)
        self.lg("ERROR: " + str(err_msg), 0)
    # end of elg


    def connect(self, debug=False):

        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika. If you want the reconnection to work, make
        sure you set stop_ioloop_on_close to False, which is not the default
        behavior of this adapter.

        :rtype: pika.SelectConnection

        """

        results                 = build_dict("FAILED", "Not Connected", {})

        try:
    
            # Setup the Credentials
            self.lg("Setting up Credentials", 6)
            self.m_credentials  = pika.PlainCredentials(self.m_app_config["Account"]["User"], self.m_app_config["Account"]["Password"])

            # Setup the Connection Parameters
            self.lg("Setting up Connection Parameters", 6)
            self.m_conn_params  = pika.ConnectionParameters(
                                        host=self.m_host_list,
                                        credentials=self.m_credentials)

            # Setup the Connection
            self.lg("Setting up Connection", 6)
            self.m_connection   = pika.SelectConnection(pika.URLParameters(self.m_url),
                                        self.on_connection_open,
                                        stop_ioloop_on_close=False)

            self.lg("Done Building Connection", 6)

            # Setup the Channel
            results             = build_dict("SUCCESS", "Connected", {})

        except Exception,k:
            err_msg             = "Failed to establish connection with Ex(" + str(k) + ")"
            self.lg("ERROR: " + str(err_msg), 0)
            self.m_status       = "Not Connected"
            results             = build_dict("FAILED", str(err_msg), {})
        # end of try/ex

        return results
    # end of connect


    def on_connection_open(self, unused_connection):

        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.

        :type unused_connection: pika.SelectConnection

        """

        self.lg("Connection opened", 6)
        self.m_status       = "CONNECTED"
        self.add_on_connection_close_callback()
        self.open_channel()

    # end of on_connection_open


    def disconnect(self, debug=False):

        results                 = build_dict("FAILED", "Unable to Disconnect", {})

        try:
    
            self.m_connection.close()
            results             = build_dict("SUCCESS", "Disconnected", {})
            self.m_status       = "Not Connected"

        except Exception,k:
            err_msg             = "Failed to establish connection with Ex(" + str(k) + ")"
            self.lg("ERROR: " + str(err_msg), 0)
            self.m_status       = "Not Connected"
            results             = build_dict("FAILED", str(err_msg), {})
        # end of try/ex

        return results
    # end of disconnect


    def close_channel(self):
        """Invoke this command to close the channel with RabbitMQ by sending
        the Channel.Close RPC command.

        """
        self.lg("Closing the channel", 6)
        if self.m_channel:
            self.m_channel.close()
    # end of close_channel


    def run(self):
        """Run the example code by connecting and then starting the IOLoop.

        """

        self.lg("Running", 6)
        self.connect()
        self.m_connection.ioloop.start()

    # end of run


    def stop(self):
        """Stop the example by closing the channel and connection. We
        set a flag here so that we stop scheduling new messages to be
        published. Restart the ioloop if we have not received all the message ack/nack's
        by now

        """

        if not self.m_stopping:
            self.lg("Starting Stopping", 6)
            self.m_stopping = True

            self.close_channel()
            
            self.close_connection()

            self.m_connection.ioloop.stop()

            self.lg("Done Stopping", 6)

    # end of stop


    def close_connection(self):
        """This method closes the connection to RabbitMQ."""
        self.m_closing = True
        self.lg("Closing connection", 6)
        self.m_connection.close()
        self.lg("Done Closing connection", 6)
    # end of close_connection


    ############################################################################
    #
    # Rabbit Specific AMQP Handlers:
    # 
    ############################################################################


    def add_on_connection_close_callback(self):
        """This method adds an on close callback that will be invoked by pika
        when RabbitMQ closes the connection to the publisher unexpectedly.

        """
        self.lg("Adding connection close callback", 6)
        self.m_connection.add_on_close_callback(self.on_connection_closed)
    
    # end of add_on_connection_close_callback


    def on_connection_closed(self, connection, reply_code, reply_text):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param pika.connection.Connection connection: The closed connection obj
        :param int reply_code: The server provided reply_code if given
        :param str reply_text: The server provided reply_text if given

        """

        self.lg("Closed Connection", 6)
        self.m_channel = None
        if self.m_closing:
            self.m_connection.ioloop.stop()
        else:
            self.lg("Connection closed, reopening in 5 seconds Reply(" + str(reply_code) + ") Text(" + str(reply_text) + ")", 0)

            self.m_connection.add_timeout(self.m_wait_interval, self.reconnect)
    # end of on_connection_closed


    def reconnect(self):
        """Will be invoked by the IOLoop timer if the connection is
        closed. See the on_connection_closed method.

        """
        if self.m_num_amqp_msgs <= self.m_message_number:
            return
        else:

            if self.m_debug_reconnect:
                self.elg("RECONNECT EVENT", True)

            self.m_deliveries = []

            # This is the old connection IOLoop instance, stop its ioloop
            self.m_connection.ioloop.stop()

            # Create a new connection
            self.connect()

            # There is now a new connection, needs a new ioloop to run
            self.m_connection.ioloop.start()

    # end of reconnect


    def open_channel(self):
        """This method will open a new channel with RabbitMQ by issuing the
        Channel.Open RPC command. When RabbitMQ confirms the channel is open
        by sending the Channel.OpenOK RPC reply, the on_channel_open method
        will be invoked.

        """
        self.lg("Creating a new channel", 6)
        self.m_connection.channel(on_open_callback=self.on_channel_open)
    # end of open_channel


    def on_channel_open(self, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.

        Since the channel is now open, we'll declare the exchange to use.

        :param pika.channel.Channel channel: The channel object

        """
        self.lg("Channel opened", 6)
        self.m_channel = channel
        self.add_on_channel_close_callback()

        self.start_consuming()
    # end of on_channel_open


    def add_on_channel_close_callback(self):
        """This method tells pika to call the on_channel_closed method if
        RabbitMQ unexpectedly closes the channel.

        """
        self.lg("Adding channel close callback", 6)
        self.m_channel.add_on_close_callback(self.on_channel_closed)
    # end of add_on_channel_close_callback


    def on_channel_closed(self, channel, reply_code, reply_text):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.

        :param pika.channel.Channel: The closed channel
        :param int reply_code: The numeric reason the channel was closed
        :param str reply_text: The text reason the channel was closed

        """
        self.lg("Channel was Closed: ReplyCode(" + str(reply_code) + ") Text(" + str(reply_text) + ")", 0)
        if not self.m_closing:
            self.m_connection.close()
     # end of on_channel_closed


    def setup_exchange(self, exchange_node):
        """Setup the exchange on RabbitMQ by invoking the Exchange.Declare RPC
        command. When it is complete, the on_exchange_declareok method will
        be invoked by pika.

        :param str|unicode exchange_name: The name of the exchange to declare

        """
        self.lg("Declaring Exchange(" + str(exchange_node["Name"]) + ") Type(" + str(exchange_node["Type"] + ") Attributes(" + str(exchange_node["Attributes"]) + ")"), 6)
        
        durable         = bool(exchange_node["Durable"])
        exclusive       = bool(exchange_node["Exclusive"])
        auto_delete     = bool(exchange_node["AutoDelete"])

        self.m_channel.exchange_declare(self.on_exchange_declareok, exchange=str(exchange_node["Name"]), type=str(exchange_node["Type"]).lower().lstrip().strip(), durable=durable, auto_delete=auto_delete)

     # end of setup_exchange


    def on_exchange_declareok(self, unused_frame):
        """Invoked by pika when RabbitMQ has finished the Exchange.Declare RPC
        command.

        :param pika.Frame.Method unused_frame: Exchange.DeclareOk response frame

        """

        self.lg("Exchange declared Frame(" + str(unused_frame) + ")", 6)
    # end of on_exchange_declareok


    def get_exchange_details(self, exchange_node, delete_flag=False, if_unused=True):

        """
        Checking for the existence of an Exchange requires a BlockingConnection...which means if we should delete this
        Exchange just do it while the connection is open.
        """

        results                 = build_dict("FAILED", "Not Found", {})

        try:

            if self.m_channel == None:
                results         = build_dict("FAILED", "Not Connected", {})
            else:
                    
                blocking_ch     = None

                try:
                    durable     = bool(exchange_node["Durable"])
                    exclusive   = bool(exchange_node["Exclusive"])
                    auto_delete = bool(exchange_node["AutoDelete"])

                    # To detect a queue exists there needs to be a blocking connection that will return immediately or throw
        
                    # Setup the Credentials
                    credentials = pika.PlainCredentials(self.m_app_config["Account"]["User"], self.m_app_config["Account"]["Password"])

                    # Setup the Connection Parameters
                    conn_params = pika.ConnectionParameters(
                                        host=self.m_app_config["BrokerAddress"][0],
                                        credentials=credentials)

                    # Setup the Connection
                    connection  = pika.BlockingConnection(conn_params)

                    # Setup the Channel
                    blocking_ch = connection.channel()
                    exch_obj    = blocking_ch.exchange_declare(exchange=str(exchange_node["Name"]), type=str(exchange_node["Type"]).lower().lstrip().strip(), durable=durable, auto_delete=auto_delete, passive=True)
                    
                    if exch_obj != None and exch_obj.method:

                        if delete_flag:
                            blocking_ch.exchange_delete(exchange=str(exchange_node["Name"]), if_unused=if_unused)
                            exch_obj        = blocking_ch.exchange_declare(exchange=str(exchange_node["Name"]), durable=durable, exclusive=exclusive, auto_delete=auto_delete, passive=True)
                            if exch_obj != None and exch_obj.method:
                                self.lg("ERROR: Failed to Delete Exchange(" + str(exchange_node["Name"]) + ") via Flag Deletion", 0)
                                results     = build_dict("SUCCESS", "Found Exchange", {
                                                    "Name"      : str(exchange_node["Name"])
                                                })
                            else:
                                results     = build_dict("SUCCESS", "No Exchange", {
                                                    "Name"      : str(exchange_node["Name"])
                                                })
                            # end of delete confirmation

                        else:
                            results         = build_dict("SUCCESS", "Found Exchange", {
                                                    "Name"      : str(exchange_node["Name"])
                                                })

                    blocking_ch.close()
                except Exception,h:
                    self.lg("Exchange(" + str(exchange_node["Name"]) + ") Exists Ex(" + str(h) + ")", 6)
                    results     = build_dict("SUCCESS", "No Exchange", {})
                # end of try/ex for getting the exchange

        except Exception,k:
            err_msg             = "Failed to run get_exchange_details with Ex(" + str(k) + ")"
            self.lg("ERROR: " + str(err_msg), 0)
            self.m_status       = "Failed"
            results             = build_dict("FAILED", str(err_msg), {})
        # end of try/ex

        return results
    # end of get_exchange_details


    def delete_exchange(self, exchange_node, if_unused=True):

        results                 = build_dict("FAILED", "Not Found", {})

        try:

            if self.m_channel == None:
                results         = build_dict("FAILED", "Not Connected", {})
            else:
                    
                blocking_ch     = None

                try:
                    durable     = bool(exchange_node["Durable"])
                    exclusive   = bool(exchange_node["Exclusive"])
                    auto_delete = bool(exchange_node["AutoDelete"])

                    # To DELETE a queue exists there needs to be a blocking connection that will return immediately or throw
        
                    # Setup the Credentials
                    credentials = pika.PlainCredentials(self.m_app_config["Account"]["User"], self.m_app_config["Account"]["Password"])

                    # Setup the Connection Parameters
                    conn_params = pika.ConnectionParameters(
                                        host=self.m_app_config["BrokerAddress"][0],
                                        credentials=credentials)

                    # Setup the Connection
                    connection  = pika.BlockingConnection(conn_params)

                    # Setup the Channel
                    blocking_ch = connection.channel()

                    # Delete it if it exists
                    blocking_ch.exchange_delete(queue=str(exchange_node["Name"]), if_unused=if_unused)

                    exch_obj    = blocking_ch.exchange_declare(exchange=str(exchange_node["Name"]), type=str(exchange_node["Type"]).lower().lstrip().strip(), durable=False, auto_delete=True, passive=True)
                    if exch_obj != None and exchange_obj.method:
                        results = build_dict("SUCCESS", "Found Exchange", {
                                                    "Name"  : str(exchange_node["Name"])
                                                })

                    blocking_ch.close()
                except Exception,h:
                    self.lg("Exchange(" + str(queue_node["Name"]) + ") Exists Ex(" + str(h) + ")", 6)
                    results     = build_dict("SUCCESS", "No Exchange", {})
                # end of try/ex for getting the queue

        except Exception,k:
            err_msg             = "Failed to run delete_exchange with Ex(" + str(k) + ")"
            self.lg("ERROR: " + str(err_msg), 0)
            self.m_status       = "Failed"
            results             = build_dict("FAILED", str(err_msg), {})
        # end of try/ex

        return results
    # end of delete_exchange


    def setup_queue(self, queue_node):
        """Setup the queue on RabbitMQ by invoking the Queue.Declare RPC
        command. When it is complete, the on_queue_declareok method will
        be invoked by pika.

        :param str|unicode queue_name: The name of the queue to declare.

        """
        self.lg("Declaring Queue(" + str(queue_node["Name"]) + ") Attributes(" + str(queue_node["Attributes"]) + ")", 6)

        durable         = bool(queue_node["Durable"])
        exclusive       = bool(queue_node["Exclusive"])
        auto_delete     = bool(queue_node["AutoDelete"])

        self.m_channel.queue_declare(self.on_queue_declareok, queue=str(queue_node["Name"]), durable=durable, exclusive=exclusive, auto_delete=auto_delete)
            
    # end of setup_queue


    def on_queue_declareok(self, method_frame):
        """Method invoked by pika when the Queue.Declare RPC call made in
        setup_queue has completed. In this method we will bind the queue
        and exchange together with the routing key by issuing the Queue.Bind
        RPC command. When this command is complete, the on_bindok method will
        be invoked by pika.

        :param pika.frame.Method method_frame: The Queue.DeclareOk frame

        """
        self.lg("Queue Declared(" + str(method_frame) + ")", 6)
    # end of on_queue_declareok


    def get_queue_details(self, queue_node, delete_flag=False, if_empty=True):

        """
        Checking for the existence of a Queue requires a BlockingConnection...which means if we should delete this
        queue just do it while the connection is open.
        """

        results                 = build_dict("FAILED", "Not Found", {})

        try:

            if self.m_channel == None:
                results         = build_dict("FAILED", "Not Connected", {})
            else:
                    
                blocking_ch     = None

                try:
                    durable     = bool(queue_node["Durable"])
                    exclusive   = bool(queue_node["Exclusive"])
                    auto_delete = bool(queue_node["AutoDelete"])

                    # To detect a queue exists there needs to be a blocking connection that will return immediately or throw
        
                    # Setup the Credentials
                    credentials = pika.PlainCredentials(self.m_app_config["Account"]["User"], self.m_app_config["Account"]["Password"])

                    # Setup the Connection Parameters
                    conn_params = pika.ConnectionParameters(
                                        host=self.m_app_config["BrokerAddress"][0],
                                        credentials=credentials)

                    # Setup the Connection
                    connection  = pika.BlockingConnection(conn_params)

                    # Setup the Channel
                    blocking_ch = connection.channel()
                    queue_obj   = blocking_ch.queue_declare(queue=str(queue_node["Name"]), durable=durable, exclusive=exclusive, auto_delete=auto_delete, passive=True)

                    if queue_obj != None and queue_obj.method:

                        if delete_flag:

                            blocking_ch.queue_delete(queue=str(queue_node["Name"]), if_empty=if_empty)
                            queue_obj       = blocking_ch.queue_declare(queue=str(queue_node["Name"]), durable=durable, exclusive=exclusive, auto_delete=auto_delete, passive=True)
                            if queue_obj != None and queue_obj.method:
                                self.lg("ERROR: Failed to Delete Queue(" + str(queue_node["Name"]) + ") via Flag Deletion", 0)
                                results     = build_dict("SUCCESS", "Found Queue", {
                                                    "Queue"     : str(queue_node["Name"]),
                                                    "Consumers" : str(queue_obj.method.consumer_count),
                                                    "Messages"  : str(queue_obj.method.message_count)
                                                })
                            else:
                                results     = build_dict("SUCCESS", "No Queue", {})
                            # end of delete confirmation

                        else:
                            results         = build_dict("SUCCESS", "Found Queue", {
                                                    "Queue"     : str(queue_node["Name"]),
                                                    "Consumers" : str(queue_obj.method.consumer_count),
                                                    "Messages"  : str(queue_obj.method.message_count)
                                                })

                    blocking_ch.close()
                except Exception,h:
                    self.lg("Queue(" + str(queue_node["Name"]) + ") Exists Ex(" + str(h) + ")", 6)
                    results     = build_dict("SUCCESS", "No Queue", {})
                # end of try/ex for getting the queue

        except Exception,k:
            err_msg             = "Failed to run get_queue_details with Ex(" + str(k) + ")"
            self.lg("ERROR: " + str(err_msg), 0)
            self.m_status       = "Failed"
            results             = build_dict("FAILED", str(err_msg), {})
        # end of try/ex

        return results
    # end of get_queue_details


    def delete_queue(self, queue_node, if_empty=True):

        results                 = build_dict("FAILED", "Not Found", {})

        try:

            if self.m_channel == None:
                results         = build_dict("FAILED", "Not Connected", {})
            else:
                    
                blocking_ch     = None

                try:
                    durable     = bool(queue_node["Durable"])
                    exclusive   = bool(queue_node["Exclusive"])
                    auto_delete = bool(queue_node["AutoDelete"])

                    # To DELETE a queue exists there needs to be a blocking connection that will return immediately or throw
        
                    # Setup the Credentials
                    credentials = pika.PlainCredentials(self.m_app_config["Account"]["User"], self.m_app_config["Account"]["Password"])

                    # Setup the Connection Parameters
                    conn_params = pika.ConnectionParameters(
                                        host=self.m_app_config["BrokerAddress"][0],
                                        credentials=credentials)

                    # Setup the Connection
                    connection  = pika.BlockingConnection(conn_params)

                    # Setup the Channel
                    blocking_ch = connection.channel()

                    # Delete it if it exists
                    blocking_ch.queue_delete(queue=str(queue_node["Name"]), if_empty=if_empty)

                    queue_obj   = blocking_ch.queue_declare(queue=str(queue_node["Name"]), durable=False, exclusive=True, auto_delete=True, passive=True)
                    if queue_obj != None and queue_obj.method:
                        results = build_dict("SUCCESS", "Found Queue", {
                                                    "Consumers" : str(queue_obj.method.consumer_count),
                                                    "Messages"  : str(queue_obj.method.message_count)
                                                })

                    blocking_ch.close()
                except Exception,h:
                    self.lg("Queue(" + str(queue_node["Name"]) + ") Exists Ex(" + str(h) + ")", 6)
                    results     = build_dict("SUCCESS", "No Queue", {})
                # end of try/ex for getting the queue

        except Exception,k:
            err_msg             = "Failed to run delete_queue with Ex(" + str(k) + ")"
            self.lg("ERROR: " + str(err_msg), 0)
            self.m_status       = "Failed"
            results             = build_dict("FAILED", str(err_msg), {})
        # end of try/ex

        return results
    # end of delete_queue


    def on_bindok(self, unused_frame):
        """This method is invoked by pika when it receives the Queue.BindOk
        response from RabbitMQ. Since we know we're now setup and bound, it's
        time to start publishing."""
        self.lg("Queue bound", 6)

    # end of on_bindok



    def convert_cur_message_dict_to_basic_properties(self, cur_job_dict, cur_message_number=None, cur_message_id=None, cur_app_id=None):

        content_type        = None
        content_encoding    = None
        headers             = None
        delivery_mode       = None
        priority            = None
        correlation_id      = None
        reply_to            = None
        expiration          = None
        message_id          = cur_message_id
        timestamp           = None
        user_id             = None
        app_id              = None
        cluster_id          = None

        if "AppID" in cur_job_dict and str(cur_job_dict["AppID"]) != "":
            app_id          = str(cur_job_dict["AppID"])
        else:
            if app_id is not None:
                app_id      = cur_app_id
            else:
                app_id      = "MsgSimApp"

        if "ClusterID" in cur_job_dict and str(cur_job_dict["ClusterID"]) != "":
            cluster_id      = str(cur_job_dict["ClusterID"])
        if "UserID" in cur_job_dict and str(cur_job_dict["UserID"]) != "":
            user_id         = str(cur_job_dict["UserID"])
        if "MessageID" in cur_job_dict and str(cur_job_dict["MessageID"]) != "":
            message_id      = str(cur_job_dict["MessageID"])
        if "ContentType" in cur_job_dict and str(cur_job_dict["ContentType"]) != "":
            content_type    = str(cur_job_dict["ContentType"])
        if "Encoding" in cur_job_dict and str(cur_job_dict["Encoding"]) != "":
            content_encoding= str(cur_job_dict["Encoding"])
        if "Headers" in cur_job_dict and (str(cur_job_dict["Headers"]) != "{}" and str(cur_job_dict["Headers"]) != ""):
            headers         = cur_job_dict["Headers"]
        if "DeliveryMode" in cur_job_dict and str(cur_job_dict["DeliveryMode"]) != "":
            delivery_mode   = int(cur_job_dict["DeliveryMode"])
        if "Priority" in cur_job_dict and str(cur_job_dict["Priority"]) != "":
            priority        = int(cur_job_dict["Priority"])
        if "CorrelationID" in cur_job_dict and str(cur_job_dict["CorrelationID"]) != "":
            correlation_id  = str(cur_job_dict["CorrelationID"])

        if "ReplyTo" in cur_job_dict and str(cur_job_dict["ReplyTo"]) != "":
            reply_to        = str(cur_job_dict["ReplyTo"])
        else:
            reply_to        = "Default"

        if "Expiration" in cur_job_dict and str(cur_job_dict["Expiration"]) != "":
            expiration      = str(cur_job_dict["Expiration"])
        else:
            now             = datetime.datetime.now()
            expiration      = str(1000 * int((now.replace(hour=23, minute=59, second=59, microsecond=999999) - now).total_seconds()))

        if "Timestamp" in cur_job_dict and str(cur_job_dict["Timestamp"]) != "":
            timestamp       = int(cur_job_dict["Timestamp"])
        else:
            timestamp       = time.time()
        
        properties          = pika.BasicProperties(
                                            content_type=content_type,
                                            content_encoding=content_encoding,
                                            headers=headers,
                                            delivery_mode=delivery_mode,
                                            priority=priority,
                                            correlation_id=correlation_id,
                                            reply_to=reply_to,
                                            expiration=expiration,
                                            message_id=message_id,
                                            timestamp=timestamp,
                                            user_id=user_id,
                                            app_id=app_id,
                                            cluster_id=cluster_id)


        return properties
    # end of convert_cur_message_dict_to_basic_properties


    def stop_broker(self, cur_message):

        """ 
        Default handler for stopping a broker on a remote node

        --- Please Read --- 
        
        Setup Notes:

            For now this is using ssh to invoke a command on the remote host

            Please install the ssh keys that will allow password-less access to a user that has credentials to perform a command:
            
                kill -9 <Broker PID>

            Eventually this could be using a Queue for control messages or post using HTTP to a rest control service deployed on the node

        """
        
        results             = build_dict("FAILED", "Stop Broker Not Started", {
                                            "Nodes"     : [],
                                            "Errors"    : []
                                    })

        try:

            self.m_cur_count    += 1

            self.lg("Handling - Stopping a Broker(" + str(json.dumps(cur_message)) + ")", 6)

            ssh_host            = str(cur_message["Host"])
            ssh_user            = str(cur_message["User"])

            commands_to_run     = cur_message["Commands"]
            count_idx           = 0

            values              = {
                                    "PID"   : None,
                                }

            all_success         = False
            err_msg             = "Stop Broker Failed"

            for ssh_command in commands_to_run:
                
                valid_command   = True

                # Allow for edits before running:
                remote_command  = str(ssh_command)

                if count_idx == 1:
                    
                    if str(values["PID"]) != "" and str(values["PID"]).lower() != "none":
                        remote_command  = remote_command.replace("%i", str(values["PID"]))

                        if values["PID"] != "":
                            self.lg("Stopping Remote Broker(" + str(ssh_host) + ") with PID(" + str(values["PID"]) + ") Command(" + str(remote_command) + ")", 6)
                        else:
                            valid_command   = False

                    else:
                        err_msg     = "Failed to find a valid Broker PID for Stopping Remote Broker(" + str(ssh_host) + ") with PID(" + str(values["PID"]) + ") Command(" + str(remote_command) + ")"
                        self.elg(err_msg, True)
                        results     = build_dict("FAILED", str(err_msg), { "Nodes" : [], "Errors" : [] })
                        return results

                # end of prescreening for kill command

                if valid_command:
                    proc            = subprocess.Popen(remote_command, shell=True, stdout=subprocess.PIPE)
                    std_rows        = proc.communicate()[0].split("\n")

                    # For killing the broker the first command gets the PID
                    if len(std_rows) == 1:

                        if count_idx == 0:
                            err_msg     = "Failed to Stop Broker with Error(" + str(std_rows) + ")"
                            self.elg(err_msg, True)
                            results     = build_dict("FAILED", str(err_msg), { "Nodes" : [], "Errors" : [] })
                            return results

                        else:
                            all_success = True


                    else:
                        if count_idx == 0:
                            values["PID"]   = str(std_rows[0].replace("   ", " ").replace("  ", " ").split(" ")[1]).strip().lstrip()
                            if values["PID"] != "":
                                self.lg("Stopping Remote Broker(" + str(ssh_host) + ") with PID(" + str(values["PID"]) + ")", 6)
                # end of valid command

                count_idx       += 1

            # end of for all commands
            
            if all_success:
                
                cluster_nodes   = self.return_all_cluster_node_details()

                if "Expected" in cur_message:

                    self.lg("Checking Cluster", 6)
                    # Confirm the cluster is as expected after stopping it:
                    all_valid       = False

                    if cluster_nodes["Status"] == "SUCCESS":
                    
                        self.lg("Validing Expected(" + str(len(cur_message["Expected"])) + ") Cluster(" + str(len(cluster_nodes["Record"]["Nodes"])) + ")", 6)

                        errors      = []

                        if len(cur_message["Expected"]) == len(cluster_nodes["Record"]["Nodes"]):

                            # This is looks like it should be refactored...

                            for expected_node in cur_messages["Expected"]["Messages"]:

                                found_node          = False

                                for cluster_node in cluster_nodes["Record"]["Nodes"]:
                                    if str(cluster_node["Name"]).lower().strip().lstrip() == str(expected_node["Name"]).lower().strip().lstrip():
                                        found_node  = True
                                        for key in expected_node:
                                            if key not in cluster_node:
                                                errors.append("Missing Expected(" + str(expected_node["Name"]) + ") with a Cluster Key(" + str(key) + ")")
                                            # if it is missing
                                            else:
                                                if cluster_node[key].strip().lstrip() != expected_node[key].lstrip().strip():
                                                    errors.append("Cluster Node(" + str(cluster_node["Name"]) + ") Key(" + str(key) + ") Value(" + str(cluster_node[key]) + ") Does not match Expected(" + str(expected_node["Name"]) + ") Value(" + str(expected_node[key]) + ")")
                                        # for each expected key on the node
                                    # if the cluster's name matches the expected

                                # end for all cluster nodes

                            # end for all expecteds
                        else:
                            errors.append("Cluster Node Mismatch Expected(" + str(len(cur_message["Expected"])) + ") Cluster(" + str(len(cluster_nodes["Record"]["Nodes"])) + ")")
                        # if there are expectations on the cluster's new status, perform the validation and build the errors

                        if len(errors) == 0:
                            results = build_dict("SUCCESS", "", { "Nodes" : cluster_nodes["Record"]["Nodes"], "Errors" : [] })
                        else:
                            results = build_dict("FAILED",  "", { "Nodes" : cluster_nodes["Record"]["Nodes"], "Errors" : [] })
                            
                    # end of if cluster_nodes["Status"] == "SUCCESS"
                else:
                    results         = build_dict("SUCCESS", "", { "Nodes" : cluster_nodes["Record"]["Nodes"], "Errors" : [] })
                # if success

            # all success 
            else:
                results             = build_dict("FAILED", str(err_msg), { "Nodes" : [], "Errors" : [] })
            # end of if/else

        except Exception,k:
            err_msg     = "Failed Stop Broker Number(" + str(self.m_message_number) + ") Message(" + str(cur_message) + ") with Ex(" + str(k) + ")"
            self.elg(err_msg, True)
            results     = build_dict("FAILED", str(err_msg), { "Nodes" : [], "Errors" : [] })

            self.m_message_number   += 1
        # end of try/ex

        return results
    # end of stop_broker


    def start_broker(self, cur_message):

        """ 
        Default handler for starting a broker on a remote node

        --- Please Read --- 
        
        Setup Notes:

            For now this is using ssh to invoke a command on the remote host

            Please install the ssh keys that will allow password-less access to a user that has credentials to perform a command:
            
                kill -9 <Broker PID>

            Eventually this could be using a Queue for control messages or post using HTTP to a rest control service deployed on the node

        """
        
        results             = build_dict("FAILED", "Start Broker Not Started", {
                                            "Nodes"     : [],
                                            "Errors"    : []
                                    })

        try:

            self.m_cur_count    += 1

            self.lg("Handling - Starting a Broker(" + str(json.dumps(cur_message)) + ")", 6)

            ssh_host            = str(cur_message["Host"])
            ssh_user            = str(cur_message["User"])

            commands_to_run     = cur_message["Commands"]
            count_idx           = 0

            values              = {}
            all_success         = False
            err_msg             = "Start Broker Failed"

            for ssh_command in commands_to_run:
                
                valid_command   = True

                # Allow for edits before running:
                remote_command  = str(ssh_command)

                # allow for filtering out remote commands based off specific rules
                if valid_command:
                    proc        = subprocess.Popen(remote_command, shell=True, stdout=subprocess.PIPE)
                    std_rows    = proc.communicate()[0].split("\n")

                    # For killing the broker the first command gets the PID
                    if len(std_rows) == 1:
                        err_msg     = "Failed to Starting Broker with Error(" + str(std_rows) + ")"
                        self.elg(err_msg, True)
                        results     = build_dict("FAILED", str(err_msg), { "Nodes" : [], "Errors" : [] })
                    else:
                        self.lg("Starting Remote Broker(" + str(ssh_host) + ") Done Command(" + str(count_idx) + ") Exec(" + str(remote_command) + ")", 6)
                        all_success = True
                # end of valid command

                count_idx       += 1

            # end of for all commands
            
            if all_success:
                
                cluster_nodes   = self.return_all_cluster_node_details()

                if "Expected" in cur_message:

                    self.lg("Checking Cluster", 6)
                    # Confirm the cluster is as expected after stopping it:
                    all_valid       = False

                    if cluster_nodes["Status"] == "SUCCESS":
                    
                        self.lg("Validing Expected(" + str(len(cur_message["Expected"])) + ") Cluster(" + str(len(cluster_nodes["Record"]["Nodes"])) + ")", 6)

                        errors      = []

                        if len(cur_message["Expected"]) == len(cluster_nodes["Record"]["Nodes"]):

                            # This is looks like it should be refactored...

                            for expected_node in cur_messages["Expected"]["Messages"]:

                                found_node          = False

                                for cluster_node in cluster_nodes["Record"]["Nodes"]:
                                    if str(cluster_node["Name"]).lower().strip().lstrip() == str(expected_node["Name"]).lower().strip().lstrip():
                                        found_node  = True
                                        for key in expected_node:
                                            if key not in cluster_node:
                                                errors.append("Missing Expected(" + str(expected_node["Name"]) + ") with a Cluster Key(" + str(key) + ")")
                                            # if it is missing
                                            else:
                                                if cluster_node[key].strip().lstrip() != expected_node[key].lstrip().strip():
                                                    errors.append("Cluster Node(" + str(cluster_node["Name"]) + ") Key(" + str(key) + ") Value(" + str(cluster_node[key]) + ") Does not match Expected(" + str(expected_node["Name"]) + ") Value(" + str(expected_node[key]) + ")")
                                        # for each expected key on the node
                                    # if the cluster's name matches the expected

                                # end for all cluster nodes

                            # end for all expecteds
                        else:
                            errors.append("Cluster Node Mismatch Expected(" + str(len(cur_message["Expected"])) + ") Cluster(" + str(len(cluster_nodes["Record"]["Nodes"])) + ")")
                        # if there are expectations on the cluster's new status, perform the validation and build the errors

                        if len(errors) == 0:
                            results = build_dict("SUCCESS", "", { "Nodes" : cluster_nodes["Record"]["Nodes"], "Errors" : [] })
                        else:
                            results = build_dict("FAILED",  "", { "Nodes" : cluster_nodes["Record"]["Nodes"], "Errors" : [] })
                            
                    # end of if cluster_nodes["Status"] == "SUCCESS"
                else:
                    results         = build_dict("SUCCESS", "", { "Nodes" : cluster_nodes["Record"]["Nodes"], "Errors" : [] })
                # if success

            # all success 
            else:
                results             = build_dict("FAILED", str(err_msg), { "Nodes" : [], "Errors" : [] })
            # end of if/else

        except Exception,k:
            err_msg     = "Failed Start Broker Number(" + str(self.m_message_number) + ") Message(" + str(cur_message) + ") with Ex(" + str(k) + ")"
            self.elg(err_msg, True)
            results     = build_dict("FAILED", str(err_msg), { "Nodes" : [], "Errors" : [] })

            self.m_message_number   += 1
        # end of try/ex

        return results
    # end of start_broker


    def validate_ssh_credentials(self, cur_message):

        """ 
        Validate the SSH Credentials are working without password for cluster control: 
        
            sudo ./run_message_simulation.py -f simulations/validate_ssh_credentials_across_cluster.json

        --- Please Read --- 
        
        Setup Notes:

            For now this is using ssh to invoke a command on the remote host

            Please install the ssh keys that will allow password-less access to a user that has credentials to perform a command:
            
                kill -9 <Broker PID>

            Eventually this could be using a Queue for control messages or post using HTTP to a rest control service deployed on the node

        """
        
        results             = build_dict("FAILED", "Not Valid", {})

        try:

            self.m_cur_count        += 1

            self.lg("Handling - Validating SSH Credentials(" + str(json.dumps(cur_message)) + ")", 6)

            ssh_host        = str(cur_message["Host"])
            ssh_user        = str(cur_message["User"])

            commands_to_run = cur_message["Commands"]
            count_idx       = 0

            valid_setup     = False

            for ssh_command in commands_to_run:
                
                # Allow for edits before running:
                remote_command  = str(ssh_command)

                proc            = subprocess.Popen(remote_command, shell=True, stdout=subprocess.PIPE)
                std_rows        = proc.communicate()[0].split("\n")
            
                if len(std_rows) == 1:
                    valid_setup = False
                else:
                    lg("\tSSH Credentials Validated(" + str(ssh_host) + ")", 5)
                    valid_setup = True

            # end of for all commands

            if valid_setup:
                results     = build_dict("SUCCESS", "SSH Credentials Validated", {})
            else:
                err_msg     = "SSH Validation Failed Please run: ssh-copy-id root@" + str(ssh_host)
                self.elg(err_msg, True)
                results     = build_dict("FAILED", str(err_msg), {})

        except Exception,k:
            err_msg         = "Failed Validating SSH Credentials Number(" + str(self.m_message_number) + ") Message(" + str(cur_message) + ") with Ex(" + str(k) + ")"
            self.elg(err_msg, True)
            results         = build_dict("FAILED", str(err_msg), {})

            self.m_message_number   += 1
        # end of try/ex

        return results
    # end of validate_ssh_credentials


    def return_all_exchange_details(self):

        """
        Getting all Exchange details requires running as root to access rabbitmqctl
        """

        results             = build_dict("FAILED", "Not Found", { "Exchanges" : [] })

        try:

            if self.m_channel == None:
                results     = build_dict("FAILED", "Not Connected", { "Exchanges" : [] })
            else:
                    
                try:

                    proc        = subprocess.Popen("/usr/bin/rabbitmqadmin list exchanges name type durable auto_delete internal policy vhost arguments", shell=True, stdout=subprocess.PIPE)
                    std_rows    = proc.communicate()[0].split("\n")
                    results     = build_dict("SUCCESS", "Found Exchanges", {
                                                        "Exchanges"  : [],
                                                })


                    self.lg("Building Exchange Rows(" + str(len(std_rows)) + ")", 6)
                    use_row     = False
                    cur_row     = 0
                    for row in std_rows:

                        if use_row:
                            row_arr         = row.split("|")

                            if len(row_arr) > 1:
                                self.dlg("Exchange Row(" + str(row_arr) + ")", 6)
                                exchange_name   = str(row_arr[1]).strip().lstrip()
                                exchange_type   = str(row_arr[2]).strip().lstrip()
                                durable         = str(row_arr[3]).strip().lstrip()
                                auto_delete     = str(row_arr[4]).strip().lstrip()
                                internal        = str(row_arr[5]).strip().lstrip()
                                policy          = str(row_arr[6]).strip().lstrip()
                                vhost           = str(row_arr[7]).strip().lstrip()
                                arguments       = str(row_arr[8]).strip().lstrip()

                                if exchange_name == "":
                                    exchange_name   = "direct"
                                
                                new_exchange    = {
                                                    "Exchange"      : str(exchange_name),
                                                    "Type"          : str(exchange_type),
                                                    "Durable"       : str(durable),
                                                    "AutoDelete"    : str(auto_delete),
                                                    "Internal"      : str(internal),
                                                    "Policy"        : str(policy),
                                                    "VHost"         : str(vhost),
                                                    "Arguments"     : str(arguments)
                                                }
                        
                                results["Record"]["Exchanges"].append(new_exchange)
                        else:

                            if cur_row > 2:
                                use_row = True
                        # end of skip first headers
                        cur_row         += 1

                    # build all the exchanges

                except Exception,h:
                    self.lg("Get All Exchanges Failed with Ex(" + str(h) + ")", 6)
                    results     = build_dict("SUCCESS", "No Exchanges", { "Exchanges" : [] })
                # end of try/ex for getting the exchanges

        except Exception,k:
            err_msg             = "Failed to run return_all_exchange_details with Ex(" + str(k) + ")"
            self.lg("ERROR: " + str(err_msg), 0)
            self.m_status       = "Failed"
            results             = build_dict("FAILED", str(err_msg), { "Exchanges" : [] })
        # end of try/ex

        return results
    # end of return_all_exchange_details


    def return_all_queue_details(self):

        """
        Getting all Exchange details requires running as root to access rabbitmqctl
        """

        results             = build_dict("FAILED", "Not Found", { "Queues" : [] })

        try:

            if self.m_channel == None:
                results     = build_dict("FAILED", "Not Connected", { "Queues" : [] })
            else:
                    
                try:

                    proc        = subprocess.Popen("/usr/bin/rabbitmqadmin list queues name node durable auto_delete policy pid owner_pid exclusive_consumer_pid exclusive_consumer_tag messages_ready messages_unacknowledged messages messages_ready_ram messages_ram messages_persistent message_bytes consumers consumer_utilisation memory state save_nodes synchronised_slave_nodes arguments", shell=True, stdout=subprocess.PIPE)
                    std_rows    = proc.communicate()[0].split("\n")
                    results     = build_dict("SUCCESS", "Found Queues", {
                                                        "Queues"  : [],
                                                })


                    self.lg("Building Queues Rows(" + str(len(std_rows)) + ")", 6)
                    use_row     = False
                    cur_row     = 0
                    for row in std_rows:

                        if use_row:
                            row_arr         = row.split("|")

                            if len(row_arr) > 1:
                                self.dlg("Queue Row(" + str(row_arr) + ")", 6)
                                queue_name  = str(row_arr[1]).strip().lstrip()
                                node        = str(row_arr[2]).strip().lstrip()
                                durable     = str(row_arr[3]).strip().lstrip()
                                auto_delete = str(row_arr[4]).strip().lstrip()
                                policy      = str(row_arr[5]).strip().lstrip()
                                pid         = str(row_arr[6]).strip().lstrip()
                                owner_pid   = str(row_arr[7]).strip().lstrip()
                                exc_con_pid = str(row_arr[8]).strip().lstrip()
                                exc_con_tag = str(row_arr[9]).strip().lstrip()
                                msgs_ready  = str(row_arr[10]).strip().lstrip()
                                msgs_unack  = str(row_arr[11]).strip().lstrip()
                                messages    = str(row_arr[12]).strip().lstrip()
                                msg_rdy_ram = str(row_arr[13]).strip().lstrip()
                                msgs_ram    = str(row_arr[14]).strip().lstrip()
                                msgs_perst  = str(row_arr[15]).strip().lstrip()
                                msg_bytes   = str(row_arr[16]).strip().lstrip()
                                consumers   = str(row_arr[17]).strip().lstrip()
                                cons_util   = str(row_arr[18]).strip().lstrip()
                                memory      = str(row_arr[19]).strip().lstrip()
                                state       = str(row_arr[20]).strip().lstrip()
                                slave_nodes = str(row_arr[21]).strip().lstrip()
                                sync_slaves = str(row_arr[22]).strip().lstrip()
                                arguments   = str(row_arr[23]).strip().lstrip()
                                
                                new_queue   = {
                                                "Name"                  : str(queue_name),
                                                "Node"                  : str(node),
                                                "Durable"               : str(durable),
                                                "AutoDelete"            : str(auto_delete),
                                                "Policy"                : str(policy),
                                                "PID"                   : str(pid),
                                                "OwnerPID"              : str(owner_pid),
                                                "ExclusiveConsumerPID"  : str(exc_con_pid),
                                                "ExclusiveConsumerTag"  : str(exc_con_tag),
                                                "MsgsReady"             : str(msgs_ready),
                                                "MsgsUnacked"           : str(msgs_unack),
                                                "Msgs"                  : str(messages),
                                                "MsgsReadyRam"          : str(msg_rdy_ram),
                                                "MsgsRam"               : str(msgs_ram),
                                                "MsgsPersistent"        : str(msgs_perst),
                                                "MsgsBytes"             : str(msg_bytes),
                                                "Consumers"             : str(consumers),
                                                "ConsumerUtilization"   : str(cons_util),
                                                "Memory"                : str(memory),
                                                "State"                 : str(state),
                                                "SlaveNodes"            : str(slave_nodes),
                                                "SyncSlaveNodes"        : str(sync_slaves),
                                                "State"                 : str(state),
                                                "Arguments"             : str(arguments)
                                            }
                        
                                results["Record"]["Queues"].append(new_queue)
                        else:
                            if cur_row > 1:
                                use_row = True
                        # end of skip first headers
                        cur_row         += 1

                    # build all the queues

                except Exception,h:
                    self.lg("Get All Queues Failed with Ex(" + str(h) + ")", 6)
                    results     = build_dict("SUCCESS", "No Queues", { "Queues" : [] })
                # end of try/ex for getting the queue

        except Exception,k:
            err_msg             = "Failed to run return_all_queue_details with Ex(" + str(k) + ")"
            self.lg("ERROR: " + str(err_msg), 0)
            self.m_status       = "Failed"
            results             = build_dict("FAILED", str(err_msg), { "Queues" : [] })
        # end of try/ex

        return results
    # end of return_all_queue_details


    def return_all_binding_details(self):

        """
        Getting all Bindings details requires running as root to access rabbitmqctl
        """

        results             = build_dict("FAILED", "Not Found", { "Bindings" : [] })

        try:

            if self.m_channel == None:
                results     = build_dict("FAILED", "Not Connected", { "Bindings" : [] })
            else:
                    
                try:

                    proc        = subprocess.Popen("/usr/bin/rabbitmqadmin list bindings source destination routing_key", shell=True, stdout=subprocess.PIPE)
                    std_rows    = proc.communicate()[0].split("\n")
                    results     = build_dict("SUCCESS", "Found Bindings", {
                                                        "Bindings"  : [],
                                                })

                    # build all the bindings

                    self.lg("Building Bindings Rows(" + str(len(std_rows)) + ")", 6)
                    use_row     = False
                    cur_row     = 0
                    for row in std_rows:

                        if use_row:
                            row_arr           = row.split("|")

                            if len(row_arr) > 1:
                                self.dlg("Binding Row(" + str(row_arr) + ")", 6)
                                source_name       = str(row_arr[1]).strip().lstrip()
                                destination_name  = str(row_arr[2]).strip().lstrip()
                                routing_key       = str(row_arr[3]).strip().lstrip()

                                if source_name == "":
                                    source_name   = "Default"
                                
                                new_binding       = {
                                                      "Source"      : str(source_name),
                                                      "Destination" : str(destination_name),
                                                      "RoutingKey"  : str(routing_key)
                                                  }
                        
                                results["Record"]["Bindings"].append(new_binding)
                        else:
                            if cur_row > 1:
                                use_row = True
                        # end of skip first headers
                        cur_row         += 1

                    # build all the bindings

                except Exception,h:
                    self.lg("Get All Bindings Failed with Ex(" + str(h) + ")", 6)
                    results     = build_dict("SUCCESS", "No Bindings", { "Bindings" : [] })
                # end of try/ex for getting the queue

        except Exception,k:
            err_msg             = "Failed to run return_all_binding_details with Ex(" + str(k) + ")"
            self.lg("ERROR: " + str(err_msg), 0)
            self.m_status       = "Failed"
            results             = build_dict("FAILED", str(err_msg), { "Bindings" : [] })
        # end of try/ex

        return results
    # end of return_all_binding_details


    def return_all_cluster_node_details(self):

        """
        Getting all Cluster details requires running as root to access rabbitmqadmin
        """

        results             = build_dict("FAILED", "Not Found", { "Nodes" : [] })

        try:

            if self.m_channel == None:
                results     = build_dict("FAILED", "Not Connected", { "Nodes" : [] })
            else:
                    
                try:

                    proc        = subprocess.Popen("/bin/rabbitmqadmin list nodes name type proc_total proc_used  processors  run_queue  running sockets_total  sockets_used  statistics_level uptime fd_total fd_used memory", shell=True, stdout=subprocess.PIPE)
                    std_rows    = proc.communicate()[0].split("\n")

                    use_row     = False
                    cur_row     = 0
                    results     = build_dict("SUCCESS", "Found Nodes", {
                                                        "Nodes"  : [],
                                                })


                    self.lg("Building Nodes Rows(" + str(len(std_rows)) + ")", 6)
                    for row in std_rows:

                        if use_row:

                            row_arr         = row.split("|")

                            if len(row_arr) > 1:
                                self.dlg("Node Row(" + str(row_arr) + ")", 6)
                                node_name       = str(row_arr[0]).lstrip().strip()
                                type_name       = str(row_arr[1]).lstrip().strip()
                                proc_total      = str(row_arr[2]).lstrip().strip()
                                proc_used       = str(row_arr[3]).lstrip().strip()
                                processors      = str(row_arr[4]).lstrip().strip()
                                run_queue       = str(row_arr[5]).lstrip().strip()
                                status          = str(row_arr[6]).lstrip().strip()
                                sockets_total   = str(row_arr[7]).lstrip().strip()
                                sockets_used    = str(row_arr[8]).lstrip().strip()
                                stats_level     = str(row_arr[9]).lstrip().strip()
                                uptime          = str(row_arr[10]).lstrip().strip()
                                fd_total        = str(row_arr[11]).lstrip().strip()
                                fd_used         = str(row_arr[12]).lstrip().strip()
                                memory          = str(row_arr[13]).lstrip().strip()

                                new_node        = {
                                                    "Name"          : str(node_name),
                                                    "Type"          : str(type_name),
                                                    "ProcTotal"     : str(proc_total),
                                                    "ProcUsed"      : str(proc_used),
                                                    "Processors"    : str(processors),
                                                    "RunQueue"      : str(run_queue),
                                                    "Running"       : str(status),
                                                    "SocketsTotal"  : str(sockets_total),
                                                    "SocketsUsed"   : str(sockets_used),
                                                    "StatsLevel"    : str(stats_level),
                                                    "Uptime"        : str(uptime),
                                                    "FDs"           : str(fd_total),
                                                    "FDUsed"        : str(fd_used),
                                                    "Memory"        : str(memory)
                                                }
                        
                                results["Record"]["Nodes"].append(new_node)
                        else:
                            if cur_row > 1:
                                use_row = True

                        cur_row         += 1
                    # build all the bindings

                except Exception,h:
                    self.lg("Get All Nodes Failed with Ex(" + str(h) + ")", 6)
                    results     = build_dict("SUCCESS", "No Nodes", { "Nodes" : [] })
                # end of try/ex for getting the queue

        except Exception,k:
            err_msg             = "Failed to run return_all_cluster_node_details with Ex(" + str(k) + ")"
            self.lg("ERROR: " + str(err_msg), 0)
            self.m_status       = "Failed"
            results             = build_dict("FAILED", str(err_msg), { "Nodes" : [] })
        # end of try/ex

        return results
    # end of return_all_cluster_node_details


    def add_on_cancel_callback(self):
        """Add a callback that will be invoked if RabbitMQ cancels the consumer
        for some reason. If RabbitMQ does cancel the consumer,
        on_consumer_cancelled will be invoked by pika.

        """
        self.lg("Adding consumer cancellation callback", 6)
        self.m_channel.add_on_cancel_callback(self.on_consumer_cancelled)

    # end of add_on_cancel_callback


    def on_consumer_cancelled(self, method_frame):
        """Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
        receiving messages.

        :param pika.frame.Method method_frame: The Basic.Cancel frame

        """
        self.lg("Consumer was cancelled remotely, shutting down(" + str(method_frame) + ")", 6)

        if self.m_channel:
            self.m_channel.close()

    # end of on_consumer_cancelled


    def start_consuming(self):
        """This method sets up the consumer by first calling
        add_on_cancel_callback so that the object is notified if RabbitMQ
        cancels the consumer. It then issues the Basic.Consume RPC command
        which returns the consumer tag that is used to uniquely identify the
        consumer with RabbitMQ. We keep the value to use it when we want to
        cancel consuming. The on_message method is passed in as a callback pika
        will invoke when a message is fully received.

        """
        self.lg("Issuing consumer related RPC commands", 6)
        self.add_on_cancel_callback()

        self.lg("Consuming Msgs from Queue(" + str(self.m_queue) + ")", 6)

        if self.m_consumer_tag != None:
            self.m_consumer_tag = self.m_channel.basic_consume(self.on_message, queue=self.m_queue, consumer_tag=self.m_consumer_tag)
        else:
            self.m_consumer_tag = self.m_channel.basic_consume(self.on_message, queue=self.m_queue)

    # end of start_consuming


    def on_message(self, unused_channel, basic_deliver, properties, body):
        """Invoked by pika when a message is delivered from RabbitMQ. The
        channel is passed for your convenience. The basic_deliver object that
        is passed in carries the exchange, routing key, delivery tag and
        a redelivered flag for the message. The properties passed in is an
        instance of BasicProperties with the message properties and the body
        is the message that was sent.

        :param pika.channel.Channel unused_channel: The channel object
        :param pika.Spec.Basic.Deliver: basic_deliver method
        :param pika.Spec.BasicProperties: properties
        :param str|unicode body: The message body

        """

        received_log    = "Received(" + str(self.m_cur_msg_count) + ") MessageTag(" + str(basic_deliver.delivery_tag) + ") From(" + str(properties.app_id) + ") Body(" + str(body)[0:10] + ")"
        self.lg(received_log, 6)

        if self.m_debug_received:
            std_log     = "Received(" + str(self.m_cur_msg_count) + ") MessageTag(" + str(basic_deliver.delivery_tag) + ") From(" + str(properties.app_id) + ") Body(" + str(body) + ")"
            print std_log

        self.acknowledge_message(basic_deliver.delivery_tag)
        self.m_cur_msg_count    += 1

        if self.m_num_amqp_msgs != 0 and self.m_cur_msg_count >= self.m_num_amqp_msgs:


            if self.m_cur_msg_count >= self.m_num_amqp_msgs:
                self.lg("Stopping Consumer Received(" + str(self.m_cur_msg_count) + ") ConfiguredToReceive(" + str(self.m_num_amqp_msgs) + ")", 6)
            else:
                self.lg("Stopping Consumer", 6)
                
            self.stop_consuming()
        else:
            sleep(self.m_publish_interval)

    # end of on_message


    def acknowledge_message(self, delivery_tag):
        """Acknowledge the message delivery from RabbitMQ by sending a
        Basic.Ack RPC method for the delivery tag.

        :param int delivery_tag: The delivery tag from the Basic.Deliver frame

        """
        self.lg("Acknowledging message(" + str(delivery_tag) + ")", 6)
        self.m_channel.basic_ack(delivery_tag)

    # end of acknowledge_message


    def stop_consuming(self):
        """Tell RabbitMQ that you would like to stop consuming by sending the
        Basic.Cancel RPC command.

        """
        if self.m_channel:
            self.lg("Sending a Basic.Cancel RPC command to RabbitMQ", 6)

            if self.m_debug:
                print "Stopping Consuming"
            self.m_channel.basic_cancel(self.on_cancelok, self.m_consumer_tag)
    # end of stop_consuming


    def on_cancelok(self, unused_frame):
        """This method is invoked by pika when RabbitMQ acknowledges the
        cancellation of a consumer. At this point we will close the channel.
        This will invoke the on_channel_closed method once the channel has been
        closed, which will in-turn close the connection.

        :param pika.frame.Method unused_frame: The Basic.CancelOk frame

        """
        self.lg("RabbitMQ acknowledged the cancellation of the consumer", 6)
        self.stop()

    # end of on_cancelok


# end of RabbitMessageConsumer

