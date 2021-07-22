version: "2"
services:
  rucio-sync-rses:
    build:
      context: .
      dockerfile: docker-compose.yaml
    hostname: rucio-sync-rses
    restart: always
    environment:
      - ftsserver=https://fts01.pic.es:8446
