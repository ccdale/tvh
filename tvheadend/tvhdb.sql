create table files (
    id integer auto increment,
    name text,
    size integer null,
    hash text,
    status integer null default 0
);
create index filename_idx on files(name);
create index filestatus_idx on files(name, status);

create table paths (
    id integer auto increment,
    name text
);
create index pathname_idx on paths(name);

create table filepathmap (
    id integer auto increment,
    fileid integer not null,
    pathid integer not null
);
