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

CREATE OR REPLACE FUNCTION update_scores(
	_account_id integer,
	_game_id integer,
	_score integer)
    RETURNS TABLE(username character varying, score integer, score_date date, score_type character varying, current_score boolean) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
DECLARE
    _save_score BOOLEAN;
    _inserted_score_id INTEGER;
BEGIN
    -- 1. Check if the score qualifies for saving
    SELECT 
        count(top10.score) < 10 or _score > COALESCE(MIN(top10.score), 0) OR count(top3.score) < 3 or _score > COALESCE(MIN(top3.score), 0)
    INTO _save_score
    FROM (
        SELECT s.score
        FROM scores s
        WHERE s.game_id = _game_id
        ORDER BY s.score DESC
        LIMIT 10
    ) AS top10,
    (
        SELECT s.score
        FROM scores s
        WHERE s.account_id = _account_id
          AND s.game_id = _game_id
        ORDER BY s.score DESC
        LIMIT 3
    ) AS top3;

    -- 2. Save the score if it qualifies
    IF _save_score THEN
        INSERT INTO scores (account_id, game_id, score)
        VALUES (_account_id, _game_id, _score)
        RETURNING id INTO _inserted_score_id;
    END IF;

    -- 3. Return the results
    RETURN QUERY
    SELECT a.username, s.score, s.score_date::date, s.score_type, s.id = _inserted_score_id AS current_score
    FROM (
        (SELECT s.id, s.score, s.score_date, s.account_id, 'top10'::character varying AS score_type
        FROM scores s
        WHERE s.game_id = _game_id
        ORDER BY s.score asc
        LIMIT 10)

        UNION ALL

        (SELECT s.id, s.score, s.score_date, s.account_id, 'top3'::character varying AS score_type
        FROM scores s
        WHERE s.game_id = _game_id
          AND s.account_id = _account_id
        ORDER BY s.score asc
        LIMIT 3)
    ) AS s
    JOIN accounts a ON a.id = s.account_id;

END;
$BODY$;