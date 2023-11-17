BEGIN;
create table if not exists transfer(name text primary key not null, 
                                    x text not null,
                                    y text not null,
                                    rfid text not null,
                                    dir text not null,
                                    group_tag text not null,
                                    coordinates text not null);

create table if not exists turn(name text primary key not null, 
                                x text not null,
                                y text not null,
                                rfid text not null,
                                dir text not null,
                                type text not null,
                                group_tag text not null,
                                coordinates text not null);

create table if not exists elevator(name text primary key not null, 
                                x text not null,
                                y text not null,
                                rfid text not null,
                                state text not null,
                                coordinates text not null);

create table if not exists standby(name text primary key not null, 
                                x text not null,
                                y text not null,
                                rfid text not null,
                                coordinates text not null);

create table if not exists speed(name text primary key not null, 
                                x text not null,
                                y text not null,
                                rfid text not null,
                                speed text not null,
                                coordinates text not null);

create table if not exists display(name text primary key not null, 
                                x text not null,
                                y text not null,
                                rfid text not null,
                                coordinates text not null);

create table if not exists other(name text primary key not null, 
                                x text not null,
                                y text not null,
                                rfid text not null,
                                type text not null,
                                coordinates text not null);
COMMIT;