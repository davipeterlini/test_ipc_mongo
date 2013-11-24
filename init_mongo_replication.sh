#!/bin/bash
#
#This script is responsible for finalizing all the old MongoDB 
# instances that were running on the machine; 
# initialize new instances, confirming the existence of a main body (primary) 
# and activate other instances (secondary) through the file initReplicaSet.js
#

SCRIPT_NAME="init_mongo_replication"
MONGODB_ADDR="192.168.10.1"
RF_HOME=`cd /home/routeflow/test_ipc_mongo;pwd`


#killall Instaces of MongoBD
kill_process_tree() {
    top=$1
    pid=$2

    children=`ps -o pid --no-headers --ppid ${pid}`

    for child in $children
    do
        kill_process_tree 0 $child
    done

    if [ $top -eq 0 ]; then
        kill -9 $pid &> /dev/null
    fi
}

reset() {
    init=$1;
    if [ $init -eq 1 ]; then
        echo "-> Starting $SCRIPT_NAME";
    else
        echo "-> Stopping child processes...";
        kill_process_tree 1 $$
    fi

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
}
reset 1
trap "reset 0; exit 0" INT


#Starting ReplicaSet service for MongoBD
echo "-> Setting up the management bridge (lxcbr0)..."
brctl addbr lxcbr0 &> /dev/null
ifconfig lxcbr0 $MONGODB_ADDR up

echo "-> Setting up MongoDB instance 1..."
mongod -f $RF_HOME/mongo/conf/master.conf --replSet rs0

echo "-> Setting up MongoDB instance 2..."
mongod -f $RF_HOME/mongo/conf/slave1.conf --replSet rs0

echo "-> Setting up MongoDB instance 3..."
mongod -f $RF_HOME/mongo/conf/slave2.conf --replSet rs0


# Conferring if instance exists to master
echo "-> Initializing Replica set..."
mongo --quiet 192.168.10.1:27017 --eval "rs.initiate()"

while [[ `mongo --quiet 192.168.10.1:27017 --eval "db.isMaster().ismaster"` == false ]]; do
    echo "Waiting instance becomes primary..."
    sleep 5       
done


# Up more two instances (ReplicaSet)
mongo 192.168.10.1:27017 --eval "load('$RF_HOME/initReplicaSet.js')"

echo "-> Waiting 30s for replica set intialization..."
sleep 30