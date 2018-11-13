
CREATE or replace FUNCTION films_f(d date,
def_t text default null,
def_d date default '2014-01-01'::date)
RETURNS TABLE(
    title character varying,
    release_date date
)
as $$select 'a'::varchar, '2014-01-01'::date$$
language sql;

CREATE OR REPLACE FUNCTION inc_f(integer) RETURNS integer AS $$
BEGIN
    RETURN $1 + 1;
END;
$$ LANGUAGE plpgsql stable;

CREATE OR REPLACE FUNCTION inc_f_out(integer, out outparam integer) returns integer AS $$
    select 1;
$$ LANGUAGE sql;

CREATE OR REPLACE FUNCTION inc_f_noargs() RETURNS void AS $$
begin
perform 1;
end;
$$ LANGUAGE plpgsql stable;
