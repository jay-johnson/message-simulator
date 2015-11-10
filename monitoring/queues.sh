#!/bin/bash

echo ""
echo "Displaying Cluster Queues"
echo ""

rabbitmqadmin list queues name node durable auto_delete messages consumers memory state exclusive_consumer_tag policy arguments

echo ""


