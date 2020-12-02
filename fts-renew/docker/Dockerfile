version: "2"
services:
  fts-renew:
    build:
      context: .
      dockerfile: docker-compose.yaml
    hostname: fts-renew
    restart: always
    volumes: 
      - ../host-cert-k8s-v2/hostcert.pem:/etc/grid-security/usercert.pem
      - ../host-cert-k8s-v2/hostkey.pem:/etc/grid-security/userkey.pem
