create database if not exists ece140;

use ece140;

-- DUMP EVERYTHING... YOU REALLY SHOULDN'T DO THIS!
drop table if exists users;
drop table if exists sessions;

create table if not exists users (
  id         integer auto_increment primary key,
  first_name varchar(64) not null,
  last_name  varchar(64) not null,
  username   varchar(64) not null unique,
  password   varchar(64) not null,
  created_at timestamp not null default current_timestamp
);

create table if not exists sessions (
  session_id varchar(64) primary key,
  session_data json not null,
  created_at timestamp not null default current_timestamp
);
