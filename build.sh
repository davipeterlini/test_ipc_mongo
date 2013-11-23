#!/bin/sh

IPC=`pwd`
INCLUDES="-I$IPC -I$IPC/ipc -I$IPC/types"

if [ "$1" = "clean" ]; then
    rm -f $IPC/ipc/*.so $IPC/ipc/*.o $IPC/ipc/*.pyc $IPC/ipc/*.pyo
    rm -f $IPC/types/*.so $IPC/types/*.o $IPC/types/*.pyc $IPC/types/*.pyo
    exit;
fi;
#Build core IPC
LIBS="-lmongoclient -lboost_thread -lboost_system -lboost_filesystem "\
"-lboost_program_options"
cd $IPC
cd ipc
clang -c -fPIC *.cc $INCLUDES
gcc -shared *.o $LIBS -o libipc.so 

# Build IPC types
cd $IPC
cd types
clang -c -fPIC *.cc $INCLUDES
gcc -shared *.o -o libipctypes.so

# Build example program
LIBS="-lboost_system"
cd $IPC
clang example.cc ExampleProtocol/*.cc \
$IPC/ipc/libipc.so $IPC/types/libipctypes.so \
$INCLUDES $LIBS -o example
