CREATE TABLE IF NOT EXISTS public.games
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
)

