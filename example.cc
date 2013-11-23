#include <Ipc.h>
#include <MongoIpc.h>
#include <RFProtocol.h>
#include <ExampleProtocol/ExampleProtocol.h>
#include <IpcMessageProcessor.h>
#include <IpcMessage.h>
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

   system("mongod -f /home/routeflow/RouteFlow/rftest/mongo/conf/master.conf --replSet rs0 --shutdown");
   system("mongod -f /home/routeflow/RouteFlow/rftest/mongo/conf/slave1.conf --replSet rs0 --shutdown");
   system("mongod -f /home/routeflow/RouteFlow/rftest/mongo/conf/slave2.conf --replSet rs0 --shutdown");

   // Terminate program
   exit(signum);
}

int main(int argc, char* argv[]) {

    signal(SIGINT, signal_callback_handler);

	if (argc < 3) {
		cout << "Usage:" << endl;
		cout << "  " << "./ipc [sender] [collection name] [destination]" << endl;
		exit(EXIT_FAILURE);
	}

    // script of Mongo Replication
    system("/home/routeflow/test_ipc_mongo/./init.sh");

    // We need to establish the IPC service that will send and receive messages
    // The first argument must specify the ID
    // The second argument must specify the database name
    MongoIpc ipc(argv[1], argv[2]);
    
                // A Ipc is responsible for creating message objects for a given type
                // ExampleProtocolFactory *factory = new ExampleProtocolFactory();
    
    // A processor is responsible for doing whatever your program wants to do
    // When it receives a message
    ExampleProtocolProcessor *processor = new ExampleProtocolProcessor();
    
                // We can listen to messages in more than one channel
                // The third argument will name a listen channel
    ipc.parallelListen(processor);
    
                // Just an example loop to send messages
    string destination, data;
    
    // Waiting instances of mongobd to load
    usleep(100);
    
    // Variable Defines
    long int msgQtde;
    cout<< "\n\nIt types the number of messages to be send:\n";
    cin >> msgQtde;
    double cal = msgQtde/2.0;

    while (msgQtde > 0) {

        data="test_replication"; 

        // Time between each message
        usleep(100);
        
        // We create our message object (which is based on IPCMessage)
        ExampleMessage m(true, 1, data);
        m.setFrom(argv[1]);

        if (msgQtde == 1)
            m.setTo("***last_messages***");
        else
            m.setTo(argv[3]);
        
        // And then we send it using the service
        // The fourth argument will name a send channel
        ipc.send(&m);

        if (msgQtde == cal) {
            cout <<"\n\nCondition of stop Instance is equal the number of typed messages divided for 2";
            cout << "\nBefore and to kill the instance to master confers the messagens in mongo...";
            cout << "\nPress any keyboard to kill an instance Master of Mongo...\n";
            char killall;
            cin >> killall;
            cout << endl;
            system("mongod -f /home/routeflow/RouteFlow/rftest/mongo/conf/master.conf --replSet rs0 --shutdown");
            sleep(5);
        }       
        msgQtde--;
    }

    cout << "\n\n\nValor do msgQtde:" << msgQtde << "\n";
    cout << "\nPress Ctrl+c to finish this program...\n\n";
    char finish;
    cin >> finish;
    return 0;
}
