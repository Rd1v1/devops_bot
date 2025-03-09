CREATE DATABASE tg_bot;

\c tg_bot;

CREATE USER repl_user WITH REPLICATION PASSWORD '123';
ALTER USER postgres WITH PASSWORD '123';

CREATE TABLE phone_numbers(
    id SERIAL PRIMARY KEY,
    phone_number varchar(20)
);

CREATE TABLE emails(
    id SERIAL PRIMARY KEY,
    email varchar(255)
);
