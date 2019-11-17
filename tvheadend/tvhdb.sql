create table files (
    id integer auto increment,
    name text not null,
    size integer null default 0,
    hash text null default "",
    status integer null default 0
);
create index filename_idx on files(name);
