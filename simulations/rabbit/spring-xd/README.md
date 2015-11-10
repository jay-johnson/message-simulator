Distributed Spring XD with RabbitMQ Clustering
==============================================

This guide is for helping set up Spring XD with a RabbitMQ Cluster for MQTT, AMQP, and Message Bus. It also has the initial hooks for the Message Simulator to help test your RabbitMQ Cluster that is powering Spring XD.

![Distributed Spring XD with RabbitMQ Clustering](http://levvel.io/wp-content/uploads/2015/11/Spring-XD-Distributed-Environment-with-RabbitMQ-Clustering.png)

### Installation

From the Spring XD guide: 

http://docs.spring.io/spring-xd/docs/current/reference/html/#_install_spring_xd

```
wget http://repo.spring.io/libs-release/org/springframework/xd/spring-xd/1.2.1.RELEASE/spring-xd-1.2.1.RELEASE-dist.zip .
unzip spring-xd-1.2.1.RELEASE-dist.zip
```

For this document, Spring XD was extracted to: 

```
/opt/spring-xd-1.2.1.RELEASE
```

Spring XD in a Non-distributed Environment
------------------------------------------

Spring XD is easier to get started in a non-distributed mode because all the components run locally in 2 terminals:

1. Everything runs locally in the SingleNode Application (xd-singlenode) and you can watch the logs
1. Use the XD Shell (xd-shell) to interface and play with your local Environment

For those wanting to try Spring XD out, it is a good way to get started.


Spring XD in a Distributed Environment
--------------------------------------

Here is an overview for setting up Spring XD to run distributed for high availability and utilizing a RabbitMQ Cluster.


#### Spring XD Start Scripts

| Technology                 | How to Run               | Source |
| -------------------------- | ------------------------ | ------ |
| Database | ```spring-xd-1.2.1.RELEASE/hsqldb/bin/hsqldb-server``` | [hsqldb-server Source](https://github.com/spring-projects/spring-xd/blob/1767d6c79a94da2f659815b0810e9ac32b6c16bf/scripts/hsqldb/hsqldb-server) |
| Zookeeper Ensemble | ```spring-xd-1.2.1.RELEASE/zookeeper/bin/zkServer.sh``` | [zkServer.sh Source](https://github.com/apache/zookeeper/blob/branch-3.4/bin/zkServer.sh) |
| Spring XD Admin | ```spring-xd-1.2.1.RELEASE/xd/bin/xd-admin``` | [xd-admin Source](https://github.com/spring-projects/spring-xd/blob/1767d6c79a94da2f659815b0810e9ac32b6c16bf/scripts/xd/xd-admin) |
| Spring XD Containers | ```spring-xd-1.2.1.RELEASE/xd/bin/xd-container``` | [xd-container Source](https://github.com/spring-projects/spring-xd/blob/1767d6c79a94da2f659815b0810e9ac32b6c16bf/scripts/xd/xd-container) |
| Spring XD Shell | ```spring-xd-1.2.1.RELEASE/shell/bin/xd-shell``` | [xd-shell Source](https://github.com/spring-projects/spring-xd/blob/1767d6c79a94da2f659815b0810e9ac32b6c16bf/scripts/shell/xd-shell) |
| RabbitMQ Cluster | [Start the Demo Cluster](https://github.com/GetLevvel/testing-rabbitmq-clustering-with-docker#starting-the-cluster) | [3_start.sh Source](https://github.com/GetLevvel/testing-rabbitmq-clustering-with-docker/blob/master/3_start.sh) |

#### Ordering for Start Scripts with Notes on High Availability

Start these components in order:

1. RabbitMQ Clustered for High Availability
  - If you need one: 
      https://github.com/GetLevvel/testing-rabbitmq-clustering-with-docker
1. Data Storage Hadoop/MySQL/Postgres/Oracle - Clustering these is outside the scope of this README
  - For testing purposes there is a local HSQLDB server that runs with: ```spring-xd-1.2.1.RELEASE/hsqldb/bin/hsqldb-server```
  - [View hsqldb Source](https://github.com/spring-projects/spring-xd/blob/1767d6c79a94da2f659815b0810e9ac32b6c16bf/scripts/hsqldb/hsqldb-server)
1. Running Zookeeper Ensemble - Clustered across at least 3 nodes
  - Installs itself with: ```spring-xd-1.2.1.RELEASE/zookeeper/bin/install-zookeeper```
  - Runs with: ```spring-xd-1.2.1.RELEASE/zookeeper/bin/zkServer.sh```
  - [View install-zookeeper Source](https://github.com/spring-projects/spring-xd/blob/1767d6c79a94da2f659815b0810e9ac32b6c16bf/scripts/zookeeper/bin/install-zookeeper)
  - [View zkServer.sh Source](https://github.com/apache/zookeeper/blob/branch-3.4/bin/zkServer.sh)
1. Spring XD Admin instances - Running across at least 2 nodes (Zookeeper handles leadership decisions)
  - Runs with: ```spring-xd-1.2.1.RELEASE/xd/bin/xd-admin```
  - [View xd-admin Source](https://github.com/spring-projects/spring-xd/blob/1767d6c79a94da2f659815b0810e9ac32b6c16bf/scripts/xd/xd-admin)
1. Spring XD Containers - These host your Source/Sink Streams, Jobs, and Taps for processing work (like OpenShift Nodes hosting applications). Try spreading an even number of running containers across as many host nodes as necessary to mitigate single points of failure and parallelizing for performance.
  - Runs with: ```spring-xd-1.2.1.RELEASE/xd/bin/xd-container```
  - [View xd-container Source](https://github.com/spring-projects/spring-xd/blob/1767d6c79a94da2f659815b0810e9ac32b6c16bf/scripts/xd/xd-container)
1. Spring XD Shell - This is a command line shell for interfacing with the Spring XD environment  
  - Runs with: ```spring-xd-1.2.1.RELEASE/shell/bin/xd-shell```
  - [View xd-shell Source](https://github.com/spring-projects/spring-xd/blob/1767d6c79a94da2f659815b0810e9ac32b6c16bf/scripts/shell/xd-shell)

After going through this guide, and if you have access to Docker then these will help:
https://hub.docker.com/u/springxd/


## Getting Started with a Non-Distributed Environment

In a new terminal, start the **xd-singlenode** (SingleNode Application) to start everything (DB, Zookeeper, Admin, and a single Container) on your local host:

```
$ cd spring-xd-1.2.1.RELEASE/xd/bin
spring-xd-1.2.1.RELEASE/xd/bin$ ./xd-singlenode

 _____                           __   _______
/  ___|          (-)             \ \ / /  _  \
\ `--. _ __  _ __ _ _ __   __ _   \ V /| | | |
 `--. \ '_ \| '__| | '_ \ / _` |  / ^ \| | | |
/\__/ / |_) | |  | | | | | (_| | / / \ \ |/ /
\____/| .__/|_|  |_|_| |_|\__, | \/   \/___/
      | |                  __/ |
      |_|                 |___/
1.2.1.RELEASE                    eXtreme Data


Started : SingleNodeApplication
Documentation: https://github.com/spring-projects/spring-xd/wiki

2015-11-04T17:16:37-0500 1.2.1.RELEASE INFO main singlenode.SingleNodeApplication - Starting SingleNodeApplication v1.2.1.RELEASE on localhost.localdomain with PID 7905 (/opt/spring-xd/spring-xd-1.2.1.RELEASE/xd/lib/spring-xd-dirt-1.2.1.RELEASE.jar started by user in /opt/spring-xd/spring-xd-1.2.1.RELEASE/xd/bin)
2015-11-04T17:16:37-0500 1.2.1.RELEASE INFO main singlenode.SingleNodeApplication

```


In another terminal start the **xd-shell** for interfacing with the Spring XD SingleNode Environment:

**Protip: xd-shell supports TAB autocompletion for almost everything**


```
$ cd spring-xd-1.2.1.RELEASE/shell/bin
spring-xd-1.2.1.RELEASE/shell/bin$ ./xd-shell
 _____                           __   _______
/  ___|          (-)             \ \ / /  _  \
\ `--. _ __  _ __ _ _ __   __ _   \ V /| | | |
 `--. \ '_ \| '__| | '_ \ / _` |  / ^ \| | | |
/\__/ / |_) | |  | | | | | (_| | / / \ \ |/ /
\____/| .__/|_|  |_|_| |_|\__, | \/   \/___/
      | |                  __/ |
      |_|                 |___/
eXtreme Data
1.2.1.RELEASE | Admin Server Target: http://localhost:9393
Welcome to the Spring XD shell. For assistance hit TAB or type "help".
xd:>
```

At this point your local host should have 2 running java proceses

```
$ ps auwwwx | grep java | grep spring
```

The xd-shell communicates using http://localhost:9393 to the xd-singlenode environment

```
$ sudo netstat -apn | grep 9393
tcp6       0      0 :::9393                 :::*                    LISTEN      7905/java           
$ 
```

### Creating a Stream

From the xd-shell terminal:

```
xd:>stream create --name ticktock --definition "time | log" --deploy
Created and deployed new stream 'ticktock'
xd:>
```

From the xd-singlenode terminal you should see output coming through:

```
2015-11-04T17:43:19-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Path cache event: path=/deployments/modules/allocated/14ba7b90-4bed-4ba8-994d-da0e218a16a5/ticktock.sink.log.1, type=CHILD_ADDED
2015-11-04T17:43:19-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Deploying module 'log' for stream 'ticktock'
2015-11-04T17:43:19-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Deploying module [ModuleDescriptor@9fc1045 moduleName = 'log', moduleLabel = 'log', group = 'ticktock', sourceChannelName = [null], sinkChannelName = [null], index = 1, type = sink, parameters = map[[empty]], children = list[[empty]]]
2015-11-04T17:43:19-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Path cache event: path=/deployments/modules/allocated/14ba7b90-4bed-4ba8-994d-da0e218a16a5/ticktock.source.time.1, type=CHILD_ADDED
2015-11-04T17:43:19-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Deploying module 'time' for stream 'ticktock'
2015-11-04T17:43:19-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Deploying module [ModuleDescriptor@3874088a moduleName = 'time', moduleLabel = 'time', group = 'ticktock', sourceChannelName = [null], sinkChannelName = [null], index = 0, type = source, parameters = map[[empty]], children = list[[empty]]]
2015-11-04T17:43:20-0500 1.2.1.RELEASE INFO DeploymentSupervisor-0 zk.ZKStreamDeploymentHandler - Deployment status for stream 'ticktock': DeploymentStatus{state=deployed}
2015-11-04T17:43:20-0500 1.2.1.RELEASE INFO task-scheduler-1 sink.ticktock - 2015-11-04 17:43:20
2015-11-04T17:43:21-0500 1.2.1.RELEASE INFO task-scheduler-1 sink.ticktock - 2015-11-04 17:43:21

... which continues every second

2015-11-04T17:45:28-0500 1.2.1.RELEASE INFO task-scheduler-3 sink.ticktock - 2015-11-04 17:45:28
2015-11-04T17:45:29-0500 1.2.1.RELEASE INFO task-scheduler-3 sink.ticktock - 2015-11-04 17:45:29
2015-11-04T17:45:30-0500 1.2.1.RELEASE INFO task-scheduler-3 sink.ticktock - 2015-11-04 17:45:30
2015-11-04T17:45:31-0500 1.2.1.RELEASE INFO task-scheduler-3 sink.ticktock - 2015-11-04 17:45:31

```

From the xd-shell terminal destroy the ticktock Stream

```
xd:>stream destroy --name ticktock
Destroyed stream 'ticktock'
xd:>
```

The xd-singlenode should log:

```

2015-11-04T17:46:37-0500 1.2.1.RELEASE INFO task-scheduler-9 sink.ticktock - 2015-11-04 17:46:37
2015-11-04T17:46:38-0500 1.2.1.RELEASE INFO task-scheduler-9 sink.ticktock - 2015-11-04 17:46:38
2015-11-04T17:46:39-0500 1.2.1.RELEASE INFO main-EventThread container.DeploymentListener - Undeploying module [ModuleDescriptor@3874088a moduleName = 'time', moduleLabel = 'time', group = 'ticktock', sourceChannelName = [null], sinkChannelName = [null], index = 0, type = source, parameters = map[[empty]], children = list[[empty]]]
2015-11-04T17:46:39-0500 1.2.1.RELEASE INFO main-EventThread container.DeploymentListener - Undeploying module [ModuleDescriptor@9fc1045 moduleName = 'log', moduleLabel = 'log', group = 'ticktock', sourceChannelName = [null], sinkChannelName = [null], index = 1, type = sink, parameters = map[[empty]], children = list[[empty]]]
2015-11-04T17:46:39-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Path cache event: path=/deployments/modules/allocated/14ba7b90-4bed-4ba8-994d-da0e218a16a5/ticktock.source.time.1, type=CHILD_REMOVED
2015-11-04T17:46:39-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Path cache event: path=/deployments/modules/allocated/14ba7b90-4bed-4ba8-994d-da0e218a16a5/ticktock.sink.log.1, type=CHILD_REMOVED

```

### Connecting Spring XD to a Docker RabbitMQ Cluster

1. Edit the servers.yml for the xd-singlenode instance

  ```
  vi spring-xd-1.2.1.RELEASE/xd/config/servers.yml
  ```

1. Find the section for the **RabbitMQ Properties** and set it for the RabbitMQ Cluster

  ```
  # RabbitMQ properties
  spring:
    rabbitmq:
     addresses: rabbit1:5672
     adminAddresses: http://rabbit1:15672
     nodes: rabbit@rabbit1
     username: guest
     password: guest
     virtual_host: /
     useSSL: false
     sslProperties:
  ```

1. Restart the xd-singlenode instance so it can connect to the RabbitMQ cluster as a Source and Sink Stream

    - CRTL+C from the xd-singlenode terminal
    - ```spring-xd-1.2.1.RELEASE/xd/bin$ ./xd-singlenode```


### Using the Message Simulator as a Source Stream with Spring XD

The Message Simulator has Spring XD simulations ready in:

https://github.com/GetLevvel/message-simulator/tree/master/simulations/rabbit/spring-xd


1. Let's run the first one with the command:

  ```
  /opt/message-simulator/run_message_simulation.py -f /opt/message-simulator/simulations/rabbit/spring-xd/xd_1_helloworld_source_stream_with_cluster.json
  ```

  This simulation will create the **rabbittest** queue and a topic exchange for routing messages to the queue and then send a message through the exchange to the queue. 

  Since Spring XD does not create queues let the simulator create the Broker Entities for you (and handle ha in upcoming releases)

1. Confirm the queue was created with:

  ```
  $ rabbitmqadmin list queues name node durable auto_delete messages consumers memory state exclusive_consumer_tag policy arguments
  +------------+----------------+---------+-------------+----------+-----------+--------+---------+------------------------+--------+-----------+
  |    name    |      node      | durable | auto_delete | messages | consumers | memory |  state  | exclusive_consumer_tag | policy | arguments |
  +------------+----------------+---------+-------------+----------+-----------+--------+---------+------------------------+--------+-----------+
  | rabbittest | rabbit@rabbit1 | False   | False       | 0        | 1         | 14152  | running |                        |        |           |
  +------------+----------------+---------+-------------+----------+-----------+--------+---------+------------------------+--------+-----------+
  ```


### Examining a RabbitMQ Source Stream


1. With the xd-shell we can start using our new queue with a RabbitMQ Source (Input) Stream by creating it in the xd-shell:

  ```
  xd:> stream create --name rabbittest --definition "rabbit | file --binary=true" --deploy
  Created and deployed new stream 'rabbittest'
  xd:>
  ```

1. Open a third terminal to tail the Sink (Output) file stored by default at: **/tmp/xd/output/rabbittest.out**

  Make sure to hit the 'Enter' button a few times to see the newest output

  ```
  $ tail -f /tmp/xd/output/rabbittest.out
  {"Data": "This is the Data from the Simulator's Spring XD Source Stream Test 1"}


  ```

1. Now run the simulator again with the same file (it does not delete or autocleanup any of the broker entities because this causes bad behavior with Spring XD):

  ```
  $ /opt/message-simulator/run_message_simulation.py -f /opt/message-simulator/simulations/rabbit/spring-xd/xd_1_helloworld_source_stream_with_cluster.json
  ```

1. From the Sink terminal confirm you see a new entry:

  ```
  {"Data": "This is the Data from the Simulator's Spring XD Source Stream Test 1"}
  ```

1. Now run the simulator again with the test 2 file (it does not delete or autocleanup any of the broker entities because this causes bad behavior with Spring XD):

  ```
  $ /opt/message-simulator/run_message_simulation.py -f /opt/message-simulator/simulations/rabbit/spring-xd/xd_2_source_stream_with_cluster.json
  ```

1. From the Sink terminal confirm you see 2 new entries:

  ```
  {"Data": "This is the Data from the Simulator's Spring XD Source Stream Test 2"}{"Data": "This is the Data from the Simulator's Spring XD Source Stream Test 2"}
  ```

1. At this point let's destroy our RabbitMQ Source Stream from the xd-shell:
  ```
  xd:>stream destroy --name rabbittest
  Destroyed stream 'rabbittest'
  xd:>
  ```

1. Confirm the xd-singlenode logged the destroy Stream event was processed:

  ```
  2015-11-04T20:07:51-0500 1.2.1.RELEASE INFO main-EventThread container.DeploymentListener - Undeploying module [ModuleDescriptor@5d7cf0c5 moduleName = 'rabbit', moduleLabel = 'rabbit', group = 'rabbittest', sourceChannelName = [null], sinkChannelName = [null], index = 0, type = source, parameters = map[[empty]], children = list[[empty]]]
  2015-11-04T20:07:52-0500 1.2.1.RELEASE INFO main-EventThread container.DeploymentListener - Undeploying module [ModuleDescriptor@782a0e82 moduleName = 'file', moduleLabel = 'file', group = 'rabbittest', sourceChannelName = [null], sinkChannelName = [null], index = 1, type = sink, parameters = map['binary' -> 'true'], children = list[[empty]]]
  2015-11-04T20:07:52-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Path cache event: path=/deployments/modules/allocated/d6be5ac1-e4ef-4a34-8e66-a072ad9fb146/rabbittest.source.rabbit.1, type=CHILD_REMOVED
  2015-11-04T20:07:52-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Path cache event: path=/deployments/modules/allocated/d6be5ac1-e4ef-4a34-8e66-a072ad9fb146/rabbittest.sink.file.1, type=CHILD_REMOVED
  ```


### Running RabbitMQ Sink tests with the Simulator


1. Create the Broker Entities to route messages to the Simulator Consumer using the **"test 3 a"** file:

  ```
  $ /opt/message-simulator/run_message_simulation.py -f /opt/message-simulator/simulations/rabbit/spring-xd/xd_3_a_create_sink_message_entities.json 
  ```

1. Now start the consumer to watch the preconfigured queue from a new terminal using the **"test 3 b"** file:

  ```
  $ /opt/message-simulator/src/__start_rabbit_mq_consumer.py -f /opt/message-simulator/simulations/rabbit/spring-xd/xd_3_b_run_sink_message_consumer.json 

  Running RabbitConsumer(/opt/message-simulator/simulations/rabbit/spring-xd/xd_3_b_run_sink_message_consumer.json)

  Received(0) MessageTag(1) From(MsgSimApp) Body({"Data": "This is the Data from the Simulator's Spring XD Sink Stream Test 3"})

  ```

1. From the xd-shell create the RabbitMQ Sink Stream that will publish messages to the Simulator's Consumer Exchange:

  ```
  xd:>stream create --name RabbitSinkStream --definition "time | rabbit --routingKey='\"Rabbit.MQTT.Test3.Rabbit1\"' --exchange='SpringXD.Sink.Ex' " --deploy
  Created and deployed new stream 'RabbitSinkStream'
  xd:>
  ```

1. The xd-singlenode terminal should log something similar:

  ```
  2015-11-04T21:19:45-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Path cache event: path=/deployments/modules/allocated/d6be5ac1-e4ef-4a34-8e66-a072ad9fb146/RabbitSinkStream.sink.rabbit.1, type=CHILD_ADDED
  2015-11-04T21:19:45-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Deploying module 'rabbit' for stream 'RabbitSinkStream'
  2015-11-04T21:19:45-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Deploying module [ModuleDescriptor@c4af9ea moduleName = 'rabbit', moduleLabel = 'rabbit', group = 'RabbitSinkStream', sourceChannelName = [null], sinkChannelName = [null], index = 1, type = sink, parameters = map['exchange' -> 'SpringXD.Sink.Ex', 'routingKey' -> '"Rabbit.MQTT.Test3.Rabbit1"'], children = list[[empty]]]
  2015-11-04T21:19:45-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Path cache event: path=/deployments/modules/allocated/d6be5ac1-e4ef-4a34-8e66-a072ad9fb146/RabbitSinkStream.source.time.1, type=CHILD_ADDED
  2015-11-04T21:19:45-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Deploying module 'time' for stream 'RabbitSinkStream'
  2015-11-04T21:19:45-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Deploying module [ModuleDescriptor@3e8ef66f moduleName = 'time', moduleLabel = 'time', group = 'RabbitSinkStream', sourceChannelName = [null], sinkChannelName = [null], index = 0, type = source, parameters = map[[empty]], children = list[[empty]]]
  2015-11-04T21:19:46-0500 1.2.1.RELEASE INFO DeploymentSupervisor-0 zk.ZKStreamDeploymentHandler - Deployment status for stream 'RabbitSinkStream': DeploymentStatus{state=deployed}

  ```

1. From the consumer's terminal you should start seeing messages coming in around once a second:

  ```
  $ /opt/message-simulator/src/__start_rabbit_mq_consumer.py -f /opt/message-simulator/simulations/rabbit/spring-xd/xd_3_b_run_sink_message_consumer.json 

  Running RabbitConsumer(/opt/message-simulator/simulations/rabbit/spring-xd/xd_3_b_run_sink_message_consumer.json)

  Received(0) MessageTag(1) From(None) Body(2015-11-04 21:19:49)
  Received(1) MessageTag(2) From(None) Body(2015-11-04 21:19:50)
  Received(2) MessageTag(3) From(None) Body(2015-11-04 21:19:51)
  Received(3) MessageTag(4) From(None) Body(2015-11-04 21:19:52)
  Received(4) MessageTag(5) From(None) Body(2015-11-04 21:19:53)
  Received(5) MessageTag(6) From(None) Body(2015-11-04 21:19:54)
  Received(6) MessageTag(7) From(None) Body(2015-11-04 21:19:55)
  Received(7) MessageTag(8) From(None) Body(2015-11-04 21:19:56)
  Received(8) MessageTag(9) From(None) Body(2015-11-04 21:19:57)
  Received(9) MessageTag(10) From(None) Body(2015-11-04 21:20:06)
  Done RabbitConsumer(/opt/message-simulator/simulations/rabbit/spring-xd/xd_3_b_run_sink_message_consumer.json)

  $
  ```

1. The consumer will stop consuming after it reads 10 messages, so please make sure to destroy the RabbitSinkStreamTest Sink Stream that is actively publishing messages at one a second from the xd-shell:

  ```
  xd:>stream destroy --name RabbitSinkStream
  Destroyed stream 'RabbitSinkStream'
  xd:>

  ```

1. Confirm the xd-singlenode terminal logs that it destroyed the sink

  ```
  2015-11-04T21:20:09-0500 1.2.1.RELEASE INFO main-EventThread container.DeploymentListener - Undeploying module [ModuleDescriptor@12967e2 moduleName = 'time', moduleLabel = 'time', group = 'RabbitSinkStream', sourceChannelName = [null], sinkChannelName = [null], index = 0, type = source, parameters = map[[empty]], children = list[[empty]]]
  2015-11-04T21:20:09-0500 1.2.1.RELEASE INFO main-EventThread container.DeploymentListener - Undeploying module [ModuleDescriptor@d9640b4 moduleName = 'rabbit', moduleLabel = 'rabbit', group = 'RabbitSinkStream', sourceChannelName = [null], sinkChannelName = [null], index = 1, type = sink, parameters = map['exchange' -> 'SpringXD.Sink.Ex', 'routingKey' -> '"Rabbit.MQTT.Test3.Rabbit1"'], children = list[[empty]]]
  2015-11-04T21:20:10-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Path cache event: path=/deployments/modules/allocated/d6be5ac1-e4ef-4a34-8e66-a072ad9fb146/RabbitSinkStream.source.time.1, type=CHILD_REMOVED
  2015-11-04T21:20:10-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Path cache event: path=/deployments/modules/allocated/d6be5ac1-e4ef-4a34-8e66-a072ad9fb146/RabbitSinkStream.sink.rabbit.1, type=CHILD_REMOVED
  ```


### Setting up MQTT on RabbitMQ

For more information on setting up RabbitMQ for MQTT: http://www.rabbitmq.com/mqtt.html

Login to one of the Docker Cluster Brokers with [ssh_node_1.sh](https://github.com/GetLevvel/testing-rabbitmq-clustering-with-docker/blob/master/ssh_node_1.sh) then confirm that the RabbitMQ MQTT plugin named **rabbitmq_mqtt** has an E* beside it.

```
$ ./ssh_node_1.sh 
SSHing into cluster_rabbit1_1
[root@rabbit1 /]# rabbitmq-plugins list
 Configured: E = explicitly enabled; e = implicitly enabled
 | Status:   * = running on rabbit@rabbit1
 |/
[e*] amqp_client                       3.5.6
[  ] cowboy                            0.5.0-rmq3.5.6-git4b93c2d
[e*] mochiweb                          2.7.0-rmq3.5.6-git680dba8
[  ] rabbitmq_amqp1_0                  3.5.6
[  ] rabbitmq_auth_backend_ldap        3.5.6
[  ] rabbitmq_auth_mechanism_ssl       3.5.6
[  ] rabbitmq_consistent_hash_exchange 3.5.6
[E*] rabbitmq_federation               3.5.6
[E*] rabbitmq_federation_management    3.5.6
[E*] rabbitmq_management               3.5.6
[E*] rabbitmq_management_agent         3.5.6
[E*] rabbitmq_management_visualiser    3.5.6
[E*] rabbitmq_mqtt                     3.5.6
[  ] rabbitmq_shovel                   3.5.6
[  ] rabbitmq_shovel_management        3.5.6
[E*] rabbitmq_stomp                    3.5.6
[  ] rabbitmq_test                     3.5.6
[  ] rabbitmq_tracing                  3.5.6
[e*] rabbitmq_web_dispatch             3.5.6
[  ] rabbitmq_web_stomp                3.5.6
[  ] rabbitmq_web_stomp_examples       3.5.6
[E*] sockjs                            0.3.4-rmq3.5.6-git3132eb9
[e*] webmachine                        1.10.3-rmq3.5.6-gite9359c7
[root@rabbit1 /]# 
[root@rabbit1 /]# exit
$
```

#### Using a Spring XD MQTT Source with the Docker RabbitMQ Cluster

##### Please Note: MQTT uses the RabbitMQ Port 1883 and SSL 8883. 

1. Run this in the xd-shell to create the MQTT Source with the Docker Rabbit Cluster hosting the MQTT server on port 1883

  ```
  xd:>stream create RabbitMQTTSource --definition "mqtt --url='tcp://rabbit1:1883' --topics='xd.mqtt.test' | log" --deploy
  Created and deployed new stream 'RabbitMQTTSource'
  xd:>
  ```

1. In the xd-single terminal should log something similar to:

  ```
  2015-11-05T00:06:04-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Path cache event: path=/deployments/modules/allocated/d6be5ac1-e4ef-4a34-8e66-a072ad9fb146/RabbitMQTTSource.sink.log.1, type=CHILD_ADDED
  2015-11-05T00:06:04-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Deploying module 'log' for stream 'RabbitMQTTSource'
  2015-11-05T00:06:04-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Deploying module [ModuleDescriptor@354e8586 moduleName = 'log', moduleLabel = 'log', group = 'RabbitMQTTSource', sourceChannelName = [null], sinkChannelName = [null], index = 1, type = sink, parameters = map[[empty]], children = list[[empty]]]
  2015-11-05T00:06:04-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Path cache event: path=/deployments/modules/allocated/d6be5ac1-e4ef-4a34-8e66-a072ad9fb146/RabbitMQTTSource.source.mqtt.1, type=CHILD_ADDED
  2015-11-05T00:06:04-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Deploying module 'mqtt' for stream 'RabbitMQTTSource'
  2015-11-05T00:06:04-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Deploying module [ModuleDescriptor@58e0c329 moduleName = 'mqtt', moduleLabel = 'mqtt', group = 'RabbitMQTTSource', sourceChannelName = [null], sinkChannelName = [null], index = 0, type = source, parameters = map['topics' -> 'xd.mqtt.test', 'url' -> 'tcp://rabbit1:1883'], children = list[[empty]]]
  2015-11-05T00:06:04-0500 1.2.1.RELEASE INFO DeploymentSupervisor-0 zk.ZKStreamDeploymentHandler - Deployment status for stream 'RabbitMQTTSource': DeploymentStatus{state=deployed}
  ```

1. Confirm the MQTT Queue and Binding were created in the RabbitMQ Cluster

  ```
  message-simulator/monitoring $ ./queues.sh 

  Displaying Cluster Queues

  +---------------------------------------------+----------------+---------+-------------+----------+-----------+--------+---------+------------------------+--------+-----------+
  |                    name                     |      node      | durable | auto_delete | messages | consumers | memory |  state  | exclusive_consumer_tag | policy | arguments |
  +---------------------------------------------+----------------+---------+-------------+----------+-----------+--------+---------+------------------------+--------+-----------+
  | mqtt-subscription-xd.mqtt.client.id.srcqos0 | rabbit@rabbit1 | False   | True        | 0        | 1         | 9192   | running |                        |        |           |
  +---------------------------------------------+----------------+---------+-------------+----------+-----------+--------+---------+------------------------+--------+-----------+

  message-simulator/monitoring $ ./bindings.sh 

  Displaying Cluster Bindings

  +-----------+---------------------------------------------+---------------------------------------------+
  |  source   |                 destination                 |                 routing_key                 |
  +-----------+---------------------------------------------+---------------------------------------------+
  |           | mqtt-subscription-xd.mqtt.client.id.srcqos0 | mqtt-subscription-xd.mqtt.client.id.srcqos0 |
  | amq.topic | mqtt-subscription-xd.mqtt.client.id.srcqos0 | xd.mqtt.test                                |
  +-----------+---------------------------------------------+---------------------------------------------+

  message-simulator/monitoring $
  ``` 


1. Setup a Producer to Stream Incoming HTTP Posts in to MQTT Messages and sent to our RabbitMQ Cluster

  From the xd-shell:

  ```
  xd:>stream create --name RabbitMQTTHttpProducer --definition "http|rabbit --exchange='amq.topic' --routingKey='''xd.mqtt.test'''" --deploy
  Created and deployed new stream 'RabbitMQTTHttpProducer'
  xd:>
  xd:>stream list
    Stream Name             Stream Definition                                                   Status
    ----------------------  ------------------------------------------------------------------  --------
    RabbitMQTTHttpProducer  http|rabbit --exchange='amq.topic' --routingKey='''xd.mqtt.test'''  deployed
    RabbitMQTTSource        mqtt --url='tcp://rabbit1:1883' --topics='xd.mqtt.test' | log       deployed
  xd:>
  ```

1. Send a 'Hello World' message to the HTTP Producer Stream Input

  From the xd-shell

  ```
  xd:>http post --data 'hello world'
  > POST (text/plain;Charset=UTF-8) http://localhost:9000 hello world
  > 200 OK

  xd:>
  ```

  From the xd-singlenode terminal confirm there is a log for this HTTP Post with contents that are similar 
  ```
  2015-11-05T00:19:51-0500 1.2.1.RELEASE INFO MQTT Call: xd.mqtt.client.id.src sink.RabbitMQTTSource - hello world
  ```

1. Monitoring Different Topics with MQTT and Sources listening on different HTTP Ports

  From the xd-shell run:

  ```
  xd:>stream create --name patientAlert --definition "http|rabbit --exchange='amq.topic' --routingKey='''patient.alert'''" --deploy
  Created and deployed new stream 'patientAlert'
  xd:>
  xd:>stream list
    Stream Name   Stream Definition                                                    Status
    ------------  -------------------------------------------------------------------  --------
    patientAlert  http|rabbit --exchange='amq.topic' --routingKey='''patient.alert'''  deployed

  xd:>stream create --name patientNotification --definition "http --port=9005|rabbit --exchange='amq.topic' --routingKey='''patient.notification'''" --deploy
  Created and deployed new stream 'patientNotification'
  xd:>
  xd:>stream list
    Stream Name          Stream Definition                                                                       Status
    -------------------  --------------------------------------------------------------------------------------  --------
    patientAlert         http|rabbit --exchange='amq.topic' --routingKey='''patient.alert'''                     deployed
    patientNotification  http --port=9005|rabbit --exchange='amq.topic' --routingKey='''patient.notification'''  deployed

  xd:>stream create --name patientMonitor --definition "mqtt --topics=patient.alert,patient.notification |log" --deploy
  Created and deployed new stream 'patientMonitor'
  xd:>
  xd:>stream list
    Stream Name          Stream Definition                                                                       Status
    -------------------  --------------------------------------------------------------------------------------  --------
    patientAlert         http|rabbit --exchange='amq.topic' --routingKey='''patient.alert'''                     deployed
    patientMonitor       mqtt --topics=patient.alert,patient.notification |log                                   deployed
    patientNotification  http --port=9005|rabbit --exchange='amq.topic' --routingKey='''patient.notification'''  deployed

  xd:>
  ```

1. At this point we have two HTTP Sources listening 
  1. ```patientAlert``` listens on the default port 9000
  1. ```patientNotification```  listens on the port 9005 

1. If we post data to the 9005 and to the 9000 Sources we will see it aggregated by the ```patientMonitor``` RabbitMQ Sink

  From the xd-shell run:

  ```
  xd:>http post --target http://localhost:9005  --data 'infusion complete'
  > POST (text/plain;Charset=UTF-8) http://localhost:9005 infusion complete
  > 200 OK

  xd:>http post --data 'pump failure'
  > POST (text/plain;Charset=UTF-8) http://localhost:9000 pump failure
  > 200 OK

  xd:>
  ```
  
  In the xd-singlenode terminal confirm the logs show the payloads consumed by the ```patientMonitor``` Source and written to the Log Sink

  ```
  2015-11-05T00:42:43-0500 1.2.1.RELEASE INFO MQTT Call: xd.mqtt.client.id.src sink.patientMonitor - infusion complete
  2015-11-05T00:42:53-0500 1.2.1.RELEASE INFO MQTT Call: xd.mqtt.client.id.src sink.patientMonitor - pump failure
  ```

1. Inspect the Cluster's Queues and Bindings

  ```
  message-simulator$ ./monitoring/queues.sh 

  Displaying Cluster Queues

  +---------------------------------------------+----------------+---------+-------------+----------+-----------+--------+---------+------------------------+--------+-----------+
  |                    name                     |      node      | durable | auto_delete | messages | consumers | memory |  state  | exclusive_consumer_tag | policy | arguments |
  +---------------------------------------------+----------------+---------+-------------+----------+-----------+--------+---------+------------------------+--------+-----------+
  | mqtt-subscription-xd.mqtt.client.id.srcqos0 | rabbit@rabbit1 | False   | True        | 0        | 1         | 9552   | running |                        |        |           |
  +---------------------------------------------+----------------+---------+-------------+----------+-----------+--------+---------+------------------------+--------+-----------+

  message-simulator$ ./monitoring/bindings.sh 

  Displaying Cluster Bindings

  +-----------+---------------------------------------------+---------------------------------------------+
  |  source   |                 destination                 |                 routing_key                 |
  +-----------+---------------------------------------------+---------------------------------------------+
  |           | mqtt-subscription-xd.mqtt.client.id.srcqos0 | mqtt-subscription-xd.mqtt.client.id.srcqos0 |
  | amq.topic | mqtt-subscription-xd.mqtt.client.id.srcqos0 | patient.alert                               |
  | amq.topic | mqtt-subscription-xd.mqtt.client.id.srcqos0 | patient.notification                        |
  +-----------+---------------------------------------------+---------------------------------------------+
  
  message-simulator$ 
  ```

  
1. Delete all the Streams (TAB Autocompletion makes this easier)

  From the xd-shell run:

  ```
  xd:> stream destroy --name patientAlert
  Destroyed stream 'patientAlert'
  xd:> stream destroy --name patientNotification
  Destroyed stream 'patientNotification'
  xd:> stream destroy --name patientMonitor
  Destroyed stream 'patientMonitor'
  xd:> stream list
    Stream Name  Stream Definition  Status
    -----------  -----------------  ----------

  xd:>
  ```

1. MQTT Simple Source and Sink Demo

  From the xd-shell run:

  ```
  xd:>stream create mqtt-out --definition "http|mqtt" --deploy
  Created and deployed new stream 'mqtt-out'
  xd:>stream create mqtt-in --definition "mqtt|log" --deploy
  Created and deployed new stream 'mqtt-in'
  xd:>http post --data "hello world"
  > POST (text/plain;Charset=UTF-8) http://localhost:9000 hello world
  > 200 OK

  xd:>
  ```
  
  Confirm the xd-single terminal logs show something similar:

  ```
  2015-11-05T00:54:49-0500 1.2.1.RELEASE INFO MQTT Call: xd.mqtt.client.id.src sink.mqtt-in - hello world
  ```

1. Delete all the Streams (TAB Autocompletion makes this easier)

  From the xd-shell run:

  ```
  xd:>stream destroy --name mqtt-in 
  Destroyed stream 'mqtt-in'
  xd:>stream destroy --name mqtt-out
  Destroyed stream 'mqtt-out'
  xd:>stream list
    Stream Name  Stream Definition  Status
    -----------  -----------------  ------

  xd:>
  ```

### Setting up the RabbitMQ Cluster as the Transport Message Bus for Spring XD

1. Edit the servers.yml

  ```spring-xd-1.2.1.RELEASE/xd/config$ vi servers.yml ``` 

1. Uncomment all the xd transports for the xd: **transport: rabbit** section as in below:

  ```
  xd:
    transport: rabbit

    messagebus:
      local:
        queueSize:                   2147483647
        polling:                     1000
        executor:
          corePoolSize:              0
          maxPoolSize:               200
          queueSize:                 2147483647
          keepAliveSeconds:          60
      rabbit:
        compressionLevel:            1
              # bus-level property, applies only when 'compress=true' for a stream module
              # See java.util.zip.Deflater; 1=BEST_SPEED, 9=BEST_COMPRESSION, ...
        default:
          ackMode:                   AUTO
              # Valid: AUTO (container acks), NONE (broker acks), MANUAL (consumer acks).
              # Upper case only.
              # Note: MANUAL requires specialized code in the consuming module and is unlikely to be
              # used in an XD application. For more information, see
              # http://docs.spring.io/spring-integration/reference/html/amqp.html#amqp-inbound-ack
          autoBindDLQ:               false
          backOffInitialInterval:    1000
          backOffMaxInterval:        10000
          backOffMultiplier:         2.0
          batchBufferLimit:          10000
          batchingEnabled:           false
          batchSize:                 100
          batchTimeout:              5000
          compress:                  false
          concurrency:               1
          deliveryMode:              PERSISTENT
          durableSubscription:       false
          maxAttempts:               3
          maxConcurrency:            1
          prefix:                    xdbus.
              # prefix for queue/exchange names so policies (ha, dle etc.) can be applied
          prefetch:                  1
          replyHeaderPatterns:       STANDARD_REPLY_HEADERS,*
          republishToDLQ:            false
              # When false, normal rabbitmq dlq processing; when true, republish to the DLQ with stack trace
          requestHeaderPatterns:     STANDARD_REQUEST_HEADERS,*
          requeue:                   true
          transacted:                false
          txSize:                    1
  ```

  Also add the rabbit transport in the file:

  ```
  #Config for singlenode.
  #Transport for single node may be overridden by --transport command line option
  #If the singlenode needs to use external datasource for batch embeddedHsql can be set to false
  spring:
    profiles: singlenode
  xd:
    transport: rabbit
  ```

1. Restart the xd-singlenode instance

1. Use the Message Simulator to create the Queues for testing the Message Bus with **"test 5"**

  ```
  $ /opt/message-simulator/run_message_simulation.py -f /opt/message-simulator/simulations/rabbit/spring-xd/xd_5_rabbitmq_transport.json 
  ```

1. Inspect the Queues on the Cluster

  ```
  message-simulator/monitoring$ ./queues.sh 

  Displaying Cluster Queues

  +------------------------+----------------+---------+-------------+----------+-----------+--------+---------+------------------------+--------+-----------+
  |          name          |      node      | durable | auto_delete | messages | consumers | memory |  state  | exclusive_consumer_tag | policy | arguments |
  +------------------------+----------------+---------+-------------+----------+-----------+--------+---------+------------------------+--------+-----------+
  | RabbitSourceToFileSink | rabbit@rabbit1 | False   | False       | 0        | 0         | 9048   | running |                        |        |           |
  | SpringXD.Test5.Queue.A | rabbit@rabbit1 | False   | False       | 0        | 0         | 9048   | running |                        |        |           |
  +------------------------+----------------+---------+-------------+----------+-----------+--------+---------+------------------------+--------+-----------+

  message-simulator/monitoring$
  ```

1. Now create the XD RabbitMQ Source Stream

  From the xd-shell run:

  ```
  xd:>stream create --name RabbitSourceToFileSink --definition "rabbit | file --binary=true" --deploy
  Created and deployed new stream 'RabbitSourceToFileSink'
  xd:>
  ```

1. Confirm there is now a message transport queue in the Cluster and a Consumer subscribed to them

  **Notice the transport queue is marked as durable by Spring XD**

  ```
  message-simulator/monitoring$ ./queues.sh 

  Displaying Cluster Queues

  +--------------------------------+----------------+---------+-------------+----------+-----------+--------+---------+------------------------+--------+-----------+
  |              name              |      node      | durable | auto_delete | messages | consumers | memory |  state  | exclusive_consumer_tag | policy | arguments |
  +--------------------------------+----------------+---------+-------------+----------+-----------+--------+---------+------------------------+--------+-----------+
  | RabbitSourceToFileSink         | rabbit@rabbit1 | False   | False       | 0        | 1         | 9192   | running |                        |        |           |
  | SpringXD.Test5.Queue.A         | rabbit@rabbit1 | False   | False       | 0        | 0         | 9048   | running |                        |        |           |
  | xdbus.RabbitSourceToFileSink.0 | rabbit@rabbit1 | True    | False       | 0        | 1         | 14152  | running |                        |        |           |
  +--------------------------------+----------------+---------+-------------+----------+-----------+--------+---------+------------------------+--------+-----------+

  message-simulator/monitoring$
  ```

1. Open a new terminal and tail the new Sink File on disk:

  ```
  $ tail -f /tmp/xd/output/RabbitSourceToFileSink.out 
  {"Data": "Test 6 - Validated Test 5 - The RabbitMQ Transport is working"}{"Data": "Test 6 - Validated Test 5 - The RabbitMQ Transport is working"}{"Data": "Test 6 - Validated Test 5 - The RabbitMQ Transport is working"}{"Data": "Test 6 - Validated Test 5 - The RabbitMQ Transport is working"}{"Data": "Test 6 - Validated Test 5 - The RabbitMQ Transport is working"}


  ```

1. Now Run Simulation **xd_6_send_messages_through_transport.json** that will send 5 messages through the Exchange bound to the Queue monitored by the Sink Stream File handler

  ```
  $ /opt/message-simulator/run_message_simulation.py -f /opt/message-simulator/simulations/rabbit/spring-xd/xd_6_send_messages_through_transport.json 
  ```

1. Confirm the Sink File logged something similar to:

  ```
  {"Data": "Test 6 - Validated Test 5 - The RabbitMQ Transport is working"}{"Data": "Test 6 - Validated Test 5 - The RabbitMQ Transport is working"}{"Data": "Test 6 - Validated Test 5 - The RabbitMQ Transport is working"}{"Data": "Test 6 - Validated Test 5 - The RabbitMQ Transport is working"}{"Data": "Test 6 - Validated Test 5 - The RabbitMQ Transport is working"}
  ```

1. Confirm the Queues show data passed through them in the Cluster:

  ```
  message-simulator/monitoring$ ./queues.sh 

  Displaying Cluster Queues

  +--------------------------------+----------------+---------+-------------+----------+-----------+--------+---------+------------------------+--------+-----------+
  |              name              |      node      | durable | auto_delete | messages | consumers | memory |  state  | exclusive_consumer_tag | policy | arguments |
  +--------------------------------+----------------+---------+-------------+----------+-----------+--------+---------+------------------------+--------+-----------+
  | RabbitSourceToFileSink         | rabbit@rabbit1 | False   | False       | 0        | 1         | 14152  | running |                        |        |           |
  | SpringXD.Test5.Queue.A         | rabbit@rabbit1 | False   | False       | 0        | 0         | 9048   | running |                        |        |           |
  | xdbus.RabbitSourceToFileSink.0 | rabbit@rabbit1 | True    | False       | 0        | 1         | 22392  | running |                        |        |           |
  +--------------------------------+----------------+---------+-------------+----------+-----------+--------+---------+------------------------+--------+-----------+

  message-simulator/monitoring$
  ```

1. Delete the Source from the xd-shell

  ```
  xd:>stream destroy --name RabbitSourceToFileSink 
  Destroyed stream 'RabbitSourceToFileSink'
  xd:>
  ```

1. Confirm the Transport Queue and RabbitSourceToFileSink no longer have a Consumer

  ```
  message-simulator/monitoring$ ./queues.sh 

  Displaying Cluster Queues

  +--------------------------------+----------------+---------+-------------+----------+-----------+--------+---------+------------------------+--------+-----------+
  |              name              |      node      | durable | auto_delete | messages | consumers | memory |  state  | exclusive_consumer_tag | policy | arguments |
  +--------------------------------+----------------+---------+-------------+----------+-----------+--------+---------+------------------------+--------+-----------+
  | RabbitSourceToFileSink         | rabbit@rabbit1 | False   | False       | 0        | 0         | 9048   | running |                        |        |           |
  | SpringXD.Test5.Queue.A         | rabbit@rabbit1 | False   | False       | 0        | 0         | 9048   | running |                        |        |           |
  | xdbus.RabbitSourceToFileSink.0 | rabbit@rabbit1 | True    | False       | 0        | 0         | 14272  | running |                        |        |           |
  +--------------------------------+----------------+---------+-------------+----------+-----------+--------+---------+------------------------+--------+-----------+

  message-simulator/monitoring$
  ```


## Running Spring XD in a Distributed Environment

1. Install Zookeeper by running the installer in the Spring XD dir

  While the install runs, take a look at what Zookeeper offers:

    - Sequential Consistency - Updates from a client will be applied in the order that they were sent.
    - Atomicity - Updates either succeed or fail. No partial results.
    - Single System Image - A client will see the same view of the service regardless of the server that it connects to.
    - Reliability - Once an update has been applied, it will persist from that time forward until a client overwrites the update.
    - Timeliness - The clients view of the system is guaranteed to be up-to-date within a certain time bound.

  ZooKeeper maintains data primarily in memory backed by a disk cache. Updates are logged to disk for recoverability, and writes are serialized to disk before they are applied to the in-memory database.

  Start the Installer:

  ```
  $ cd spring-xd-1.2.1.RELEASE/zookeeper/bin/
  $ ./install-zookeeper
  ```

1. To log to the standard Zookeeper Log file: ```/var/log/zookeeper/zookeeper.out``` edit the ```spring-xd-1.2.1.RELEASE/zookeeper/bin/zkServer.sh``` and add:

  ```
  ZOO_LOG_DIR="/var/log/zookeeper"
  ```

1. Please check that the directory /var/log/zookeeper exists and is writeable by zookeeper

  ```
  $ ls -lrt /var/log/ | grep zookeeper
  drwxr-xr-x  2 zookeeper zookeeper            4096 Jan 15  2015 zookeeper
  $ 
  ```

1. Start the Zookeeper server:

  ```
  spring-xd-1.2.1.RELEASE/zookeeper/bin$ ./zkServer.sh start
  ```

1. Confirm that Zookeeper is running an listening on Port 2181:

  ```
  $ sudo netstat -apn | grep 2181 | grep tcp
  tcp6       0      0 :::2181                 :::*                    LISTEN      32375/java     
  $
  ```
  
  ```
  $ ps auwwx | grep zookeeper | grep -v grep
  root     32375  1.9  1.0 3529024 40640 pts/4   Sl   12:03   0:00 java -Dzookeeper.log.dir=/var/log/zookeeper -Dzookeeper.root.logger=INFO,CONSOLE -cp /opt/zookeeper-3.4.6/bin/../build/classes:/opt/zookeeper-3.4.6/bin/../build/lib/*.jar:/opt/zookeeper-3.4.6/bin/../lib/slf4j-log4j12-1.6.1.jar:/opt/zookeeper-3.4.6/bin/../lib/slf4j-api-1.6.1.jar:/opt/zookeeper-3.4.6/bin/../lib/netty-3.7.0.Final.jar:/opt/zookeeper-3.4.6/bin/../lib/log4j-1.2.16.jar:/opt/zookeeper-3.4.6/bin/../lib/jline-0.9.94.jar:/opt/zookeeper-3.4.6/bin/../zookeeper-3.4.6.jar:/opt/zookeeper-3.4.6/bin/../src/java/lib/*.jar:/opt/zookeeper-3.4.6/bin/../conf: -Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.local.only=false org.apache.zookeeper.server.quorum.QuorumPeerMain /opt/zookeeper-3.4.6/bin/../conf/zoo.cfg
  $
  ```

1. Open a log tail terminal running: ```tail -f /var/log/zookeeper/zookeeper.out```

1. Enable the Local Zookeeper in the ```spring-xd-1.2.1.RELEASE/xd/config/servers.yml```

  ```
  # Zookeeper properties
  # namespace is the path under the root where XD's top level nodes will be created
  # client connect string: host1:port1,host2:port2,...,hostN:portN
  zk:
    namespace: xd
    client:
       connect: localhost:2181
       sessionTimeout: 60000
       connectionTimeout: 30000
       initialRetryWait: 1000
       retryMaxAttempts: 3
  ```

1. Optional - Install Redis with the Installer Script

  ```spring-xd-1.2.1.RELEASE/redis/bin$ ./install-redis```

1. Optional - Start Redis

  ```cd spring-xd-1.2.1.RELEASE/redis/bin; nohup ./redis-server &```

1. Start the xd-singlenode 

  ```spring-xd-1.2.1.RELEASE/xd/bin$ ./xd-singlenode```

1. Confirm Zookeeper logs the attempt to use it:

  ```
  2015-11-05 12:53:10,976 [myid:] - INFO  [NIOServerCxn.Factory:0.0.0.0/0.0.0.0:2181:NIOServerCnxnFactory@197] - Accepted socket connection from /127.0.0.1:46188
  2015-11-05 12:53:10,980 [myid:] - INFO  [NIOServerCxn.Factory:0.0.0.0/0.0.0.0:2181:ZooKeeperServer@868] - Client attempting to establish new session at /127.0.0.1:46188
  2015-11-05 12:53:10,982 [myid:] - INFO  [SyncThread:0:ZooKeeperServer@617] - Established session 0x150d8a037f50002 with negotiated timeout 40000 for client /127.0.0.1:46188
  ```

#### Adding a Container to a Running Spring XD Environment

1. Check how many containers are available with the xd-shell

  ```
  xd:>runtime containers
    Container Id                          Host                   IP Address   PID    Groups  Custom Attributes
    ------------------------------------  ---------------------  -----------  -----  ------  -----------------
    ad4c761f-046e-4237-976f-5acdf2d9a0c4  localhost.localdomain  172.17.42.1  15557

  xd:>
  ```

1. From a new terminal create the container:

  ```
  spring-xd-1.2.1.RELEASE/xd/bin$ ./xd-container

   _____                           __   _______
  /  ___|          (-)             \ \ / /  _  \
  \ `--. _ __  _ __ _ _ __   __ _   \ V /| | | |
   `--. \ '_ \| '__| | '_ \ / _` |  / ^ \| | | |
  /\__/ / |_) | |  | | | | | (_| | / / \ \ |/ /
  \____/| .__/|_|  |_|_| |_|\__, | \/   \/___/
        | |                  __/ |
        |_|                 |___/
  1.2.1.RELEASE                    eXtreme Data


  Started : ContainerServerApplication
  Documentation: https://github.com/spring-projects/spring-xd/wiki
   
  ```

1. In a new terminal start a Zookeeper Command Line Client (cli) to connect to the running ZK instance:

  ```
  spring-xd-1.2.1.RELEASE/zookeeper/bin$ ./zkCli.sh -server localhost:2181

  ... ignoring the logs:

  WATCHER::

  WatchedEvent state:SyncConnected type:None path:null
  [zk: localhost:2181(CONNECTED) 0] ls /
  [zookeeper, xd]

  ```

1. Confirm the container registers with Zookeeper cli

  ```
  [zk: localhost:2181(CONNECTED) 1] ls /xd/containers
  [ad4c761f-046e-4237-976f-5acdf2d9a0c4, 9ecd6c98-2ba7-4369-b013-ef209722f8fd]
  [zk: localhost:2181(CONNECTED) 2] 
  ```

1. Confirm the container registered with the xd-shell

  ```
  xd:>runtime containers
  Container Id                          Host                   IP Address   PID    Groups  Custom Attributes
  ------------------------------------  ---------------------  -----------  -----  ------  -----------------
  9ecd6c98-2ba7-4369-b013-ef209722f8fd  localhost.localdomain  172.17.42.1  17515
  ad4c761f-046e-4237-976f-5acdf2d9a0c4  localhost.localdomain  172.17.42.1  15557

  xd:>
  ```

### Automatic Redeployment

Refer to reployment of a running Stream from the guide:

http://docs.spring.io/spring-xd/docs/current/reference/html/#_example_automatic_redeployment

1. Check the running containers in the xd-shell

  ```
  xd:>runtime containers
  Container Id                          Host                   IP Address   PID    Groups  Custom Attributes
  ------------------------------------  ---------------------  -----------  -----  ------  -----------------
  9ecd6c98-2ba7-4369-b013-ef209722f8fd  localhost.localdomain  172.17.42.1  17515
  ad4c761f-046e-4237-976f-5acdf2d9a0c4  localhost.localdomain  172.17.42.1  15557

  xd:>
  ```

1. Create the ticktock Stream in the xd-shell:

  ```
  xd:>stream create ticktock --definition "time | log"
  Created new stream 'ticktock'
  xd:>stream deploy ticktock
  Deployed stream 'ticktock'
  xd:>
  ```

1. Check the running modules in the xd-shell:

  **Notice that the Sink and the Source Streams were deployed to different Containers**

  ```
  xd:>runtime modules
    Module Id               Container Id                          Options                                                                                      Deployment Properties                                         Unit status
    ----------------------  ------------------------------------  -------------------------------------------------------------------------------------------  ------------------------------------------------------------  -----------
    ticktock.sink.log.1     ad4c761f-046e-4237-976f-5acdf2d9a0c4  {name=ticktock, expression=payload, level=INFO}                                              {consumer.sequence=1, count=1, consumer.count=1, sequence=1}  deployed
    ticktock.source.time.1  9ecd6c98-2ba7-4369-b013-ef209722f8fd  {maxMessages=1, initialDelay=0, fixedDelay=1, format=yyyy-MM-dd HH:mm:ss, timeUnit=SECONDS}  {producer.next.module.count=1, count=1, sequence=1}           deployed

  xd:>
  ```

1. Use CTRL+C in the Container's terminal to simulate a container crash event

  Here are the logs during a CTRL+C:

  ```
  2015-11-05T14:45:07-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Path cache event: path=/deployments/modules/allocated/9ecd6c98-2ba7-4369-b013-ef209722f8fd/ticktock.source.time.1, type=CHILD_ADDED
  2015-11-05T14:45:07-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Deploying module 'time' for stream 'ticktock'
  2015-11-05T14:45:07-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Deploying module [ModuleDescriptor@453a522 moduleName = 'time', moduleLabel = 'time', group = 'ticktock', sourceChannelName = [null], sinkChannelName = [null], index = 0, type = source, parameters = map[[empty]], children = list[[empty]]]
  ^C2015-11-05T14:46:23-0500 1.2.1.RELEASE INFO main-EventThread container.DeploymentListener - Undeploying module [ModuleDescriptor@453a522 moduleName = 'time', moduleLabel = 'time', group = 'ticktock', sourceChannelName = [null], sinkChannelName = [null], index = 0, type = source, parameters = map[[empty]], children = list[[empty]]]
  ```

1. From the xd-singlenode terminal confirm it logged that the container was lost while 'ticktock' was running

  ```
  2015-11-05T14:46:19-0500 1.2.1.RELEASE INFO xdbus.ticktock.0-1 sink.ticktock - 2015-11-05 14:46:19
  2015-11-05T14:46:20-0500 1.2.1.RELEASE INFO xdbus.ticktock.0-1 sink.ticktock - 2015-11-05 14:46:20
  2015-11-05T14:46:21-0500 1.2.1.RELEASE INFO xdbus.ticktock.0-1 sink.ticktock - 2015-11-05 14:46:21
  2015-11-05T14:46:22-0500 1.2.1.RELEASE INFO xdbus.ticktock.0-1 sink.ticktock - 2015-11-05 14:46:22
  2015-11-05T14:46:23-0500 1.2.1.RELEASE INFO xdbus.ticktock.0-1 sink.ticktock - 2015-11-05 14:46:23
  2015-11-05T14:46:23-0500 1.2.1.RELEASE INFO DeploymentSupervisor-0 zk.ContainerListener - Path cache event: path=/containers/9ecd6c98-2ba7-4369-b013-ef209722f8fd, type=CHILD_REMOVED
  2015-11-05T14:46:23-0500 1.2.1.RELEASE INFO DeploymentSupervisor-0 zk.ContainerListener - Container departed: Container{name='9ecd6c98-2ba7-4369-b013-ef209722f8fd', attributes={ip=172.17.42.1, host=localhost.localdomain, groups=, pid=17515, id=9ecd6c98-2ba7-4369-b013-ef209722f8fd}}
  2015-11-05T14:46:23-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Path cache event: path=/deployments/modules/allocated/ad4c761f-046e-4237-976f-5acdf2d9a0c4/ticktock.source.time.1, type=CHILD_ADDED
  2015-11-05T14:46:23-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Deploying module 'time' for stream 'ticktock'
  2015-11-05T14:46:24-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Deploying module [ModuleDescriptor@7949dd6a moduleName = 'time', moduleLabel = 'time', group = 'ticktock', sourceChannelName = [null], sinkChannelName = [null], index = 0, type = source, parameters = map[[empty]], children = list[[empty]]]
  2015-11-05T14:46:24-0500 1.2.1.RELEASE INFO xdbus.ticktock.0-1 sink.ticktock - 2015-11-05 14:46:24
  2015-11-05T14:46:24-0500 1.2.1.RELEASE INFO DeploymentSupervisor-0 zk.ModuleRedeployer - Deployment state for stream 'ticktock': DeploymentStatus{state=deployed}
  2015-11-05T14:46:25-0500 1.2.1.RELEASE INFO xdbus.ticktock.0-1 sink.ticktock - 2015-11-05 14:46:25
  2015-11-05T14:46:26-0500 1.2.1.RELEASE INFO xdbus.ticktock.0-1 sink.ticktock - 2015-11-05 14:46:26
  2015-11-05T14:46:27-0500 1.2.1.RELEASE INFO xdbus.ticktock.0-1 sink.ticktock - 2015-11-05 14:46:27
  2015-11-05T14:46:28-0500 1.2.1.RELEASE INFO xdbus.ticktock.0-1 sink.ticktock - 2015-11-05 14:46:28
  2015-11-05T14:46:29-0500 1.2.1.RELEASE INFO xdbus.ticktock.0-1 sink.ticktock - 2015-11-05 14:46:29
  ```

1. Confirm Zookeeper no longer has the container

  ```
  [zk: localhost:2181(CONNECTED) 2] ls /xd/containers
  [ad4c761f-046e-4237-976f-5acdf2d9a0c4]
  [zk: localhost:2181(CONNECTED) 3] 
  ```

1. Confirm the xd-shell no longer has the container

  ```
  xd:>runtime containers
  Container Id                          Host                   IP Address   PID    Groups  Custom Attributes
  ------------------------------------  ---------------------  -----------  -----  ------  -----------------
  ad4c761f-046e-4237-976f-5acdf2d9a0c4  localhost.localdomain  172.17.42.1  15557

  xd:>
  ```

1. Confirm both Streams are deployed to the same container in the xd-shell

  ```
  xd:>runtime modules
    Module Id               Container Id                          Options                                                                                      Deployment Properties                                         Unit status
    ----------------------  ------------------------------------  -------------------------------------------------------------------------------------------  ------------------------------------------------------------  -----------
    ticktock.sink.log.1     ad4c761f-046e-4237-976f-5acdf2d9a0c4  {name=ticktock, expression=payload, level=INFO}                                              {consumer.sequence=1, count=1, consumer.count=1, sequence=1}  deployed
    ticktock.source.time.1  ad4c761f-046e-4237-976f-5acdf2d9a0c4  {maxMessages=1, initialDelay=0, fixedDelay=1, format=yyyy-MM-dd HH:mm:ss, timeUnit=SECONDS}  {producer.next.module.count=1, count=1, sequence=1}           deployed

  xd:>
  ```

1. CTRL+C the xd-singlenode instance to stop it from running

### Moving from the xd-singlenode to a Distributed Environment

1. Start the HSQLDB Server

  ```
  spring-xd-1.2.1.RELEASE/hsqldb/bin$ ./hsqldb-server
  [2015-11-05 14:14.375] INFO main o.s.x.b.h.s.HsqlServerApplication - Starting HsqlServerApplication v1.2.1.RELEASE on localhost.localdomain with PID 22386 (/opt/spring-xd-1.2.1.RELEASE/xd/lib/spring-xd-batch-1.2.1.RELEASE.jar started by user in /opt/spring-xd-1.2.1.RELEASE/hsqldb/bin)
  [2015-11-05 14:14.468] INFO main o.s.c.a.AnnotationConfigApplicationContext - Refreshing org.springframework.context.annotation.AnnotationConfigApplicationContext@35038141: startup date [Thu Nov 05 15:14:14 EST 2015]; root of context hierarchy
  ```

1. From a new terminal start the xd-admin (Admin) terminal

  ```
  spring-xd-1.2.1.RELEASE/xd/bin$ ./xd-admin

   _____                           __   _______
  /  ___|          (-)             \ \ / /  _  \
  \ `--. _ __  _ __ _ _ __   __ _   \ V /| | | |
   `--. \ '_ \| '__| | '_ \ / _` |  / ^ \| | | |
  /\__/ / |_) | |  | | | | | (_| | / / \ \ |/ /
  \____/| .__/|_|  |_|_| |_|\__, | \/   \/___/
        | |                  __/ |
        |_|                 |___/
  1.2.1.RELEASE                    eXtreme Data


  Started : AdminServerApplication
  Documentation: https://github.com/spring-projects/spring-xd/wiki

  2015-11-05T15:14:42-0500 1.2.1.RELEASE INFO main util.XdConfigLoggingInitializer - XD Home: /opt/spring-xd-1.2.1.RELEASE/xd
  2015-11-05T15:14:42-0500 1.2.1.RELEASE INFO main util.XdConfigLoggingInitializer - Transport: rabbit
  2015-11-05T15:14:42-0500 1.2.1.RELEASE INFO main util.XdConfigLoggingInitializer - Hadoop version detected from classpath 2.6.0
  2015-11-05T15:14:42-0500 1.2.1.RELEASE INFO main util.XdConfigLoggingInitializer - XD config location: file:/opt/spring-xd-1.2.1.RELEASE/xd/config//
  2015-11-05T15:14:42-0500 1.2.1.RELEASE INFO main util.XdConfigLoggingInitializer - XD config names: servers,application
  2015-11-05T15:14:42-0500 1.2.1.RELEASE INFO main util.XdConfigLoggingInitializer - XD module config location: file:/opt/spring-xd-1.2.1.RELEASE/xd/config//modules/
  2015-11-05T15:14:42-0500 1.2.1.RELEASE INFO main util.XdConfigLoggingInitializer - XD module config name: modules
  2015-11-05T15:14:42-0500 1.2.1.RELEASE INFO main util.XdConfigLoggingInitializer - Admin web UI: http://localhost.localdomain:9393/admin-ui
  2015-11-05T15:14:42-0500 1.2.1.RELEASE INFO main util.XdConfigLoggingInitializer - Zookeeper at: localhost:2181
  2015-11-05T15:14:42-0500 1.2.1.RELEASE INFO main util.XdConfigLoggingInitializer - Zookeeper namespace: xd
  2015-11-05T15:14:42-0500 1.2.1.RELEASE INFO main util.XdConfigLoggingInitializer - Analytics: redis
  2015-11-05T15:14:42-0500 1.2.1.RELEASE INFO LeaderSelector-0 zk.DeploymentSupervisor - Leader Admin 172.17.42.1:9393 is watching for stream/job deployment requests.
  2015-11-05T15:14:42-0500 1.2.1.RELEASE INFO main admin.AdminServerApplication - Started AdminServerApplication in 6.333 seconds (JVM running for 15.198)
  2015-11-05T15:14:42-0500 1.2.1.RELEASE INFO LeaderSelector-0 zk.DefaultDeploymentStateRecalculator - Deployment status for stream 'ticktock': DeploymentStatus{state=failed}
  2015-11-05T15:14:42-0500 1.2.1.RELEASE INFO DeploymentSupervisor-0 zk.ContainerListener - Path cache event: type=INITIALIZED

  ```

1. Start a new xd-shell (shell) session to connect to the running Admin instance

  ```
  spring-xd-1.2.1.RELEASE/xd/bin$ ./xd-shell
   _____                           __   _______
  /  ___|          (-)             \ \ / /  _  \
  \ `--. _ __  _ __ _ _ __   __ _   \ V /| | | |
   `--. \ '_ \| '__| | '_ \ / _` |  / ^ \| | | |
  /\__/ / |_) | |  | | | | | (_| | / / \ \ |/ /
  \____/| .__/|_|  |_|_| |_|\__, | \/   \/___/
        | |                  __/ |
        |_|                 |___/
  eXtreme Data
  1.2.1.RELEASE | Admin Server Target: http://localhost:9393
  Welcome to the Spring XD shell. For assistance hit TAB or type "help".
  xd:>
  ```

1. Inspect the containers from the xd-shell

  ```
  xd:>runtime containers
    Container Id  Host  IP Address  PID  Groups  Custom Attributes
    ------------  ----  ----------  ---  ------  -----------------

  xd:>
  ```

1. Add a container from a new terminal

  ```
  spring-xd-1.2.1.RELEASE/xd/bin$ ./xd-container

   _____                           __   _______
  /  ___|          (-)             \ \ / /  _  \
  \ `--. _ __  _ __ _ _ __   __ _   \ V /| | | |
   `--. \ '_ \| '__| | '_ \ / _` |  / ^ \| | | |
  /\__/ / |_) | |  | | | | | (_| | / / \ \ |/ /
  \____/| .__/|_|  |_|_| |_|\__, | \/   \/___/
        | |                  __/ |
        |_|                 |___/
  1.2.1.RELEASE                    eXtreme Data


  Started : ContainerServerApplication
  Documentation: https://github.com/spring-projects/spring-xd/wiki

  2015-11-05T15:25:04-0500 1.2.1.RELEASE INFO main container.ContainerServerApplication - Starting ContainerServerApplication v1.2.1.RELEASE on localhost.localdomain with PID 23353 (/opt/spring-xd-1.2.1.RELEASE/xd/lib/spring-xd-dirt-1.2.1.RELEASE.jar started by user in /opt/spring-xd-1.2.1.RELEASE/xd/bin)
  2015-11-05T15:25:05-0500 1.2.1.RELEASE INFO main container.ContainerServerApplication - Started ContainerServerApplication in 2.439 seconds (JVM running for 3.317)
  2015-11-05T15:25:17-0500 1.2.1.RELEASE INFO main util.XdConfigLoggingInitializer - XD Home: /opt/spring-xd-1.2.1.RELEASE/xd
  2015-11-05T15:25:17-0500 1.2.1.RELEASE INFO main util.XdConfigLoggingInitializer - Transport: rabbit
  2015-11-05T15:25:17-0500 1.2.1.RELEASE INFO main util.XdConfigLoggingInitializer - Hadoop version detected from classpath 2.6.0
  2015-11-05T15:25:17-0500 1.2.1.RELEASE INFO main util.XdConfigLoggingInitializer - XD config location: file:/opt/spring-xd-1.2.1.RELEASE/xd/config//
  2015-11-05T15:25:17-0500 1.2.1.RELEASE INFO main util.XdConfigLoggingInitializer - XD config names: servers,application
  2015-11-05T15:25:17-0500 1.2.1.RELEASE INFO main util.XdConfigLoggingInitializer - XD module config location: file:/opt/spring-xd-1.2.1.RELEASE/xd/config//modules/
  2015-11-05T15:25:17-0500 1.2.1.RELEASE INFO main util.XdConfigLoggingInitializer - XD module config name: modules
  2015-11-05T15:25:17-0500 1.2.1.RELEASE INFO main util.XdConfigLoggingInitializer - Container IP address: 172.17.42.1
  2015-11-05T15:25:17-0500 1.2.1.RELEASE INFO main util.XdConfigLoggingInitializer - Container hostname:   localhost.localdomain
  2015-11-05T15:25:17-0500 1.2.1.RELEASE INFO main util.XdConfigLoggingInitializer - Zookeeper at: localhost:2181
  2015-11-05T15:25:17-0500 1.2.1.RELEASE INFO main util.XdConfigLoggingInitializer - Zookeeper namespace: xd
  2015-11-05T15:25:17-0500 1.2.1.RELEASE INFO main util.XdConfigLoggingInitializer - Analytics: redis
  2015-11-05T15:25:17-0500 1.2.1.RELEASE INFO DeploymentsPathChildrenCache-0 container.DeploymentListener - Path cache event: type=INITIALIZED
  2015-11-05T15:25:17-0500 1.2.1.RELEASE INFO main container.ContainerRegistrar - Container {ip=172.17.42.1, host=localhost.localdomain, groups=, pid=23353, id=78f681d7-fe53-4265-b4bc-9b55e7f2631e} joined cluster

  ```

1. Wait for Spring XD to automatically restart showing the tick tock Stream logs

  ```
  2015-11-05T15:25:35-0500 1.2.1.RELEASE INFO xdbus.ticktock.0-1 sink.ticktock - 2015-11-05 15:25:34
  2015-11-05T15:25:36-0500 1.2.1.RELEASE INFO xdbus.ticktock.0-1 sink.ticktock - 2015-11-05 15:25:36
  2015-11-05T15:25:37-0500 1.2.1.RELEASE INFO xdbus.ticktock.0-1 sink.ticktock - 2015-11-05 15:25:37
  2015-11-05T15:25:38-0500 1.2.1.RELEASE INFO xdbus.ticktock.0-1 sink.ticktock - 2015-11-05 15:25:38
  2015-11-05T15:25:39-0500 1.2.1.RELEASE INFO xdbus.ticktock.0-1 sink.ticktock - 2015-11-05 15:25:39
  2015-11-05T15:25:40-0500 1.2.1.RELEASE INFO xdbus.ticktock.0-1 sink.ticktock - 2015-11-05 15:25:40
  2015-11-05T15:25:41-0500 1.2.1.RELEASE INFO xdbus.ticktock.0-1 sink.ticktock - 2015-11-05 15:25:41
  2015-11-05T15:25:42-0500 1.2.1.RELEASE INFO xdbus.ticktock.0-1 sink.ticktock - 2015-11-05 15:25:42

  ```

1. Confirm Zookeeper cli shows the new container

  ```
  [zk: localhost:2181(CONNECTED) 3] ls /xd/containers
  [78f681d7-fe53-4265-b4bc-9b55e7f2631e]
  [zk: localhost:2181(CONNECTED) 3] 
  ```

1. Confirm the xd-shell has the container too

  ```
  xd:>runtime containers
    Container Id                          Host                   IP Address   PID    Groups  Custom Attributes
    ------------------------------------  ---------------------  -----------  -----  ------  -----------------
    78f681d7-fe53-4265-b4bc-9b55e7f2631e  localhost.localdomain  172.17.42.1  23353

  xd:>
  ```

1. Confirm the xd-shell has the deployed Streams on the new container instance

  ```
  xd:>runtime modules 
    Module Id               Container Id                          Options                                                                                      Deployment Properties                                         Unit status
    ----------------------  ------------------------------------  -------------------------------------------------------------------------------------------  ------------------------------------------------------------  -----------
    ticktock.sink.log.1     78f681d7-fe53-4265-b4bc-9b55e7f2631e  {name=ticktock, expression=payload, level=INFO}                                              {consumer.sequence=1, count=1, consumer.count=1, sequence=1}  deployed
    ticktock.source.time.1  78f681d7-fe53-4265-b4bc-9b55e7f2631e  {maxMessages=1, initialDelay=0, fixedDelay=1, format=yyyy-MM-dd HH:mm:ss, timeUnit=SECONDS}  {producer.next.module.count=1, count=1, sequence=1}           deployed

  xd:>
  ```


## Troubleshooting

1. If the xd-shell fails to connect just wait for the xd-singlenode to boot up

  ```
  server-unknown:>admin config server http://localhost:9393
  Unable to contact XD Admin Server at 'http://localhost:9393'.
  server-unknown:>

  ... wait a few seconds and retry:

  server-unknown:>admin config server http://localhost:9393
  Successfully targeted http://localhost:9393
  xd:>
  ```

1. Make sure to confirm Streams deployed successfully with the ```stream list``` command

  The HTTP Source Streams require an argument: --port=1234 in order to change the port...however these Streams silently failed to deploy and the only way I could tell was watching the logs in the xd-singlenode and using the ```stream list``` command. I had to use ```stream destroy --name STREAMNAME``` to actually get things working. Streams that failed to Deploy are not auto-cleaned up either.

1. Do not create more than one MQTT Source Subscriber to the same topic

  I did this to inspect what would happen and it crashed my xd-singlenode instance. The cluster is still running, but I had to restart the xd-singlenode instance.

1. In Distributed Mode - The xd-singlenode fails to connect to zookeeper:

  ```
  12:58:24,316  INFO HSQLDB Server @11e17893 HSQLDB50D492CA74.ENGINE - checkpointClose start
  12:58:24,335  INFO HSQLDB Server @11e17893 HSQLDB50D492CA74.ENGINE - checkpointClose end

  2015-11-05T12:58:29-0500 1.2.1.RELEASE WARN main-SendThread(localhost:2181) zookeeper.ClientCnxn - Session 0x0 for server null, unexpected error, closing socket connection and attempting reconnect
  java.net.ConnectException: Connection refused
      at sun.nio.ch.SocketChannelImpl.checkConnect(Native Method) ~[na:1.8.0_60]
      at sun.nio.ch.SocketChannelImpl.finishConnect(SocketChannelImpl.java:717) ~[na:1.8.0_60]
  ```

  Please restart the zookeeper instance:

  ```spring-xd-1.2.1.RELEASE/zookeeper/bin$ ./zkServer.sh stop```
  ```spring-xd-1.2.1.RELEASE/zookeeper/bin$ ./zkServer.sh start```

  Now try the xd-singlenode again
 
1. What to do if the Spring XD configuration file is broken

  A working Spring XD servers.yml (preconfigured to connect to all components) is included in the repo.

  Copy: https://github.com/GetLevvel/message-simulator/blob/master/simulations/rabbit/spring-xd/configs/servers.yml to ```spring-xd-1.2.1.RELEASE/xd/config/servers.yml```


