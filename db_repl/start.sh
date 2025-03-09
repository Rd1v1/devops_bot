#!/bin/bash
locale-gen "en_US.UTF-8"
service postgresql start
service ssh start
until pg_isready -U postgres; do
  sleep 2
done
echo "postgres:123" | chpasswd
service postgresql stop
sleep 10
rm -rf /var/lib/postgresql/16/main/*
export PGPASSWORD="123"
pg_basebackup -R -h db -U repl_user -D /var/lib/postgresql/16/main -P
chmod -R 777 /var/lib/postgresql/16/main/*
sleep 10
service postgresql start
until pg_isready -U postgres; do
  sleep 2
done
while true; do sleep 1; done