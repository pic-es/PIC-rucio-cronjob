#!/bin/bash

if [ ! -f /tmp/robotkey.pem ] && [ -f /etc/secrets/robotkey.pem ]; then
    sudo cp /etc/secrets/robotkey.pem /tmp
    sudo chmod 0400 /tmp/robotkey.pem
    sudo chown $USER /tmp/robotkey.pem
    sudo chgrp $USER /tmp/robotkey.pem
fi
if [ ! -f /tmp/robotcert.pem ] && [ -f /etc/secrets/robotcert.pem ]; then
    sudo cp /etc/secrets/robotcert.pem /tmp
    sudo chown $USER /tmp/robotcert.pem
    sudo chgrp $USER /tmp/robotcert.pem
fi
if [ -f /tmp/robotkey.pem ] && [ -f /tmp/robotcert.pem ]; then
    # keep proxy validity for 4 days (roll over long weekend)
    voms-proxy-init -voms -rfc -valid 95:50 \
        -key /tmp/robotkey.pem \
        -cert /tmp/robotcert.pem \
        -out /tmp/proxy
    out=$?
    if [ $out -eq 0 ]; then
        kubectl create secret generic proxy-secrets \
            --from-file=/tmp/proxy --dry-run=client -o yaml | \
            kubectl apply --validate=false -f -
    else
        echo "Failed to obtain new proxy, voms-proxy-init error $out"
        echo "Will not update proxy-secrets"
    fi
fi
