#include "ExampleProtocol.h"
#include <RFProtocol.h>
#include <mongo/client/dbclient.h>

ExampleMessage::ExampleMessage() {
    set_a(false);
    set_b(0);
    set_c("");
}

ExampleMessage::ExampleMessage(bool a, uint32_t b, string c) {
    set_a(a);
    set_b(b);
    set_c(c);
}

int ExampleMessage::get_type() {
    return EXAMPLE_MESSAGE;
}

bool ExampleMessage::get_a() {
    return this->a;
}

void ExampleMessage::set_a(bool a) {
    this->a = a;
}

uint32_t ExampleMessage::get_b() {
    return this->b;
}

void ExampleMessage::set_b(uint32_t b) {
    this->b = b;
}

string ExampleMessage::get_c() {
    return this->c;
}

void ExampleMessage::set_c(string c) {
    this->c = c;
}

void ExampleMessage::from_BSON(const char* data) {
    mongo::BSONObj obj(data);
    set_a(obj["a"].Bool());
    set_b(string_to<uint32_t>(obj["b"].String()));
    set_c(obj["c"].String());
}

const char* ExampleMessage::to_BSON() {
    mongo::BSONObjBuilder _b;
    _b.append("a", get_a());
    _b.append("b", to_string<uint32_t>(get_b()));
    _b.append("c", get_c());
    mongo::BSONObj o = _b.obj();
    char* data = new char[o.objsize()];
    memcpy(data, o.objdata(), o.objsize());
    return data;
}

string ExampleMessage::str() {
    stringstream ss;
    ss << "ExampleMessage" << endl;
    ss << "  a: " << get_a() << endl;
    ss << "  b: " << to_string<uint32_t>(get_b()) << endl;
    ss << "  c: " << get_c() << endl;
    return ss.str();
}
