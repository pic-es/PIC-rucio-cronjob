#!/bin/bash
#
# fts_proxy
#
# Create an x509 proxy from the host's igtf grid certificate and delegate
# against the osg fts server at https://fts01.pic.es:8446.  Run this script (as
# root) as a cronjob to maintain an FTS-delegated proxy for rucio operations.
#
## Configuration
ftsproxylog=/var/log/fts-proxy.log
proxytool=/usr/bin/voms-proxy-init 
hostcert=/etc/grid-security/usercert.pem
hostkey=/etc/grid-security/userkey.pem
x509proxy=/tmp/x509up_u0
ftsdelegate=/bin/fts-rest-delegate

# export PASSPHRASE="if needed"

## Logging info
dtstamp="`date +%F-%A-%H.%M.%S `"
echo -e "\n################ ${dtstamp} ################" >> ${ftsproxylog}

## Create robot proxy
echo -e "${dtstamp}: ${proxytool} -cert ${hostcert} -key ${hostkey} -out ${x509proxy} -debug "
echo ${proxytool} -cert ${hostcert} -key ${hostkey} -out  ${x509proxy} -pwstdin -debug 2>> ${ftsproxylog} 2>&1
proxy_ret=$?
echo -e "${dtstamp}: ${proxytool} return: ${proxy_ret}\n" >> ${ftsproxylog} 2>&1

${proxytool} -cert ${hostcert} -key ${hostkey} -out  ${x509proxy} -pwstdin -debug 2>> ${ftsproxylog} 2>&1

## Delgate proxy

echo -e "${ftsdelegate} -f -v -s ${ftsserver} --cert ${x509proxy} --key ${x509proxy}"  >> ${ftsproxylog} 2>&1

${ftsdelegate} -f -v -s ${ftsserver} --cert ${x509proxy} --key ${x509proxy}  >> ${ftsproxylog} 2>&1

cat ${ftsproxylog}

delegate_ret=$? 
echo -e "${dtstamp}: ${ftsdelegate} return: ${delegate_ret}" >> ${ftsproxylog} 2>&1


