#!/bin/bash
locale-gen "en_US.UTF-8"
service postgresql start
service ssh start
until pg_isready -U postgres; do
  sleep 2
done
psql -U postgres -f /init.sql
echo "postgres:123" | chpasswd
while true; do sleep 1; done