# Below is a couple of scripts that facilitate other tests to interact with Rucio's server. In each one of them, the amount and scope corresponding to the person are owed (and in the case that the RSEs are desired, although it is not necessary)

First of all, here is a script to do simple uploads of randoms fixers :
https://gitlab.pic.es/bruzzese/Rucio-register-files/-/blob/master/Tests/Rucio-Client/Rucio02.pic.es/test-create-files.py

Then, we have two scripts to test transfer functionalities through fts and some demons.

Creation of files in the non-deterministic RSE:
https://gitlab.pic.es/bruzzese/Rucio-register-files/-/blob/master/Tests/Rucio-Client/Rucio02.pic.es/test-upload.py

Replication of those files in the deterministic RSE:
https://gitlab.pic.es/bruzzese/Rucio-register-files/-/blob/master/Tests/Rucio-Client/Rucio02.pic.es/test-create-rules.py

#### The correct operation of all these scripts is strictly related to the identification and authentication against the black server using certificates. If the identification is carried out by user / pass, the scripts will not work and will give a permission error