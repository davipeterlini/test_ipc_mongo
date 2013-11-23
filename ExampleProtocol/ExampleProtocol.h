#ifndef __EXAMPLEPROTOCOL_H__
#define __EXAMPLEPROTOCOL_H__

#include <stdint.h>

#include "Ipc.h"
#include "IPAddress.h"
#include "MACAddress.h"
#include "converter.h"
#include "Action.hh"
#include "Match.hh"
#include "Option.hh"

// enum {
// 	EXAMPLE_MESSAGE
// };

class ExampleMessage : public IpcMessage {
    public:
        ExampleMessage();
        ExampleMessage(bool a, uint32_t b, string c);

        bool get_a();
        void set_a(bool a);

        uint32_t get_b();
        void set_b(uint32_t b);

        string get_c();
        void set_c(string c);

        virtual int get_type();
        virtual void from_BSON(const char* data);
        virtual const char* to_BSON();
        virtual string str();

    private:
        bool a;
        uint32_t b;
        string c;
};

#endif /* __EXAMPLEPROTOCOL_H__ */