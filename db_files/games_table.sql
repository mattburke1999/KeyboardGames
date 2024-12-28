CREATE TABLE IF NOT EXISTS games
(
    id serial primary key,
    title character varying  NOT NULL,
    title_style character varying  NOT NULL DEFAULT 'dot open',
	title_color character varying not null,
	bg_color1 character varying not null,
	bg_color2 character varying not null,
	bg_rot int not null default 45,
    abbrev_name character varying  NOT NULL,
    duration double precision NOT NULL DEFAULT 60,
    basic_circle_template boolean NOT NULL DEFAULT true,
    last_updated_time timestamp without time zone DEFAULT now()
);

create table IF NOT EXISTS accounts (
	id serial primary key,
	username character varying not null unique,
	email character varying not null unique,
	password bytea NOT NULL,
	first_name character varying not null,
	last_name character varying not null,
    created_time timestamp without time zone NOT NULL DEFAULT now(),
	last_updated_time timestamp without time zone NOT NULL DEFAULT now()
);

create table IF NOT EXISTS scores (
	id serial primary key,
	game_id int not null,
	account_id int not null,
	score int not null,
	score_date timestamp without time zone not null default now(),
	foreign key (game_id) references games(id) on update cascade on delete cascade,
	foreign key (account_id) references accounts(id) on update cascade on delete cascade
)