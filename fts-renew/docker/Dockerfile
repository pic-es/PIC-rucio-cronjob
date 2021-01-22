version: "2"
services:
  fts-renew:
    build:
      context: .
      dockerfile: docker-compose.yaml
    hostname: fts-renew
    restart: always
    volumes: 
      - ../host-cert-k8s-v4/hostcert.pem:/etc/grid-security/usercert.pem
      - ../host-cert-k8s-v4/hostkey.pem:/etc/grid-security/userkey.pem
