#include <Ipc.h>
#include <MongoIpc.h>
#include <RFProtocol.h>
#include <ExampleProtocol/ExampleProtocol.h>
#include <IpcMessageProcessor.h>
#include <IpcMessage.h>
#include <stdio.h>
#include <signal.h>

class ExampleProtocolProcessor : public IpcMessageProcessor {
    public:
        ExampleProtocolProcessor() { }

    private:

        virtual void process(IpcMessage* msg) {
            cout << endl;
            cout << "Message from " << msg->getFrom() << " to " << msg->getTo() << endl;
            int type = msg->get_type();
            if (type == EXAMPLE_MESSAGE) {
                // Remember to use a dynamic_cast
                ExampleMessage *ex = dynamic_cast<ExampleMessage*>(msg);
                // Our example processing prints the message
                cout << ex->str() << endl;
            }
            cout << "-> Destination: " << endl;
            //return true;
        }
};
void signal_callback_handler(int signum){
   printf("Caught signal %d\n",signum);
   // Cleanup and close up stuff here

    system("mongod -f /home/routeflow/test_ipc_mongo/mongo/conf/master.conf --replSet rs0 --shutdown");
    system("mongod -f /home/routeflow/test_ipc_mongo/mongo/conf/slave1.conf --replSet rs0 --shutdown");
    system("mongod -f /home/routeflow/test_ipc_mongo/mongo/conf/slave2.conf --replSet rs0 --shutdown");
    system("rm -rf /home/routeflow/test_ipc_mongo/mongo/data/*/*");

   // Terminate program
   exit(signum);
}

int main(int argc, char* argv[]) {

    signal(SIGINT, signal_callback_handler);

	if (argc < 3) {
		cout << "Usage:" << endl;
		cout << "  " << "./ipc [sender] [mongobd_collection] [destination]" << endl;
		exit(EXIT_FAILURE);
	}

    // script of Mongo Replication
    system("/home/routeflow/test_ipc_mongo/./init_mongo_replication.sh");

    // We need to establish the IPC service that will send and receive messages
    // The first argument must specify the sender
    // The second argument must specify the mongo collection 
    MongoIpc ipc(argv[1], argv[2]);
    
    // A processor is responsible for doing whatever your program wants to do
    // When it receives a message
    ExampleProtocolProcessor *processor = new ExampleProtocolProcessor();
    
    // Waiting the messages in separate thread
    ipc.parallelListen(processor);  
    
    // Define qtd messages 
    long int msgQtde = 1000000;

    double cal = (msgQtde/2.0) + 1.0;
    string destination, data;

    while (msgQtde > 0) {

        // Time between each message
        usleep(100);

        // changing last message
        if (msgQtde == 1)
            data="last_message"; 
        else
            data="test_replication"; 
        
        // We create our message object (which is based on IPCMessage)
        ExampleMessage m(true, 1, data);

        //Configuring sender and destination
        m.setFrom(argv[1]);
        m.setTo(argv[3]);

        // And then we send it using the service
        ipc.send(&m);

        // stopped condition (mensagens/2)
        if (msgQtde == cal) {
            system("mongod -f /home/routeflow/test_ipc_mongo/mongo/conf/master.conf --replSet rs0 --shutdown");
            sleep(5);
        }       
        msgQtde--;
    }

    while (true) { 
    sleep(25);
    cout << "\n\n--> Press Ctrl+c to finish this program correctly...\n\n\n";
    }

    getchar();
    return 0;
}
