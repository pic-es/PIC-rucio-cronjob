# First Steps into Rucio
git clone https://gitlab.pic.es/bruzzese/rucio-client.git

cd rucio-client

cat README.md

#### In the event that you do not have an account, using the root account with functionality limitations (only basic functions can be performed by interacting with the rucio API, such as "rucio ping" or "rucio whoami"). If you want to create an account, write an email to bruzzese@pic.es with a copy to merino@pic.es and tallada@pic.es. For more information on account management, please read: https://redmine.pic.es/issues/990

#### Else, If you already have an account 
cd  Rucio02.pic.es

#### and then change your user configuration
nano rucio.cfg 

# Second step build a docker image of Rucio client 

#### If you do not have user certificate :
sudo docker-compose --file docker-compose.yml up -d --build

#### With user certificate 
sudo docker-compose --file docker-compose.yml up -d -v /[location of your key certificate]/usercert.pem:/etc/grid-security/usercert.pem -v /[location of your key certificate]/usercert.key:/etc/grid-security/usercert.key -e X509_USER_CERT=/etc/grid-security/usercert.pem -e X509_USER_KEY=/etc/grid-security/usercert.key

# Third step, go inside the client image 
docker exec -it dev_rucio-client-startup /bin/bash

# Possible next update. Transform this repository into a docker repository.
