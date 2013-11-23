test_ipc_mongo
==============

Teste entre Mongo e IPC

Este teste consiste na troca de mensagens entre mongo e IPC e 
engloba toda a parte de replicação, até então implementada.

Para iniciar os teste acesse a RF_VM através de ssh ou SOFT.
inicialmente é preciso instalar o compilador 
sudo apt-get install clang

Faça o clone dos arquivos da IPC com replicação através do comando:
git clone https://github.com/davipeterlini/test_ipc_mongo.git

Em seguida, acesse a pasta clonada (cd <PASTA_CLONADA>) e crie um link para a lib do 
mongoclient com o comando 
sudo ln -s<PASTA_CLONADA>/libmongoclient.so /usr/lib/

Antes da execução do teste entre no script init.sh e mude a variável RF_HOME 
para a que correspondente ao nome do seu diretório clonado do git.

Entre tambem no arquivo example.cc e altera a linha 52 colocando 
dentro da função system o caminho correspondente ao seu diretório. 
obs: De forma resumida o arquivo example.cc é o arquivo que contei a 
implementação para teste de troca de mensagens entre IPC e MongoBD

Gere o executável digitando sudo ./build.sh na raiza da pasta clonada

Após compilação o teste pode ser executado através do comando sudo ./example.
obs: caso seja preciso ajustar algo no código example.cc é necessário recompilar
para isso utilize sudo ./build clean && sudo ./build.sh.
