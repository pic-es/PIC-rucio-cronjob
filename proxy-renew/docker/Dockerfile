version: "2"
services:
  proxy-renew:
    build:
      context: .
      dockerfile: docker-compose.yaml
    hostname: proxy-renew
    restart: always
    volumes: 
      - ../host-cert-k8s-v2/hostcert.pem:/tmp/robotcert.pem
      - ../host-cert-k8s-v2/hostkey.pem:/tmp/robotkey.pem
