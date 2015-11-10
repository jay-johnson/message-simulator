#!/bin/bash

echo ""
echo "Displaying Cluster Exchanges"
echo ""

rabbitmqadmin list exchanges name type durable auto_delete internal policy vhost arguments

echo ""


