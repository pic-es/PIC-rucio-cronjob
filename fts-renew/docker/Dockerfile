version: "2"
services:
  fts-renew:
    build:
      context: .
      dockerfile: docker-compose.yaml
    hostname: fts-renew
    restart: always
    environment:
      - ftsserver=https://fts01.pic.es:8446
    volumes: 
      - ../certs-folder/hostcert.pem:/etc/grid-security/usercert.pem
      - ../certs-folder/hostkey.pem:/etc/grid-security/userkey.pem
