#!/bin/bash

RF_HOME=`cd ../RouteFlow/;pwd`

#killall Instaces of ongoBD
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
    if [ $MONGOPID == true ]; then
         echo "-> Kill all services MongoDB..."    
         kill -15 $MONGOPID &> /dev/null
    fi
   
    echo "-> Shutting down MongoDB instance 1..."
    mongod -f $RF_HOME/rftest/mongo/conf/master.conf --replSet rs0 --shutdown &> /dev/null

    echo "-> Shutting down MongoDB instance 2..."
    mongod -f $RF_HOME/rftest/mongo/conf/slave1.conf --replSet rs0 --shutdown &> /dev/null

    echo "-> Shutting down MongoDB instance 3..."
    mongod -f $RF_HOME/rftest/mongo/conf/slave2.conf --replSet rs0 --shutdown &> /dev/null

    echo "-> Deleting data from previous runs...";
    rm -rf $RF_HOME/rftest/mongo/data/*/*
}
reset 1
trap "reset 0; exit 0" INT

#Starting ReplicaSet service for MongoBD
echo "-> Setting up MongoDB instance 1..."
mongod -f $RF_HOME/rftest/mongo/conf/master.conf --replSet rs0

echo "-> Setting up MongoDB instance 2..."
mongod -f $RF_HOME/rftest/mongo/conf/slave1.conf --replSet rs0

echo "-> Setting up MongoDB instance 3..."
mongod -f $RF_HOME/rftest/mongo/conf/slave2.conf --replSet rs0


# Conferring if instance exists to master
echo "-> Initializing Replica set..."
mongo --quiet 192.168.10.1:27017/db --eval "rs.initiate()"

while [[ `mongo --quiet 192.168.10.1:27017/db --eval "db.isMaster().ismaster"` == false ]]; do
    echo "Waiting instance becomes primary..."
    sleep 5       
done


# Up more two instances (ReplicaSet)
mongo 192.168.10.1:27017/db --eval "load('$RF_HOME/rftest/initReplicaSet.js')"

echo "-> Waiting 10s for replica set intialization..."
sleep 10