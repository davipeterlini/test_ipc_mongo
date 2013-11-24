#!/bin/bash
#
# Script used to finalize all the old MongoDB instances 
# that were running on the machine 
# where the executable is finished test_ipc_mongo.cc
#

RF_HOME=`cd /home/routeflow/test_ipc_mongo;pwd`

MONGOPID=`ps -ef | grep 'mongo' | grep -v grep | awk '{print $2}'`
if [[ $MONGOPID == true ]]; then
     echo "-> Kill all services MongoDB..."    
     kill -15 $MONGOPID &> /dev/null
fi

echo "-> Shutting down MongoDB instance 1..."
mongod -f $RF_HOME/mongo/conf/master.conf --replSet rs0 --shutdown &> /dev/null

echo "-> Shutting down MongoDB instance 2..."
mongod -f $RF_HOME/mongo/conf/slave1.conf --replSet rs0 --shutdown &> /dev/null

echo "-> Shutting down MongoDB instance 3..."
mongod -f $RF_HOME/mongo/conf/slave2.conf --replSet rs0 --shutdown &> /dev/null

echo "-> Deleting data from previous runs...";
rm -rf $RF_HOME/mongo/data/*/*