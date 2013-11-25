import ExampleProtocol.ExampleProtocol as Protocol
import bson
import threading
import pymongo as mongo
import time
import sys

from ipc.Ipc import Ipc
from ipc.MongoUtils import MongoFactory
from defs import *

FIELD_NAME_ID = "_id"
FIELD_NAME_FROM = "from"
FIELD_NAME_TO = "to"
FIELD_NAME_TYPE = "type"
FIELD_NAME_READ = "read"
FIELD_NAME_CONTENT = "content"

# 1 MB for the capped collection
CC_SIZE = 1048576

class MongoIpc(Ipc):

    def __init__(self, user_id, channel_id):
        self._mf = MongoFactory()
        self._producer_connection = self._mf.create_connection()
        self._user_id = user_id
        self._channel_id = channel_id
        self._db_name = MONGO_DB_NAME

        db = self._producer_connection[self._db_name]
        try:
            collection = mongo.collection.Collection(db, self._channel_id, True, capped=True, size=CC_SIZE)
            collection.ensure_index([("_id", mongo.ASCENDING)])
            collection.ensure_index([(FIELD_NAME_TO, mongo.ASCENDING)])
        except:
            print "channel already exists"

    def listen(self, message_processor):
        #self._producer_connection = self._mf.create_connection()
        while True:            
            # tries to get unread messages
            for i in xrange(0, MONGO_MAX_RETRIES):            
                try:
                    collection = self._producer_connection[self._db_name][self._channel_id]
                    cursor = collection.find(
                        {FIELD_NAME_TO: self._user_id, FIELD_NAME_READ: False},
                        tailable=True
                    )
                    
                    #cursor OK, break for
                    break
                
                except:                    
                    if (i + 1) == MONGO_MAX_RETRIES:
                        print "[ERROR]MongoIPC: Could not get unread messages. Error: (", sys.exc_info(), ")"                                   
                        sys.exit(2)
                        
                    print "[RECOVERING]MongoIPC: Could not get unread messages. Trying again in ", MONGO_RETRY_INTERVAL, " seconds. [",  (i+1),  "]"                
                    time.sleep(MONGO_RETRY_INTERVAL)
            
            while cursor.alive:
                
                try:
                    envelope = next(cursor, None)
                    if envelope == None:
                        break;
                    
                except StopIteration:
                    time.sleep(1)
                    continue
                except:
                    #print "[RECOVERING]MongoIPC: Fail to reach messages. Err:",sys.exc_info()
                    break;
                
                ipc_message = MongoIpcMessageFactory.fromMongoMessageType(envelope)
                message_processor.process(ipc_message);
                        
                # tries to mark message as read
                for j in xrange(0, MONGO_MAX_RETRIES):                            
                    try:
                        collection = self._producer_connection[self._db_name][self._channel_id]
                        collection.update({"_id": envelope["_id"]},
                                          {"$set": {FIELD_NAME_READ: True}})                                
                                                       
                        # update done, break for
                        break
                        
                    except:                                
                        if (j + 1) == MONGO_MAX_RETRIES:
                            print "[ERROR]MongoIPC: The Message (id: ",
                            print envelope["_id"], 
                            print ") could not be marked as read. ",
                            print "Error: (", sys.exc_info, ")"
                            sys.exit(1)
                                                                                           
                        print "[RECOVERING]MongoIPC: Could not mark message ",
                        print "as read. Trying again in ",
                        print MONGO_RETRY_INTERVAL, " seconds. [", (j+1), "]"
                        time.sleep(MONGO_RETRY_INTERVAL)
                    
                print "[OK]MongoIPC: Message (id: ", envelope["_id"], ") was marked as Read."    
                    
            time.sleep(0.05)       

    def parallel_listen(self, message_processor):
        worker = threading.Thread(target=self.listen, args=(message_processor,))
        worker.start()
        
    def send(self, ipc_message):
        #self._producer_connection = self._mf.create_connection()
        mongo_message = MongoIpcMessageFactory.fromMessageType(ipc_message)                
        for i in xrange(0, MONGO_MAX_RETRIES):            
            try:                
                collection = self._producer_connection[self._db_name][self._channel_id]
                collection.insert(mongo_message)
                                
                break;
                           
            except:
                if (i + 1) == MONGO_MAX_RETRIES:
                    print "[ERROR]MongoIPC: Message could not be sent. ",
                    print "Error: (", sys.exc_info(), ")"
                    sys.exit(1)
                        
                print "[RECOVERING]MongoIPC: Message not sent. ",
                print "Trying again in ", MONGO_RETRY_INTERVAL, " seconds. ",
                print "[", (i+1), "]"
                
                time.sleep(MONGO_RETRY_INTERVAL)
                
        #print "[OK]MongoIPC: Message sent"
        return True
        



class MongoIpcMessageFactory:
    """This class implements a factory to build a Ipc Message object from Bson Object and vice versa"""
    @staticmethod
    def fromMongoMessageType(mongo_obj):
        """Receives mongo BSONObj and build an
           ipc message object, based on message type"""
        #message = bson.BSON.decode(mongo_obj)
        message = mongo_obj
        message_content = message[FIELD_NAME_CONTENT]
        ipc_message = None
        
        if int(message[FIELD_NAME_TYPE]) == Protocol.EXAMPLE_MESSAGE:
            ipc_message = RFProtocol.PortRegister()
            ipc_message.set_a(message_content["a"])
            ipc_message.set_b(message_content["b"])
            ipc_message.set_c(message_content["c"])


        else:
            return None

        ipc_message.set_message_id(message[FIELD_NAME_ID])
        ipc_message.set_to(message[FIELD_NAME_TO])
        ipc_message.set_from(message[FIELD_NAME_FROM])
        ipc_message.set_read(message[FIELD_NAME_READ])

	return ipc_message

            

    @staticmethod
    def fromMessageType(ipc_message):
        """Receives the ipc message object and build a mongo Bson Object,
           based on message type"""

        mongo_message = {}
        mongo_message[FIELD_NAME_ID] = bson.objectid.ObjectId(ipc_message.get_message_id())
        mongo_message[FIELD_NAME_TO] = str(ipc_message.get_to())
        mongo_message[FIELD_NAME_FROM] = str(ipc_message.get_from())
        mongo_message[FIELD_NAME_READ] = ipc_message.is_read()
        mongo_message[FIELD_NAME_TYPE] = ipc_message.get_type()

        message_content = {}
        if int(ipc_message.get_type()) == Protocol.EXAMPLE_MESSAGE:
            message_content["a"] = str(ipc_message.get_a())
            message_content["b"] = str(ipc_message.get_b())
            message_content["c"] = str(ipc_message.get_c())


        else:
            return None

        mongo_message[FIELD_NAME_CONTENT] = message_content

	return mongo_message

