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

create table skins.types (
	id serial primary key,
	name character varying not null
);

create table skins.inputs (
	id serial primary key,
	name character varying not null
);

create table skins.type_inputs (
	id serial primary key,
	type_id int not null,
	input_id int not null,
	foreign key (type_id) references skins.types(id)
	on update cascade
	on delete cascade,
	foreign key (input_id) references skins.inputs(id)
	on update cascade
	on delete cascade
);

CREATE TABLE skins.core
(
    id serial primary key,
    type_id int not null,
    name character varying COLLATE pg_catalog."default" NOT NULL,
    points integer NOT NULL,
	foreign key (type_id) references skins.types(id)
	on update cascade
	on delete cascade
);

create table skins.input_values (
	id serial primary key,
	skin_id int not null,
	input_id int not null,
	value character varying not null,
	foreign key (skin_id) references skins.core(id)
	on update cascade
	on delete cascade,
	foreign key (input_id) references skins.inputs(id)
	on update cascade
	on delete cascade
);


create table IF NOT EXISTS accounts (
	id serial primary key,
	username character varying not null unique,
	email character varying not null unique,
	password bytea NOT NULL,
	first_name character varying not null,
	last_name character varying not null,
    points int not null default 0,
    skin_id int default 1,
    created_time timestamp without time zone NOT NULL DEFAULT now(),
	last_updated_time timestamp without time zone NOT NULL DEFAULT now(),
    foreign key (skin_id) references skins(id) on update cascade on delete set null
);

create table IF NOT EXISTS scores (
	id serial primary key, -- change this to bigserial
	game_id int not null,
	account_id int not null,
	score int not null,
	score_date timestamp without time zone not null default now(),
	foreign key (game_id) references games(id) on update cascade on delete cascade,
	foreign key (account_id) references accounts(id) on update cascade on delete cascade
);

