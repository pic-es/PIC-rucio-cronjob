version: "2"
services:
  rucio-monitoring-startup:
    build:
      context: .
      dockerfile: docker-compose.yaml
    hostname: rucio-monitoring-startup
    restart: always
    environment:
      - RUCIO_CFG_RUCIO_HOST=https://pic01-rucio-server.pic.es:443
      - RUCIO_CFG_AUTH_HOST=https://pic01-rucio-server-auth.pic.es:443
      - RUCIO_CFG_CA_CERT=/etc/grid-security/certificates
      - RUCIO_CFG_AUTH_TYPE=userpass
      - RUCIO_CFG_USERNAME=ddmlab
      - RUCIO_CFG_PASSWORD=secret
      - RUCIO_CFG_ACCOUNT=root
    volumes: 
      - ../../../host-cert-k8s-v4/hostcert.pem:/opt/rucio/etc/usercert/usercert.pem
      - ../../../host-cert-k8s-v4/hostkey.pem:/opt/rucio/etc/userkey/userkey.pem
