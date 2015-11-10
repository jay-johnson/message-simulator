A Message Simulator for Clusters
================================================

This project is a lightweight testing automation tool for helping validate a cluster's High Availability, performance, and resilience.

![The Message Simulator](http://levvel.io/wp-content/uploads/2015/11/Message-Simulator-Logo.png)

This project supports creating normal messaging operational traffic load with the ability to subject the cluster to external events in real time. If you know what type of traffic your cluster will handle, then this repository can help you predict and identify where bottlenecks will happen ahead of a production outage (at midnight). The focus for this initial version is for RabbitMQ clusters with the ability to support Redis and ZeroMQ in the future.

If you do not have a running RabbitMQ cluster, please refer to our [How to setup a RabbitMQ Cluster with Docker Guide](https://github.com/GetLevvel/testing-rabbitmq-clustering-with-docker) 

[Table of Contents](#toc)
=========================

[1. Overview](#overview)

[2. Features](#features)

[3. Learn More](#learn-more)

[4. Getting Started](#getting-started)

[5. Setup and Installation](#setup-and-installation)

- [5.1. Networking](#networking)

- [5.2. Installation for use with a local Docker RabbitMQ Cluster](#installation-for-use-with-a-local-docker-rabbitmq-cluster)

- [5.3. Validating SSH Credentials are ready](#validating-ssh-credentials-are-ready)

[5.4. Hello World Simulation](#hello-world-simulation)

[6. How to run Message Simulations](#how-to-run-message-simulations)

- [6.1. General Usage](#general-usage)

- [6.2. Absolute Path Example](#absolute-path-example)

- [6.3. Relative Path Example](#relative-path-example)

[7. Technical Documentation](#technical-documentation)

- [7.1. How Simulations Work](#how-simulations-work)

- [7.1.1. Simulation Processing Order and Notes](#simulation-processing-order-and-notes)

[8. Running Messaging Simulations](#running-messaging-simulations)

- [8.1. Running Load Simulations](#running-load-simulations)

- [8.2. Running High Availability Simulations](#running-high-availability-simulations)

  - [8.2.1 HA Tests Coming Soon](#ha-tests-coming-soon)

- [8.3 Running Stress Simulations](#running-stress-simulations)

- [8.4 Building your own Simulation](#building-your-own-simulation)

  - [8.4.1 JSON Messaging Simulation Model Overview](#json-messaging-simulation-model-overview)

    - [8.4.1.1 RabbitMQ Connection Object](#rabbitmq-connection-object)

    - [8.4.1.2 Consumers Descriptions](#consumers-descriptions)

    - [8.4.1.3 Exchanges List](#exchanges-list)

    - [8.4.1.4 Queues List](#queues-list)

    - [8.4.1.5 Bindings List](#bindings-list)

    - [8.4.1.6 Messages List](#messages-list)

  - [8.4.2 Building your own Messages and Custom Control Events](#building-your-own-messages-and-custom-control-events)

  - [8.4.3 Simulation Attributes and Configuration](#simulation-attributes-and-configuration)

[9. Troubleshooting](#troubleshooting)

[10. Resources](#resources)

[11. Contributing](#contributing)

[12. License](#license)


## Overview
------------

```
├── monitoring
│   ├── bindings.sh           - Inspect the cluster's Bindings
│   ├── exchanges.sh          - Inspect the cluster's Exchanges
│   ├── msg_queues.sh         - Inspect the cluster's Queues Messaging Details
│   ├── queues.sh             - Inspect the cluster's Queues
│   ├── rst                   - Inspect the cluster's Status
├── run_message_simulation.py - Command line driver for Message Simulations and requires a simulation file to start
├── simulations
│   └── rabbit
│       ├── burst
│       │   └── burst_1_send_100000_messages.json - Support for Burst tests is coming soon.
│       ├── ha
│       │   ├── ha_1_start_sending_and_crash_a_node.json - Testing that the cluster supports load and handles a remote node outage without interruption
│       │   ├── ha_2_start_sending_and_stop_then_start_a_node.json - Testing that the cluster supports message traffic load during a remote node outage and restart without interruption
│       │   └── ha_3_network_latency_event_during_messaging.json - Testing how the cluster handles a network latency event where the remote node's cluster Port 25672 is blocked
│       ├── load
│       │   ├── load_1_send_100000_messages.json - Load test that the system can handle 100000 messages
│       │   ├── load_2_start_sending_and_consuming_messages.json - Load test that publishing messages and consuming messages works and shut the consumers down 'At End'
│       │   └── load_3_start_sending_and_leave_consumers_running.json - Load test and leave the consumers running at the end of the test
│       ├── setup_validation
│       │   ├── docker_cluster_hello_world.json - Validation sanity check with a running local Docker RabbitMQ Cluster
│       │   ├── hello_world.json - Simple sanity check
│       │   ├── validate_1_ssh_credentials_across_cluster.json - Validate that all the cluster's nodes have the SSH keys deployed to control the cluster remotely
│       │   ├── validate_2_consumer_works.json - Testing that Exchanges, Queues, and Messages can be sent through the cluster
│       │   └── validate_3_send_100_messages.json - Testing that the cluster supports sending some messages
│       └── stress
│           ├── stress_1_a_send_10000000_msgs_over_fanout_to_many_queues.json - Stress the cluster's internal resources by publishing to a Fanout Exchange with many Queues subscribed. This test also spawns multiple publisher processes that utilize the stress_1_b simulation file for publishing to the same exchange at the same time during the test.
│           └── stress_1_b_send_10000000_msgs_over_fanout_to_many_queues.json - Stress publisher worker configuration for stress_1_a
└── src
    ├── logger.py - Colorized logging to stdout and syslog
    ├── message_simulator.py - Message Simulator with state machine logic to handle advanced tests
    ├── rabbit_consumer_configs - Consumer test configurations
    │   └── _test.json - Sample configuration
    ├── rabbit_message_consumer.py - Rabbit Async Consumer for consuming messages
    ├── rabbit_message_publisher.py - Rabbit Async Publisher (Test Driver) class for message simulations. This creates all broker entities, performs broker interfacing for statistics, and can spawn consumers and worker publishers for advanced messaging simulations.
    ├── __start_rabbit_mq_consumer.py - Standalone wrapper for running a RabbitMQ Consumer process
    └── utils.py - Utility functions

```

## Features
-----------

The technology in this repository is implemented in Python 2.7 with JSON files. The goal is for creating easy-to-run Message Simulations modeled in JSON to help with hardening message queue clusters. The initial version only supports RabbitMQ with Redis and ZeroMQ coming soon.

## Learn More
-------------

Here are some underlying systems and components:

| Technology                 | Learn More Link                                     |
| -------------------------- | --------------------------------------------------- |
| RabbitMQ                   | https://www.rabbitmq.com/                           |
| RabbitMQ Getting Started   | https://www.rabbitmq.com/getstarted.html            |
| RabbitMQ High Availability | https://www.rabbitmq.com/reliability.html           |
| RabbitMQ Debugging         | https://www.rabbitmq.com/man/rabbitmqctl.1.man.html |

## Getting Started
------------------

## Setup and Installation 

Install the base RPMs (Assumes Fedora/CentOS)

```
$ sudo yum install -y python-setuptools git-core telnet net-tools erlang
$ sudo yum install -y http://www.rabbitmq.com/releases/rabbitmq-server/v3.5.6/rabbitmq-server-3.5.6-1.noarch.rpm
$ /usr/sbin/rabbitmq-plugins enable rabbitmq_mqtt rabbitmq_stomp rabbitmq_management  rabbitmq_management_agent rabbitmq_management_visualiser rabbitmq_federation rabbitmq_federation_management sockjs
$ sudo pip install --upgrade pip
$ sudo pip install pika==0.10.0
```

### Networking

For now, the Message Simulation tests target connecting to a RabbitMQ cluster available at the URI: [amqp://guest:guest@rabbit1:5672/](https://github.com/GetLevvel/message-simulator/blob/b8d3fcee1be762efdd7e7e755873236be79ac6b0/simulations/rabbit/setup_validation/hello_world.json#L13)

By default most environments will not have a working RabbitMQ broker available at ```rabbit1``` that is listening on TCP port 5672 by default. To test if you do, you can use the command:

```
$ telnet rabbit1 5672
telnet: rabbit1: Name or service not known
rabbit1: Unknown host
$
```

For getting the simulator running with a local Docker RabbitMQ Cluster, please make sure your /etc/hosts file maps the hostnames ```rabbit1 rabbit2 rabbit3``` to the loopback IP address for 127.0.0.1:

```
$ cat /etc/hosts
127.0.0.1           localhost localhost.localdomain localhost4 localhost4.localdomain4 rabbit1 rabbit2 rabbit3
::1                 localhost localhost.localdomain localhost6 localhost6.localdomain6

$
````

If you have a cluster running on a different FQDN than ```rabbit1``` or behind a load balancer, you can add the IP address to your /etc/hosts the same way. For documentation purposes let's say it is 10.1.1.2:

```
$ cat /etc/hosts
127.0.0.1           localhost localhost.localdomain localhost4 localhost4.localdomain4 
::1                 localhost localhost.localdomain localhost6 localhost6.localdomain6

# Our hypothetical RabbitMQ Cluster running behind 10.1.1.2
10.1.1.2         rabbit1 rabbit2 rabbit3
$
```

Once ```rabbit1``` is resolvable to a host, you can confirm connectivity is ready with the command:

```
$ telnet rabbit1 5672
Trying 127.0.0.1...
telnet: connect to address 127.0.0.1: Connection refused
$
```

This command failed because there is no Broker listening on TCP port 5672 running on ```rabbit1```. Please start the cluster (For those using the Docker RabbitMQ Cluster Repo just run ```3_start.sh``` from the file: https://github.com/GetLevvel/testing-rabbitmq-clustering-with-docker/blob/master/3_start.sh). 

Once the cluster is running and the network has a resolvable IP for the hostname ```rabbit1```, then these commands can be used to ensure the required networking connectivity is ready for message simulations:

```
$ telnet rabbit1 5672
Trying 127.0.0.1...
Connected to rabbit1.
Escape character is '^]'.
^]

telnet> quit
Connection closed.
$
```

or

```
$ sudo netstat -apn | grep 5672
tcp6       0      0 :::15672                :::*                    LISTEN      32370/docker-proxy  
tcp6       0      0 :::5672                 :::*                    LISTEN      32379/docker-proxy  
$
```

### Installation for use with a local Docker RabbitMQ Cluster

The Message Simulator has only been validated on Fedora 22.

1. To setup a local Docker RabbitMQ Cluster please refer to:

  https://github.com/GetLevvel/testing-rabbitmq-clustering-with-docker

1. These repositories can be cloned locally to any directory, but for simplifying the documentation we will assume they are cloned to the same parent directory ```/opt``` so that by running the command ```ls /opt``` the two repositories appear in the directory like:

  ```
  $ git clone https://github.com/GetLevvel/testing-rabbitmq-clustering-with-docker.git /opt/
  ```

  ```
  $ git clone https://github.com/GetLevvel/message-simulator.git /opt/
  ```

  ```
  $ ls /opt
  message-simulator  testing-rabbitmq-clustering-with-docker
  $ 
  ```

1. Start your cluster with the script: 
  
  https://github.com/GetLevvel/testing-rabbitmq-clustering-with-docker/blob/master/3_start.sh

1. Confirm the Docker RabbitMQ Cluster responds and all members report back that they are running:

  ```
  $ /opt/message-simulator/monitoring/rst

  Running Cluster Status

  +----------------+------+---------+
  |      name      | type | running |
  +----------------+------+---------+
  | rabbit@rabbit1 | disc | True    |
  | rabbit@rabbit2 | ram  | True    |
  | rabbit@rabbit3 | disc | True    |
  +----------------+------+---------+

  $
  ```

**If you are using a pre-existing RabbitMQ cluster that was not built using the Docker Containers please continue setting up your environment for the Message Simulator**


### Validating SSH Credentials are ready

In this version, the Message Simulator uses SSH to invoke remote commands across a cluster. To do this the Simulator assumes SSH credentials are installed on each remote broker host to perform Broker management actions.

To confirm your cluster's SSH credentials are ready for the Simulator please run this as root:

```
# /opt/message-simulator/run_message_simulation.py -f /opt/message-simulator/simulations/rabbit/setup_validation/validate_1_ssh_credentials_across_cluster.json 

Running Simulation(simulations/rabbit/setup_validation/validate_1_ssh_credentials_across_cluster.json)

    SSH Credentials Validated(rabbit1)
    SSH Credentials Validated(rabbit2)
    SSH Credentials Validated(rabbit3)

Done Simulation(simulations/rabbit/setup_validation/validate_1_ssh_credentials_across_cluster.json)

#
```

Confirm the cluster's remote nodes reported that **SSH Credentials Validated**


### Hello World Simulation

Once the ssh credentials are validated, please confirm the Hello World example works.

As root, please run and confirm the stdout looks similar to: 

```
/opt/message-simulator# ./run_message_simulation.py -f simulations/rabbit/setup_validation/hello_world.json

Running Simulation(simulations/rabbit/setup_validation/hello_world.json)

Done Waiting for Messages(1)

Running Connector Summary

Checking Exchanges(8)
    Exchange({'VHost': '/', 'Internal': 'False', 'Arguments': '', 'AutoDelete': 'False', 'Exchange': 'Hello.Ex', 'Policy': '', 'Durable': 'False', 'Type': 'topic'})
    Exchange({'VHost': '/', 'Internal': 'False', 'Arguments': '', 'AutoDelete': 'False', 'Exchange': 'amq.direct', 'Policy': '', 'Durable': 'True', 'Type': 'direct'})
    Exchange({'VHost': '/', 'Internal': 'False', 'Arguments': '', 'AutoDelete': 'False', 'Exchange': 'amq.fanout', 'Policy': '', 'Durable': 'True', 'Type': 'fanout'})
    Exchange({'VHost': '/', 'Internal': 'False', 'Arguments': '', 'AutoDelete': 'False', 'Exchange': 'amq.headers', 'Policy': '', 'Durable': 'True', 'Type': 'headers'})
    Exchange({'VHost': '/', 'Internal': 'False', 'Arguments': '', 'AutoDelete': 'False', 'Exchange': 'amq.match', 'Policy': '', 'Durable': 'True', 'Type': 'headers'})
    Exchange({'VHost': '/', 'Internal': 'True', 'Arguments': '', 'AutoDelete': 'False', 'Exchange': 'amq.rabbitmq.log', 'Policy': '', 'Durable': 'True', 'Type': 'topic'})
    Exchange({'VHost': '/', 'Internal': 'True', 'Arguments': '', 'AutoDelete': 'False', 'Exchange': 'amq.rabbitmq.trace', 'Policy': '', 'Durable': 'True', 'Type': 'topic'})
    Exchange({'VHost': '/', 'Internal': 'False', 'Arguments': '', 'AutoDelete': 'False', 'Exchange': 'amq.topic', 'Policy': '', 'Durable': 'True', 'Type': 'topic'})

Checking Queues(1)
    Queue({'Consumers': '0', 'Durable': 'False', 'ConsumerUtilization': '', 'MsgsReadyRam': '0', 'State': 'running', 'Arguments': '', 'Memory': '17024', 'Policy': '', 'MsgsRam': '0', 'MsgsReady': '0', 'MsgsPersistent': '0', 'Node': 'rabbit@rabbit1', 'PID': '', 'SyncSlaveNodes': '', 'MsgsBytes': '0', 'Name': 'hello', 'AutoDelete': 'False', 'ExclusiveConsumerTag': '', 'Msgs': '0', 'SlaveNodes': '', 'ExclusiveConsumerPID': '', 'OwnerPID': '', 'MsgsUnacked': '0'})

Checking Bindings(2)
    Binding Ex(amq.direct) => Queue(hello) RoutingKey(queue)
    Binding Ex(Hello.Ex) => Queue(hello) RoutingKey(queue)

Checking Nodes(3)
    Node({'Uptime': '', 'Processors': '189', 'SocketsUsed': '829', 'FDUsed': '1024', 'RunQueue': '2', 'Memory': '22', 'Type': 'rabbit@rabbit1', 'Name': '', 'StatsLevel': '1', 'SocketsTotal': 'True', 'FDs': '7549155', 'ProcTotal': 'disc', 'Running': '0', 'ProcUsed': '1048576'})
    Node({'Uptime': '', 'Processors': '184', 'SocketsUsed': '829', 'FDUsed': '1024', 'RunQueue': '2', 'Memory': '22', 'Type': 'rabbit@rabbit2', 'Name': '', 'StatsLevel': '1', 'SocketsTotal': 'True', 'FDs': '5921395', 'ProcTotal': 'disc', 'Running': '0', 'ProcUsed': '1048576'})
    Node({'Uptime': '', 'Processors': '184', 'SocketsUsed': '829', 'FDUsed': '1024', 'RunQueue': '2', 'Memory': '22', 'Type': 'rabbit@rabbit3', 'Name': '', 'StatsLevel': '1', 'SocketsTotal': 'True', 'FDs': '5276085', 'ProcTotal': 'disc', 'Running': '0', 'ProcUsed': '1048576'})

Done Simulation(simulations/hello_world.json)

# 
```

## How to run Message Simulations

For tests that require remote execution on a Broker (most of the HA tests) please make sure to run as root. If you are running with the Docker RabbitMQ Cluster you do not have to run as root.

Here are a few example commands for running a Message Simulation.


### General Usage
  ```
  $ cd /opt/message-simulator
  $ ./run_message_simulation.py -f <Simulation File>
  ```

### Absolute Path Example

  ```
  $ /opt/message-simulator/run_message_simulation.py -f /opt/message-simulator/simulations/rabbit/setup_validation/hello_world.json
  ```

### Relative Path Example

  ```
  $ ./run_message_simulation.py -f simulations/rabbit/load/load_1_send_100000_messages.json
  ```

## Technical Documentation
--------------------------

### How Simulations Work

Here is the general control flow for running a Simulation:

| Steps to Run a Simulation                    | View Source |
| -------------------------------------------- | ----------- |
| Create and Connect the Simulation Publisher  | [src/message_simulator.py#L67-L73](https://github.com/GetLevvel/message-simulator/blob/b8d3fcee1be762efdd7e7e755873236be79ac6b0/src/message_simulator.py#L67-L73) |
| Run the Simulation                           | [src/message_simulator.py#L136](https://github.com/GetLevvel/message-simulator/blob/b8d3fcee1be762efdd7e7e755873236be79ac6b0/src/message_simulator.py#L136) |
| Simulation Publisher connects to the Cluster | [src/rabbit_message_publisher.py#L255-L264](https://github.com/GetLevvel/message-simulator/blob/b8d3fcee1be762efdd7e7e755873236be79ac6b0/src/rabbit_message_publisher.py#L255-L264) |
| Once connected create the Broker Entities    | [src/rabbit_message_publisher.py#L413-L455](https://github.com/GetLevvel/message-simulator/blob/b8d3fcee1be762efdd7e7e755873236be79ac6b0/src/rabbit_message_publisher.py#L413-L455) |
| Start Consumers                              | [src/rabbit_message_publisher.py#L694-L698](https://github.com/GetLevvel/message-simulator/blob/b8d3fcee1be762efdd7e7e755873236be79ac6b0/src/rabbit_message_publisher.py#L694-L698) |
| Start Message Publishing                     | [src/rabbit_message_publisher.py#L235-L239](https://github.com/GetLevvel/message-simulator/blob/b8d3fcee1be762efdd7e7e755873236be79ac6b0/src/rabbit_message_publisher.py#L235-L239) |
| Handling Message Publishing                  | [src/rabbit_message_publisher.py#L1049-L1094](https://github.com/GetLevvel/message-simulator/blob/b8d3fcee1be762efdd7e7e755873236be79ac6b0/src/rabbit_message_publisher.py#L1049-L1094) |
| Stop when all Messages are Published         | [src/rabbit_message_publisher.py#L1038-L1040](https://github.com/GetLevvel/message-simulator/blob/b8d3fcee1be762efdd7e7e755873236be79ac6b0/src/rabbit_message_publisher.py#L1038-L1040) |
| Run Summary and Reports                      | [src/rabbit_message_publisher.py#L2562-L2593](https://github.com/GetLevvel/message-simulator/blob/b8d3fcee1be762efdd7e7e755873236be79ac6b0/src/rabbit_message_publisher.py#L2562-L2593) |

#### Simulation Processing Order and Notes

1. Create and Connect the Simulation Publisher (for this version only RabbitMQ is supported)

1. Run the Simulation

1. The Simulation Publisher connects to the Cluster 

1. Once the Publisher has a connection, it will create the Broker Entities for the test

    For RabbitMQ the entity creation order is: Exchanges, Queues, Bindings

1. Start Consumers

    Because each simulation utilizes an asynchronous producer implementation, the simulation will wait to start the Consumers until all Queues report back that they were declared ok. This ensures there is no race condition when initializing the simulation's Consumers before their appropriate Queue is ready.

1. Start Message Publishing
    
    Message publishing will begin once all Queues are bound. In this version all simulations require at least **one** Binding before messages will be published.

1. Handling Message Publishing

    The Message Simulator supports sending **AMQP** messages and **Custom Control Events**. By utilizing the "MessageType" attribute in the Message Simulation JSON Model file, tests can pass special messages to initiate Control Events.

    Here is an example of an **AMQP** MessageType:
            
    [simulations/rabbit/ha/ha_1_start_sending_and_crash_a_node.json#L76](https://github.com/GetLevvel/message-simulator/blob/b8d3fcee1be762efdd7e7e755873236be79ac6b0/simulations/rabbit/ha/ha_1_start_sending_and_crash_a_node.json#L76)

    Here is a **Custom Control Event** example of **Stopping a running Broker Node in the Cluster**:

    [simulations/rabbit/ha/ha_1_start_sending_and_crash_a_node.json#L128](https://github.com/GetLevvel/message-simulator/blob/b8d3fcee1be762efdd7e7e755873236be79ac6b0/simulations/rabbit/ha/ha_1_start_sending_and_crash_a_node.json#L128)

    Each of the currently supported MessageTypes are defined in the ```publish_message``` method here:
    
    [src/rabbit_message_publisher.py#L1049-L1094](https://github.com/GetLevvel/message-simulator/blob/b8d3fcee1be762efdd7e7e755873236be79ac6b0/src/rabbit_message_publisher.py#L1049-L1094)

1. Stop when all Messages are Published
    
    Once all messages are processed, the Simulation Publisher will perform a summary and stop.

1. Summary and Reporting

## Running Messaging Simulations
--------------------------------

### Running Load Simulations

For running Load Simulations use any of the included JSON files in the ```./simulations/rabbit/load/``` directory.

These tests are focused on creating a constant and predictable load on your cluster. These tests are the first step in preparing a cluster for production.

```
$ tree simulations/rabbit/load/
simulations/rabbit/load/
├── load_1_send_100000_messages.json
├── load_2_start_sending_and_consuming_messages.json
└── load_3_start_sending_and_leave_consumers_running.json
$
```

### Running High Availability Simulations

For running High Availability (HA) Simulations use any of the included JSON files in the ```./simulations/rabbit/ha/``` directory. For Non-Docker RabbitMQ clusters, these simulations require ssh password-less login with the ability to run as root on the remote host for ```sudo service rabbitmq-server stop|start``` capability.

These tests are all about building confidence in a cluster's resiliency, durability, persistence, client handling, monitoring tools and determining your team's outage handling processes when events outside of normal operation occur. 

#### HA Tests Coming Soon

  - Utilizing different Broker entities combined with ha-policies during external events
  - Tests for demonstrating how messages can get copied but not lost with ha-policies like durability and persistence enabled
  - Unsynchronized Cluster Slaves trying to join a running cluster during a simulation and the Master Node crashes
  - Unsynchronized Cluster Slaves trying to join a running cluster during a simulation and running an explicit synchronization
  - Internal cluster TCP network events at varying flapping rates instead of being 100% unavailable (like [ha_3_network_latency_event_during_messaging.json](https://github.com/GetLevvel/message-simulator/blob/master/simulations/rabbit/ha/ha_3_network_latency_event_during_messaging.json))
  - Forcibly disconnecting producers and consumers from the default RabbitMQ TCP Port
  - Tests for demonstrating message loss without HA
  - Tests filling an HDD using brokers set up in disc or ram mode and persistence and durability enabled
  - 100% CPU and memory utilization tests
  - More tests aimed at helping diagnose network partitioning and other split brain events
  - Cluster nodes that leave and join clusters repeatedly
  - Restarting cluster members when the cluster is set to perform automatic synchronization on startup
  - Full cluster outage restoration during messaging
  - Federation network latency and outage events
  - Sending messages with large payloads during an outage event
  - Alternate Exchange tests

```
$ tree simulations/rabbit/ha/
simulations/rabbit/ha/
├── ha_1_start_sending_and_crash_a_node.json
├── ha_2_start_sending_and_stop_then_start_a_node.json
└── ha_3_network_latency_event_during_messaging.json
$
```

### Running Stress Simulations

For running Stress Simulations use any of the included JSON files in the ```./simulations/rabbit/stress/``` directory. 

The Stress Simulations are focused on creating broker entities that will stress the cluster in unexpected ways. The first test creates a single Fanout Exchange that has over 150 Queues bound to it and then forks 10 independent Publisher processes that will help publish messages to the same Fanout Exchange at the same time. The goal is not to exceed your cluster's ability but to stress the internal cluster's processing and resources to see how this internal stress affects your monitoring tools and more importantly where bottlenecks will occur for your cluster's clients. 

Future releases will include tests:

- Sending large messages (static and randomly generated ones)
- Shovel and Federation
- Stress via AMQP Headers routing
- Testing with too many producers 

Here are the current available Stress Simulations:

```
$ tree simulations/rabbit/stress/
simulations/rabbit/stress/
├── stress_1_a_send_10000000_msgs_over_fanout_to_many_queues.json
└── stress_1_b_send_10000000_msgs_over_fanout_to_many_queues.json
$
```

### Building your own Simulation

Each Message Simulation is a JSON file that Models the objects, events, and entities you would like to test. The JSON outline was laid out for making it easy to write specific use case tests without having to change the underlying code driving the test. 

Here is the starting point for building your own simulation:

```
{
  "Simulation" : {
      "Name" : <The Name of the Simulation Test>,
      "Type" : "Rabbit",
      "Rabbit" : {
      }
  },
  "Consumers" : { },
  "BrokerEntities" : {
      "Exchanges" : [ ],
      "Queues"    : [ ],
      "Bindings"  : [ ],
      "Messages"  : [ ]
  }
}
```

#### JSON Messaging Simulation Model Overview 

##### RabbitMQ Connection Object

  Here is a sample RabbitMQ Connection Description from [Load Test 1](https://github.com/GetLevvel/message-simulator/blob/b8d3fcee1be762efdd7e7e755873236be79ac6b0/simulations/rabbit/load/load_1_send_100000_messages.json#L10-L18)

  ```
  "Rabbit" :  {
              "Name"          : "Load_1_Pub",
              "BrokerAddress" : [ "rabbit1", "rabbit2", "rabbit3" ],
              "BrokerURL"     : "amqp://guest:guest@rabbit1:5672/%2F?connection_attempts=3&heartbeat_interval=3600",
              "Account"       : {
                                "User"        : "guest",
                                "Password"    : "guest"
              }
  }
  ```
  
  Please set the RabbitMQ BrokerURL to the appropriate URI for connecting to the RabbitMQ cluster. For debugging purposes you can set the **Name** value to a name you want for showing it in the logs and for tracking the connection.

##### Consumers Descriptions

The Message Simulator creates Consumers as independent processes running on the host system. The Simulator tracks the PID for the new process and autogenerates a unique configuration file for each one. This allows consumers to be re-run independently from a simulation as well as for parallelizing how fast messages are consumed from a Queue. Consumers assume the Exchanges, Queues, and Bindings are already created for them to function properly.

Here is a sample Consumers Description from [Load Test 3](https://github.com/GetLevvel/message-simulator/blob/b8d3fcee1be762efdd7e7e755873236be79ac6b0/simulations/rabbit/load/load_3_start_sending_and_leave_consumers_running.json#L19-L47) 

```
"Consumers" : {
    "PrefixName"    : "Load_3_",
    "PIDDir"        : "/tmp/",
    "TmpConfigDir"  : "/tmp/test6consumers_",
    "ConsumeQueues" : [
                {
                    "NumConsumers"  : "2",
                    "Starter"       : "src/__start_rabbit_mq_consumer.py",
                    "ConsumeInt"    : "0.5",
                    "CheckDone"     : "0.5",
                    "Queue"         : "Load_3_A_Messages",
                    "ReplyToQueue"  : "Load_3_A_Responses",
                    "NumberMessages": "100",
                    "ValidateBody"  : false,
                    "Expected"      : {}
                },
                {
                    "NumConsumers"  : "2",
                    "Starter"       : "src/__start_rabbit_mq_consumer.py",
                    "ConsumeInt"    : "0.5",
                    "CheckDone"     : "0.5",
                    "Queue"         : "Load_3_B_Messages",
                    "ReplyToQueue"  : "Load_3_B_Responses",
                    "NumberMessages": "100",
                    "ValidateBody"  : false,
                    "Expected"      : {}
                }
    ]
}
```

A simulation will start a certain number of consumers (**NumConsumers**) as unique processes by using the **Starter** script for consuming messages from the assigned **Queue** name. Each consumer can be configured to stop once they consume an expected **NumberMessages** from their Queue. Consumers can be setup to consume at a rate of one message per **ConsumeInt** seconds. Consumers will be able to validate the body of each message in an upcoming release.

From this example, the Message Simulator will create:

  - 2 Consumers using the [src/__start_rabbit_mq_consumer.py](https://github.com/GetLevvel/message-simulator/blob/master/src/__start_rabbit_mq_consumer.py) as a wrapper script to consume 100 messages from the **Load_3_A_Messages** Queue
  - 2 Consumers using the [src/__start_rabbit_mq_consumer.py](https://github.com/GetLevvel/message-simulator/blob/master/src/__start_rabbit_mq_consumer.py) as a wrapper script to consume 100 messages from the **Load_3_B_Messages** Queue. 
  
All 4 Consumers will shut down as soon as they can consume 100 messages from their assigned Queue.

##### Exchanges List

  Each node in the Exchanges list describes an Exchange to create in the cluster. 

  Here is a sample Exchanges list from [Load Test 1](https://github.com/GetLevvel/message-simulator/blob/b8d3fcee1be762efdd7e7e755873236be79ac6b0/simulations/rabbit/load/load_1_send_100000_messages.json#L21-L30)

  ```
  "Exchanges" : [ 
                {
                    "Type"          : "Topic",
                    "Name"          : "Load_1.Ex",
                    "Durable"       : false,
                    "AutoDelete"    : false,
                    "Exclusive"     : false,
                    "Attributes"    : {}
                }
  ]
  ```

  The simulator will walk through this list of Exchange descriptions and setup each Exchange based off the properties in the test. Federation attributes will be supported and defined in the **Attributes** section in a future release.

##### Queues List
 
  Each node in the Queues list describes a Queue to create in the cluster. 

  Here is a sample Queues list from [Load Test 1](https://github.com/GetLevvel/message-simulator/blob/b8d3fcee1be762efdd7e7e755873236be79ac6b0/simulations/rabbit/load/load_1_send_100000_messages.json#L31-L60)

  ```
  "Queues"    : [
                {
                    "Name"          : "Load_1_A_Messages",
                    "Durable"       : false,
                    "AutoDelete"    : false,
                    "Exclusive"     : false,
                    "Attributes"    : {}
                },
                {
                    "Name"          : "Load_1_B_Messages",
                    "Durable"       : false,
                    "AutoDelete"    : false,
                    "Exclusive"     : false,
                    "Attributes"    : {}
                },
                {
                    "Name"          : "Load_1_A_Responses",
                    "Durable"       : false,
                    "AutoDelete"    : false,
                    "Exclusive"     : false,
                    "Attributes"    : {}
                },
                {
                    "Name"          : "Load_1_B_Responses",
                    "Durable"       : false,
                    "AutoDelete"    : false,
                    "Exclusive"     : false,
                    "Attributes"    : {}
                }
  ]
  ```

  The simulator will walk through this list of Queue descriptions and apply the attributes to each Queue. Please note the next version of the Message Simulator will support explicit HA attributes for Queues and Mirroring inside the **Attributes** dictionary as key-value pairs from the RabbitMQ [Highly Available Queues](https://www.rabbitmq.com/ha.html) documentation. For now, we are using rabbitmqctl to manually test HA.

##### Bindings List

  Each node in the Bindings list describes a RabbitMQ binding for an Exchange to route messages to a Queue

  Here is a sample Bindings list from [Load Test 1](https://github.com/GetLevvel/message-simulator/blob/b8d3fcee1be762efdd7e7e755873236be79ac6b0/simulations/rabbit/load/load_1_send_100000_messages.json#L61-L72)

  ```
  "Bindings"  : [
                {
                    "Exchange"      : "Load_1.Ex",
                    "Queue"         : "Load_1_A_Messages",
                    "RoutingKey"    : "Load_1.A"
                },
                {
                    "Exchange"      : "Load_1.Ex",
                    "Queue"         : "Load_1_B_Messages",
                    "RoutingKey"    : "Load_1.B"
                }
  ]
  ```

  The simulator will apply each binding to the RabbitMQ cluster which will assign the Exchange a route key for delivering messages to the Queue.

  * For Cell 1 in the Binding list above, Exchange **Load_1.Ex** will route messages with a Routing Key of **Load_1.A** to be delivered to the Queue named **Load_1.A**
  * For Cell 2 in the Binding list above, Exchange **Load_1.Ex** will route messages with a Routing Key of **Load_1.B** to be delivered to the Queue named **Load_1.B**

##### Messages List

Each node in the Messages list is considered a set of messages. The simulator can send batches of AMQP messages, and it also supports handling for Custom Control Events as well.

Here is a sample Messages list from [High Availability Test 2](https://github.com/GetLevvel/message-simulator/blob/b8d3fcee1be762efdd7e7e755873236be79ac6b0/simulations/rabbit/ha/ha_2_start_sending_and_stop_then_start_a_node.json#L73-L289)

```
"Messages"  : [
          {
              "NumberToSend"  : "100",
              "MessageType"   : "AMQP",
              "Exchange"      : "HA_2.Ex",
              "Queue"         : "",
              "ReplyTo"       : "HA_2_A_Responses",
              "RoutingKey"    : "HA_2.A",
              "Headers"       : {
                                  "Test"      : "HA 2",
                                  "Message"   : "Route to A"
                              },
              "Body"          : {
                                  "Data"      : "Route to A"
                              },
              "AppID"         : "",
              "ClusterID"     : "",
              "UserID"        : "",
              "MessageID"     : "",        
              "ContentType"   : "application/json",
              "Encoding"      : "",
              "DeliveryMode"  : "2",
              "Priority"      : "0",
              "CorrelationID" : "",
              "Expiration"    : "",
              "Timestamp"     : ""
          },
          {
              "NumberToSend"  : "100",
              "MessageType"   : "AMQP",
              "Exchange"      : "HA_2.Ex",
              "Queue"         : "",
              "ReplyTo"       : "HA_2_B_Responses",
              "RoutingKey"    : "HA_2.B",
              "Headers"       : {
                                  "Test"      : "HA 2",
                                  "Message"   : "Route to B"
                              },
              "Body"          : {
                                  "Data"      : "Route to B"
                              },
              "AppID"         : "",
              "ClusterID"     : "",
              "UserID"        : "",
              "MessageID"     : "",        
              "ContentType"   : "application/json",
              "Encoding"      : "",
              "DeliveryMode"  : "2",
              "Priority"      : "0",
              "CorrelationID" : "",
              "Expiration"    : "",
              "Timestamp"     : ""
          },
          {
              "NumberToSend"  : "1",
              "MessageType"   : "Stop Broker",
              "Host"          : "rabbit3",
              "User"          : "root",
              "Commands"      : [
                                  "/usr/bin/ssh root@rabbit3 \"ps auwwwx | grep rabbitmq | grep boot | grep -v grep | awk '{print $2}'\" ",
                                  "/usr/bin/ssh root@rabbit3 \"kill -9 %i\" "
                              ],
              "Excepted"      : {
                                  "Nodes" : [
                                              {
                                                  "Name"      : "rabbit1",
                                                  "Running"   : "True",
                                                  "Type"      : "disc"
                                              },
                                              {
                                                  "Name"      : "rabbit2",
                                                  "Running"   : "True",
                                                  "Type"      : "disc"
                                              },
                                              {
                                                  "Name"      : "rabbit3",
                                                  "Running"   : "True",
                                                  "Type"      : "disc"
                                              }
                                          ]
                              }
          },
          {
              "NumberToSend"  : "500",
              "MessageType"   : "AMQP",
              "Exchange"      : "HA_2.Ex",
              "Queue"         : "",
              "ReplyTo"       : "HA_2_B_Responses",
              "RoutingKey"    : "HA_2.B",
              "Headers"       : {
                                  "Test"      : "HA 2",
                                  "Message"   : "Route to B"
                              },
              "Body"          : {
                                  "Data"      : "Route to B"
                              },
              "AppID"         : "",
              "ClusterID"     : "",
              "UserID"        : "",
              "MessageID"     : "",        
              "ContentType"   : "application/json",
              "Encoding"      : "",
              "DeliveryMode"  : "2",
              "Priority"      : "0",
              "CorrelationID" : "",
              "Expiration"    : "",
              "Timestamp"     : ""
          },
          {
              "NumberToSend"  : "500",
              "MessageType"   : "AMQP",
              "Exchange"      : "HA_2.Ex",
              "Queue"         : "",
              "ReplyTo"       : "HA_2_A_Responses",
              "RoutingKey"    : "HA_2.A",
              "Headers"       : {
                                  "Test"      : "HA 2",
                                  "Message"   : "Route to A"
                              },
              "Body"          : {
                                  "Data"      : "Route to A"
                              },
              "AppID"         : "",
              "ClusterID"     : "",
              "UserID"        : "",
              "MessageID"     : "",        
              "ContentType"   : "application/json",
              "Encoding"      : "",
              "DeliveryMode"  : "2",
              "Priority"      : "0",
              "CorrelationID" : "",
              "Expiration"    : "",
              "Timestamp"     : ""
          },
          {
              "NumberToSend"  : "1",
              "MessageType"   : "Start Broker",
              "Host"          : "rabbit3",
              "User"          : "root",
              "Commands"      : [
                                  "/usr/bin/ssh root@rabbit3 \"/sbin/service rabbitmq-server stop\" ",
                                  "/usr/bin/ssh root@rabbit3 \"/sbin/service rabbitmq-server start\" "
                              ],
              "Excepted"      : {
                                  "Nodes" : [
                                              {
                                                  "Name"      : "rabbit1",
                                                  "Running"   : "True",
                                                  "Type"      : "disc"
                                              },
                                              {
                                                  "Name"      : "rabbit2",
                                                  "Running"   : "True",
                                                  "Type"      : "disc"
                                              },
                                              {
                                                  "Name"      : "rabbit3",
                                                  "Running"   : "True",
                                                  "Type"      : "disc"
                                              }
                                          ]
                              }
          },
          {
              "NumberToSend"  : "500",
              "MessageType"   : "AMQP",
              "Exchange"      : "HA_2.Ex",
              "Queue"         : "",
              "ReplyTo"       : "HA_2_A_Responses",
              "RoutingKey"    : "HA_2.A",
              "Headers"       : {
                                  "Test"      : "HA 2",
                                  "Message"   : "Route to A"
                              },
              "Body"          : {
                                  "Data"      : "Route to A"
                              },
              "AppID"         : "",
              "ClusterID"     : "",
              "UserID"        : "",
              "MessageID"     : "",        
              "ContentType"   : "application/json",
              "Encoding"      : "",
              "DeliveryMode"  : "2",
              "Priority"      : "0",
              "CorrelationID" : "",
              "Expiration"    : "",
              "Timestamp"     : ""
          },
          {
              "NumberToSend"  : "500",
              "MessageType"   : "AMQP",
              "Exchange"      : "HA_2.Ex",
              "Queue"         : "",
              "ReplyTo"       : "HA_2_B_Responses",
              "RoutingKey"    : "HA_2.B",
              "Headers"       : {
                                  "Test"      : "HA 2",
                                  "Message"   : "Route to B"
                              },
              "Body"          : {
                                  "Data"      : "Route to B"
                              },
              "AppID"         : "",
              "ClusterID"     : "",
              "UserID"        : "",
              "MessageID"     : "",        
              "ContentType"   : "application/json",
              "Encoding"      : "",
              "DeliveryMode"  : "2",
              "Priority"      : "0",
              "CorrelationID" : "",
              "Expiration"    : "",
              "Timestamp"     : ""
          }
]
```

[High Availability Test 2](https://github.com/GetLevvel/message-simulator/blob/master/simulations/rabbit/ha/ha_2_start_sending_and_stop_then_start_a_node.json) will send these AMQP Messages and handle these Custom Control Events in the following order:

  1. Send 100 AMQP Messages to the Exchange **HA_2.Ex** with **HA_2.A** as the Routing Key
    - Build each message using the assigned JSON headers, JSON body, and assign message properties if that property is not set to an empty string value of **""**.
  1. Send 100 AMQP Messages to the Exchange **HA_2.Ex** with **HA_2.B** as the Routing Key
    - Build each message using the assigned JSON headers, JSON body, and assign message properties if that property is not set to an empty string value of **""**.
  1. Stop a Broker targeting **rabbit3** as the cluster node to stop using ssh
  1. Send 500 AMQP Messages to the Exchange **HA_2.Ex** with **HA_2.B** as the Routing Key
    - Build each message using the assigned JSON headers, JSON body, and assign message properties if that property is not set to an empty string value of **""**.
  1. Send 500 AMQP Messages to the Exchange **HA_2.Ex** with **HA_2.A** as the Routing Key
    - Build each message using the assigned JSON headers, JSON body, and assign message properties if that property is not set to an empty string value of **""**.
  1. Start a Broker targeting **rabbit3** as the cluster node to start using ssh
  1. Send 500 AMQP Messages to the Exchange **HA_2.Ex** with **HA_2.A** as the Routing Key
    - Build each message using the assigned JSON headers, JSON body, and assign message properties if that property is not set to an empty string value of **""**.
  1. Send 500 AMQP Messages to the Exchange **HA_2.Ex** with **HA_2.B** as the Routing Key
    - Build each message using the assigned JSON headers, JSON body, and assign message properties if that property is not set to an empty string value of **""**.

More Custom Control Events and message types will be supported in the future, here is the current list of supported message types:

  1. AMQP
  1. Stop Broker
  1. Start Broker
  1. Start Worker Publisher
  1. Add Network Latency Event
  1. Remove All Network Latency Events
  1. Validate SSH Credentials
  1. Validate Docker Credentials
  1. Reset All Broker Entities

#### Building your own Messages and Custom Control Events

  You can develop and extend support for your own messages and events by editing the [publish_message code](https://github.com/GetLevvel/message-simulator/blob/b8d3fcee1be762efdd7e7e755873236be79ac6b0/src/rabbit_message_publisher.py#L1049-L1074).

#### Simulation Attributes and Configuration

Here is the full set of supported attributes and configuration properties for building your own Message Simulation. Values you can change are marked inside of the **<** **>** characters.

```
{
"Simulation" : {
  "Name" : <The Name of the Simulation Test>,
  "StopFile" : <A file that when present will initiate the Message Simulator to stop>,
  "PauseFile" : <A file that when present will initiate the Message Simulator to pause>,
  "Interval" : <Float value for determining how long to wait between sending a message>,
  "CheckDone" : <Float value for how long to wait to check until the Simulation is done>,
  "ResetAll" : <Boolean for reseting all previously created cluster entities before starting the test values can be: true | false>,
  "Type" : "Rabbit",
  "Rabbit" : {
    "Name" : <The name of the Simulation Publisher in /var/log/messages>,
    "BrokerAddress: [
      "rabbit1",
      "rabbit2",
      "rabbit3"
    ],
    "BrokerURL" : "amqp://guest:guest@rabbit1:5672/%2F?connection_attempts=3&heartbeat_interval=3600",
    "Account" : {
      "User" : "guest",
      "Password" : "guest"
    }
  },
  "Consumers" : {
    "PrefixName" : <Prefix logging name for each consumer in /var/log/messages>,
    "PIDDir" : <Directory for storing each Consumer's PID files>,
    "TmpConfigDir" : <Directory for storing autogenerated Consumer JSON Configuration Files>,
    "StopConsumers" : <If set to the value "At End" the Consumers will be shut down at the end of the Simulation otherwise they are left running>,
    "ConsumeQueues" : [
      {
        "NumConsumers" : <Number of Consumers to run with this configuration>,
        "Starter" : <You can write your own Consumer, by default we provide one that works with "src/__start_rabbit_mq_consumer.py">,
        "ConsumeInt" : <Float value for how long to wait between consuming a message from the queue>,
        "CheckDone" : <Float value for determining how long to wait after consuming all messages before stopping>,
        "Queue" : <Name of a Broker Queue to consumer messages>,
        "ReplyToQueue" : <Name of a Reply to Queue this is not used in this version>,
        "NumberMessages" : <Integer for the Number of Messages to Read before stopping>,
        "ValidateBody" : <Boolean indicating expected AMQP message fields to validate>,
        "Expected" : { "Support Coming soon" }
      }
    ]
  },
  "BrokerEntities" : {
    "Exchanges" : [
      {
        "Type" : <Type of AMQP Exchange to create not case sensitive and supports Topic, Fanout, Direct, Headers>,
        "Name" : <Name of the AMQP Exchange where a Producer will publish messages>,
        "Durable" : <Boolean indicating is the Exchange Durable or not>,
        "AutoDelete" : <Boolean indicating is the Exchange Auto Delete or not>,
        "Exclusive" : <Boolean indicating is the Exchange Exclusive or not>,
        "Attributes" : { "Support Coming Soon" }
      }
    ],
    "Queues" : [
      {
        "Name" : <Name of the Queue where a Consumer reads Messages>,
        "Durable" : <Boolean indicating is the Queue Durable or not>,
        "AutoDelete" : <Boolean indicating is the Queue Auto Delete or not>,
        "Exclusive" : <Boolean indicating is the Queue Exclusive or not>,
        "Attributes" : { "Support Coming Soon" }
      }
    ],
    "Bindings" : [
      {
        "Exchange" : <Name of the Exchange as the Source for the AMQP Binding>,
        "Queue" : <Name of the Queue as the destination for the AMQP Binding>,
        "RoutingKey" : <String AMQP Routing Key for connecting an Exchange to a Queue based off pattern matching>
      }
    ],
    "Messages" : [
      {
        "NumberToSend" : <Integer for how many of copies this Message to send>,
        "MessageType" : "AMQP",
        "Exchange" : <Name of the Exchange where messages will be sent>,
        "Queue" : <Name of the Queue where messages will be sent>,
        "ReplyTo" : <Name of the Reply To Attribute assigned inside the Message - Does not auto-reply yet>,
        "RoutingKey" : <String for the AMQP Routing Key assigned inside the Message>,
        "ContentType" : "application/json",
        "Headers" : {
          JSON Key/Value Pairs for the Message's AMQP Headers
          "HeaderKey"  : "HeaderValue"
        },
        "Body" : {
          JSON Key/Value Pairs for the Message's Body Payload
          "Data"  : "Some Data"
        },
        "AppID" : <Application ID Attribute for the AMQP Message>,
        "ClusterID" : <Cluster ID Attribute for the AMQP Message>,
        "UserID" : <User ID Attribute for the AMQP Message>,
        "MessageID" : <Message ID Attribute for the AMQP Message>,
        "Encoding" : <Encoding Attribute for the AMQP Message>,
        "DeliveryMode" : <Integer as a String holding the Delivery Mode Attribute for the AMQP Message>,
        "Priority" : <Integer as a String holding the Priority Attribute for the AMQP Message>,
        "CorrelationID" : <Correlation ID Attribute for the AMQP Message>,
        "Expiration" : <Expiration Attribute for the AMQP Message>,
        "Timestamp" : <Timestamp Attribute for the AMQP Message>
      },
      {
          "NumberToSend"  : "1",
          "MessageType"   : "Start Worker Publisher",
          "NumberWorkers" : "Integer as a String for the number of Workers to start as publishers",
          "Command"       : "nohup ./run_message_simulation.py -f <simulation file to target> &"
      },
      {
          "NumberToSend"  : "1",
          "MessageType"   : "Stop Broker",
          "Host"          : "String Hostname of the cluster Node to use for example: rabbit2",
          "User"          : "root",
          "Commands"      : [
                            "docker exec -it <docker name of the running Container> /opt/simulator/tools/stop_node.sh"
                        ],
          "Expected"      : {
                            "Nodes" : [
                                        {
                                            "Name"      : "rabbit1",
                                            "Running"   : "Boolean String for validating the running state of this Node in the cluster: True | False",
                                            "Type"      : "Type of cluster Node: ram | disc"
                                        },
                                        {
                                            "Name"      : "rabbit2",
                                            "Running"   : "Boolean String for validating the running state of this Node in the cluster: True | False",
                                            "Type"      : "Type of cluster Node: ram | disc"
                                        },
                                        {
                                            "Name"      : "rabbit3",
                                            "Running"   : "Boolean String for validating the running state of this Node in the cluster: True | False",
                                            "Type"      : "Type of cluster Node: ram | disc"
                                        }
                                    ]
                        }
      },
      {
          "NumberToSend"  : "1",
          "MessageType"   : "Start Broker",
          "Host"          : "String Hostname of the cluster Node to use for example: rabbit2",
          "User"          : "root",
          "Commands"      : [
                            "docker exec -it <docker name of the running Container> /opt/simulator/tools/start_node.sh"
                        ],
          "Expected"      : {
                            "Nodes" : [
                                        {
                                            "Name"      : "rabbit1",
                                            "Running"   : "Boolean String for validating the running state of this Node in the cluster: True | False",
                                            "Type"      : "Type of cluster Node: ram | disc"
                                        },
                                        {
                                            "Name"      : "rabbit2",
                                            "Running"   : "Boolean String for validating the running state of this Node in the cluster: True | False",
                                            "Type"      : "Type of cluster Node: ram | disc"
                                        },
                                        {
                                            "Name"      : "rabbit3",
                                            "Running"   : "Boolean String for validating the running state of this Node in the cluster: True | False",
                                            "Type"      : "Type of cluster Node: ram | disc"
                                        }
                                    ]
                        }
      },
      {
        "NumberToSend"  : "1",
        "MessageType"   : "Reset All Broker Entities",
        "Host"          : "String Hostname of the cluster Node to use for example rabbit1",
        "User"          : "root",
        "Commands"      : [
                        ],
        "Excepted"      : {
                        }
      }
    ]
  }
}
```

## Troubleshooting
------------------

1. Fixing things when an HA test leaves your cluster in an unknown state

If you are using the Docker RabbitMQ Cluster you can just stop the cluster with ```4_stop.sh``` and then restart it with ```3_start.sh```. If the cluster is not utilizing the Docker Containers, then it will require a bit more detective work. Find which hosts are not responding with the command:

```
$ ./monitoring/rst 

Running Cluster Status

+----------------+------+---------+
|      name      | type | running |
+----------------+------+---------+
| rabbit@rabbit1 | disc | True    |
| rabbit@rabbit2 | ram  | True    |
| rabbit@rabbit3 | disc | False   |
+----------------+------+---------+

$
```

From this hypothetical example, it appears **rabbit3** is no longer running in a good state. Let's gracefully try to restore services first (so message loss does not happen). Here is a general RabbitMQ debugging guide:

  1. Make sure iptables is not blocking anything:

  ```
  # iptables -L
  Chain INPUT (policy ACCEPT)
  target     prot opt source               destination         

  Chain FORWARD (policy ACCEPT)
  target     prot opt source               destination         

  Chain OUTPUT (policy ACCEPT)
  target     prot opt source               destination     
  #
  ```

  If there are iptable DROP entries listed for port 5672, 25672, or 15672 please make sure to remove them. 5672 is the default RabbitMQ TCP port and 25672 is the internal clustering port. If permitted you can remove all the iptables entries by flushing them with ```iptables -F```

  1. Check for free hard drive space

  ```
  [root@rabbit3 /]# df -h
  Filesystem                                                                                         Size  Used Avail Use% Mounted on
  /dev/mapper/docker-253:1-1457956-418c5146d311bc6e40508e8eb677f5dc4370bf46fc815d119b7b17fa2f84aa33   99G  520M   93G   1% /
  tmpfs                                                                                              2.0G     0  2.0G   0% /dev
  shm                                                                                                 64M     0   64M   0% /dev/shm
  tmpfs                                                                                              2.0G     0  2.0G   0% /sys/fs/cgroup
  tmpfs                                                                                              2.0G     0  2.0G   0% /run/secrets
  /dev/mapper/fedora-root                                                                             35G   29G  5.1G  85% /etc/hosts
  tmpfs                                                                                              2.0G     0  2.0G   0% /proc/kcore
  tmpfs                                                                                              2.0G     0  2.0G   0% /proc/timer_stats
  [root@rabbit3 /]#
  ```

  1. Stop the Server

      ```sudo service rabbitmq-server stop```

  1. Start the Server
      
      ```sudo service rabbitmq-server start```

  1. What do the logs say?

      ```cat /var/log/rabbitmq/rabbit.log```

  1. If the server immediately stops or fails to even start

      Failing to start the RabbitMQ broker means we may not be able to restore messages.
      
      ```
      # Stop the application:
      /usr/sbin/rabbitmqctl stop_app
    
      # Reset the application:
      /usr/sbin/rabbitmqctl reset

      # Start the application:
      /usr/sbin/rabbitmqctl start_app
      ```

      
      1. If the server starts and stays running after the reset

        ```
        # Stop the application:
        /usr/sbin/rabbitmqctl stop_app

        # Try joining the cluster:
        /usr/sbin/rabbitmqctl join_cluster rabbit@rabbit1
      
        # Start the application:
        /usr/sbin/rabbitmqctl start_app
        ```

      1. If the server stays up but fails to join the cluster:

        ```
        [root@rabbit3 /]# /usr/sbin/rabbitmqctl join_cluster rabbit@rabbit1 
        Clustering node rabbit@rabbit3 with rabbit@rabbit1 ...
        Error: mnesia_unexpectedly_running
        #
        ```

        Check if there is a partition in the cluster: 
        
        ```
        [root@rabbit3 /]# rabbitmqctl cluster_status
        Cluster status of node rabbit@rabbit3 ...
        [{nodes,[{disc,[rabbit@rabbit1,rabbit@rabbit3]},{ram,[rabbit@rabbit2]}]},
         {running_nodes,[rabbit@rabbit3]},
         {cluster_name,<<"rabbit@rabbit1">>},
         {partitions,[{rabbit@rabbit3,[rabbit@rabbit1,rabbit@rabbit2]}]}]
        #
        ```

        Try stopping and starting it 

        ```
        [root@rabbit3 /]# rabbitmqctl stop_app
        Stopping node rabbit@rabbit3 ...
        [root@rabbit3 /]# rabbitmqctl start_app
        Starting node rabbit@rabbit3 ...
        [root@rabbit3 /]# 
        [root@rabbit3 /]# rabbitmqctl cluster_status                      
        Cluster status of node rabbit@rabbit3 ...
        [{nodes,[{disc,[rabbit@rabbit1,rabbit@rabbit3]},{ram,[rabbit@rabbit2]}]},
         {running_nodes,[rabbit@rabbit1,rabbit@rabbit2,rabbit@rabbit3]},
         {cluster_name,<<"rabbit@rabbit1">>},
         {partitions,[]}]
        [root@rabbit3 /]# 

        ```

        From outside the cluster confirm each node is back in a good running state:

        ```
        message-simulator$ ./monitoring/rst 

        Running Cluster Status

        +----------------+------+---------+
        |      name      | type | running |
        +----------------+------+---------+
        | rabbit@rabbit1 | disc | True    |
        | rabbit@rabbit2 | ram  | True    |
        | rabbit@rabbit3 | disc | True    |
        +----------------+------+---------+

        message-simulator$ 
        ```
      
      1. If the server is not able to startup after trying a reset

         I am interested in hearing what others respond with for restoration policies (like backing up RabbitMQ files to persisted storage), but to get things going again please delete the RabbitMQ persistent data directory which will restore itself when the RabbitMQ broker starts again. 
         
         **Messages can be lost at this point.**

         ```
         [root@rabbit3 /]# service rabbitmq-server stop
         [root@rabbit3 /]# rm -rf /var/lib/rabbitmq/mnesia/rabbit/*
         [root@rabbit3 /]# service rabbitmq-server start
         [root@rabbit3 /]# rabbitmqctl stop_app                   
         Stopping node rabbit@rabbit3 ...
         [root@rabbit3 /]# rabbitmqctl reset                      
         Resetting node rabbit@rabbit3 ...
         [root@rabbit3 /]# rabbitmqctl join_cluster rabbit@rabbit1
         Clustering node rabbit@rabbit3 with rabbit@rabbit1 ...
         [root@rabbit3 /]# rabbitmqctl start_app                  
         Starting node rabbit@rabbit3 ...
         [root@rabbit3 /]# rabbitmqctl cluster_status             
         Cluster status of node rabbit@rabbit3 ...
         [{nodes,[{disc,[rabbit@rabbit1,rabbit@rabbit3]},{ram,[rabbit@rabbit2]}]},
          {running_nodes,[rabbit@rabbit1,rabbit@rabbit2,rabbit@rabbit3]},
          {cluster_name,<<"rabbit@rabbit1">>},
          {partitions,[]}]
         [root@rabbit3 /]# 
         ```

  1. If the server started and stays running for 30 seconds but fails to join the cluster:

      ````
      # Stop the application:
      /usr/sbin/rabbitmqctl stop_app
    
      # Try joining the cluster:
      /usr/sbin/rabbitmqctl join_cluster rabbit@rabbit1

      # Start the application:
      /usr/sbin/rabbitmqctl start_app
      ```

  1. Confirm the cluster has all the nodes in a good running state:

  ```
  $ rabbitmqadmin list nodes name type running
  +----------------+------+---------+
  |      name      | type | running |
  +----------------+------+---------+
  | rabbit@rabbit1 | disc | True    |
  | rabbit@rabbit2 | ram  | True    |
  | rabbit@rabbit3 | disc | True    |
  +----------------+------+---------+
  $
  ```


## Resources
------------

| Topics                           | References                                             |
| ---------------------------------| ------------------------------------------------------ |
| RabbitMQ Reliability Guide       | https://www.rabbitmq.com/reliability.html              |
| RabbitMQ Highly Available Queues | https://www.rabbitmq.com/ha.html                       |
| RabbitMQ Unsynchronised Slaves   | https://www.rabbitmq.com/ha.html#unsynchronised-slaves |
| RabbitMQ Federation              | https://www.rabbitmq.com/federation.html               |
| RabbitMQ Debugging               | https://www.rabbitmq.com/man/rabbitmqctl.1.man.html    |

## Contributing
---------------

This section gives an overview of how to contribute.

**Pull Requests are Always Welcome!**

We will appreciate any contributions no matter how small. Your time is valuable so thank you in advance. We are always excited to receive pull requests, and we do our best to process them quickly. 

Any significant improvement should be documented as a GitHub issue before anybody starts working on it. This will help us coordinate, track and prioritize development.

Here is a general way to contribute:

1. Fork this repository to your GitHub account
1. Clone the Fork repository
1. Create a feature branch off master
1. Commit changes and tests to the feature branch
1. When the code is ready, open a Pull Request for merging your Fork's feature branch into master
1. We will review the Pull Request and address any questions in the comments section of the Pull Request
1. After an initial "Looks Good", we will initiate a regression test where the feature branch is applied to master and confirm nothing breaks
1. If something breaks we will add comments to the Pull Request documenting the failure and help work through solutions with you
1. Once everything passes we will merge your feature branch into master

## License
----------

  Apache 2.0 License

  Copyright 2015 Levvel LLC

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.