CREATE TABLE IF NOT EXISTS public.score_updates
(
    id bigserial primary key,
    account_id integer NOT NULL,
    score_id integer NOT NULL,
    game_id integer NOT NULL,
    current_game_rank integer NOT NULL,
    update_time timestamp without time zone NOT NULL DEFAULT now(),
    CONSTRAINT score_updates_account_id_fkey FOREIGN KEY (account_id)
        REFERENCES public.accounts (id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

create table point_updates (
    id bigserial primary key,
    account_id integer NOT NULL,
    point_amount integer NOT NULL,
	update_type character varying not null,
	skin_id int,
	score_update_id int,
    update_time timestamp without time zone NOT NULL DEFAULT now(),
    foreign key (account_id) references accounts(id)
    on update cascade on delete cascade,
	foreign key (skin_id) references skins.core(id)
	on update cascade on delete set null,
	foreign key (score_update_id) references score_updates(id)
	on update cascade on delete set null
);




CREATE TABLE IF NOT EXISTS public.user_skins
(
    id serial primary key,
    account_id integer NOT NULL REFERENCES accounts (id),
    skin_id integer NOT NULL REFERENCES skins.core(id),
    purchase_date timestamp without time zone NOT NULL DEFAULT now()
);



--- VIEWS

create view skins.skins_view as
select s.id, s.name, s.points, t.name type, jsonb_object_agg(i.name, sv.value) AS data
from skins s
join skin_types t on s.type_id = t.id
join skin_type_inputs st on t.id = st.type_id
join skin_inputs i on i.id = st.input_id
join skin_input_values sv on s.id = sv.skin_id and sv.input_id = i.id
group by s.name, s.points, t.name, s.id
order by s.points, t.name, s.id;

create view profile_view as
with score_ranks as (
	select account_id,
		game_id, 
		score,
		row_number() over (partition by game_id order by score desc, score_date desc) "rank"
	from scores
)
select a.id, username, created_time, points, num_top10, json_agg(json_build_object('score', score, 'rank', s.rank, 'game_name', g.title)) as ranks
from (
	select min(rank) "rank", game_id, account_id
	from score_ranks s
	where rank <= 3
	group by game_id, account_id
) s
join score_ranks sr on sr.game_id = s.game_id and sr.account_id = s.account_id and sr.rank = s.rank
join games g on g.id = s.game_id
join (
	select account_id, 
		sum(case when rank <= 10 then 1 else 0 end) as num_top10
	from score_ranks	
	group by account_id
) s2 on s.account_id = s2.account_id
join accounts a on a.id = s.account_id
group by a.id, username, created_time, num_top10, points


--- functions

CREATE OR REPLACE FUNCTION update_scores(
	_account_id integer,
	_game_id integer,
	_score integer)
    RETURNS TABLE(high_scores json, points_added integer, score_rank integer) 
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
DECLARE
    _save_score BOOLEAN;
    _inserted_score_id INTEGER;
    _points_added integer := 0;
    _score_rank integer := null;
	_inserted_score_update_id integer;
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

    -- 2. Save the score if it qualifies and update account points
    IF _save_score THEN
        INSERT INTO scores (account_id, game_id, score)
        VALUES (_account_id, _game_id, _score)
        RETURNING id INTO _inserted_score_id;
	END IF;
	drop table if exists top10scores;

	create temp table top10scores AS
	SELECT id, score, score_date, account_id, 'top10'::character varying AS score_type
	FROM scores s
	WHERE game_id = _game_id
	ORDER BY score desc, score_date desc
	LIMIT 10;
	
	IF _save_score THEN
        select p.score_ranked into _score_rank
        from 
        (
            SELECT id, row_number() over(order by score desc, score_date desc) as score_ranked
            from top10scores
        ) p
        where id = _inserted_score_id;

        select 11 - _score_rank into _points_added;

        -- if they get the top score, award 15 points instead of 10
        select case when _points_added = 10 then 15 else _points_added into _points_added end;

        update accounts 
        set points = points + _points_added,
            last_updated_time = now()
        where id = _account_id;

        insert into score_updates (account_id, score_id, game_id, current_game_rank)
        values (_account_id, _inserted_score_id, _game_id, _score_rank)
		returning id into _inserted_score_update_id;

		insert into point_updates (account_id, point_amount, update_type, score_update_id)
		values (_account_id, _points_added, 'game points', _inserted_score_update_id);
    END IF;

    -- 3. Return the results
    RETURN QUERY
    SELECT json_agg(
            json_build_object('username', a.username, 'score', s.score, 'score_date', s.score_date::date, 'score_type', s.score_type, 'current_score', s.id = _inserted_score_id)
            ORDER BY s.score DESC, s.score_date deSC
        ) high_scores, 
        _points_added as points_added, _score_rank as score_rank
    FROM (
        (SELECT * from top10scores)

        UNION ALL

        (SELECT s.id, s.score, s.score_date, s.account_id, 'top3'::character varying AS score_type
        FROM scores s
        WHERE s.game_id = _game_id
          AND s.account_id = _account_id
        ORDER BY s.score desc
        LIMIT 3)
    ) AS s
    JOIN accounts a ON a.id = s.account_id;

END;
$BODY$;

CREATE OR REPLACE FUNCTION skins.purchase_skin(_account_id int, _skin_id int)
RETURNS void
LANGUAGE 'plpgsql'
as $$
declare 
_skin_points int;
_purchaseable bool;
BEGIN
    select points into _skin_points from skins.core where id = _skin_id;
	select _skin_points is not null and points >= _skin points into _purchaseable;

	if purchaseable then
     	update accounts set points = points - _skin_points where id = _account_id;
        
		insert into point_updates (account_id, point_amount, update_type, skin_id) 
		values (_account_id, -_skin_points, 'skin purchase', _skin_id);
		
        insert into user_skins (account_id, skin_id) values (_account_id, _skin_id);
	end if;
END;
$$