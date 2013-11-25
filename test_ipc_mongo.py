#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import binascii
import threading
import time
import argparse
import subprocess
import signal
from bson.binary import Binary

import ipc.Ipc as Ipc
from ExampleProtocol.ExampleProtocol import ExampleMessage
import ipc.MongoIpc as MongoIpc
from defs import *

usleep = lambda x: time.sleep(x/1000000.0)

def signal_handler(signal, frame):
	subprocess.call(['mongod', '-f', '/home/routeflow/test_ipc_mongo/mongo/conf/master.conf', '--replSet', 'rs0', '--shutdown'])
	subprocess.call(['mongod', '-f', '/home/routeflow/test_ipc_mongo/mongo/conf/slave1.conf', '--replSet', 'rs0', '--shutdown'])
	subprocess.call(['mongod', '-f', '/home/routeflow/test_ipc_mongo/mongo/conf/slave2.conf', '--replSet', 'rs0', '--shutdown'])
	subprocess.call(['rm', '-rf', '/home/routeflow/test_ipc_mongo/mongo/data/*/*'])
	sys.exit(0)

class ExampleProtocolProcessor(Ipc.IpcMessageProcessor):
    def __init__(self):
	print ''

    def process(self, msg):
        type_ = msg.get_type()
        if type_ == EXAMPLE_MESSAGE:
            print msg.str()

if __name__ == "__main__":

	signal.signal(signal.SIGINT, signal_handler)
	description='Test for MongoIPC(Python) '
	epilog=''
	parser = argparse.ArgumentParser(description=description, epilog=epilog)
	parser.add_argument('sender', help='Sender of messages')
	parser.add_argument('mongo_collection', help='Mongo Collection')
	parser.add_argument('to', help='Send messages to')
	args = parser.parse_args()
	print 'Starting Test...'
	subprocess.call(['mongod', '-f', '/home/routeflow/test_ipc_mongo/mongo/conf/master.conf', '--replSet', 'rs0', '--shutdown'])
	subprocess.call(['mongod', '-f', '/home/routeflow/test_ipc_mongo/mongo/conf/slave1.conf', '--replSet', 'rs0', '--shutdown'])
	subprocess.call(['mongod', '-f', '/home/routeflow/test_ipc_mongo/mongo/conf/slave2.conf', '--replSet', 'rs0', '--shutdown'])
	subprocess.call(['rm', '-rf', '/home/routeflow/test_ipc_mongo/mongo/data/*/*'])
	subprocess.call('./init_mongo_replication.sh')
	
	# The second argument must specify the mongo collection 
	ipc = MongoIpc.MongoIpc(args.sender, args.mongo_collection)    
	# A processor is responsible for doing whatever your program wants to do
	# Waiting the messages in separate thread
	ipc.parallel_listen(ExampleProtocolProcessor())
	    
	# Define qtd messages 
	msgQtde = 1000

	print 'Sending ', msgQtde, ' messages'
	cal = (msgQtde/2.0) + 1.0
	while msgQtde > 0:
		# Time between each message
		usleep(100)

		# changing last message
		if msgQtde == 1:
		    data="last_message"
		else:
		    data="test_replication"
		
		# We create our message object (which is based on IPCMessage)
		m = ExampleMessage(True, 1, data)

		#Configuring sender and destination
		m.set_from(args.sender)
		m.set_to(args.to)

		# And then we send it using the service
		ipc.send(m)

		# stopped condition (mensagens/2)
		if msgQtde == cal:
			subprocess.call(['mongod', '-f', '/home/routeflow/test_ipc_mongo/mongo/conf/master.conf', '--replSet', 'rs0', '--shutdown'])
			time.sleep(5)
		msgQtde = msgQtde - 1
	print 'end of test'
	sys.exit()


	   
