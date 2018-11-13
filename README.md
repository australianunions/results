# Don't get mad, get `results`

Tabular data and SQL for people who don't have time to faff about.

Move between xlsx, xls, csv, python, postgres and back with ease.

Features:

- Zero-boilerplate database creating, connecting and querying.
- Loading/tidying/transforming csv and excel data.
- Autodetect column types, load your data with little or no manual specification.
- Powerful multi-column, multi-order keyset paging of database results.
- Schema syncing.

Limitations

- Python 3.6+, PostgreSQL 10+ only. Many features will work with other databases, but many won't. Just use Postgres!

# Installation

[`results` is on PyPI](https://pypi.org/project/results). Install it with `pip` or any of the (many) Python package managers.

## Scenario

Somebody gives you a messy csv or excel file. You need to load it, clean it up, put it into a database, query it, make a pivot table from it, then send the pivot table to somebody as a csv.

`results` is here to get this sort of thing done quickly and with minimum possible fuss.

Let's see.

First, load and clean:

```python
import results

# load a csv (in this example, some airport data)
sheet = results.from_file("airports.csv")

# do general cleanup
sheet.standardize_spaces()
sheet.set_blanks_to_none()

# give the keys lowercase-with-underscore names to keep the database happy
cleaned = sheet.with_standardized_keys()
```

Then, create a database:

```python
# create a database
DB = "postgresql:///example"

db = results.db(DB)

# create it if it doesn't exist
db.create_database()
```

Then create a table for the data, automatically guessing the columns and creating a table to match.

```python
# guess the column types
guessed = cleaned.guessed_sql_column_types()

# create a table for the data
create_table_statement = results.create_table_statement("data", guessed)

# create or auto-update the table structure in the database
# syncing requires a copy of postgres running locally with your current user set up as superuser
db.sync_db_structure_to_definition(create_table_statement, confirm=False)
```

Then insert the data and freely query it.

```python
# insert the data. you can also do upserts with upsert_on!
db.insert("data", cleaned)

# show recent airfreight numbers from the top 5 airports
# ss means "single statement"
query_result = db.ss(
    """
with top5 as (
    select
        foreignport, sum(freight_in_tonnes)
    from
        data
    where year >= 2010
    group by
        foreignport
    order by 2 desc
    limit 5
)

select
    year, foreignport, sum(freight_in_tonnes)
from
    data
where
    year >= 2010
    and foreignport in (select foreignport from top5)
group by 1, 2
order by 1, 2

"""
)
```

Create a pivot table, then print it as markdown or save it as csv.

```python
# create a pivot table
pivot = query_result.pivoted()

# print the pivot table in markdown format
print(pivot.md)
```

Output:

```
|   year |   Auckland |    Dubai |   Hong Kong |   Kuala Lumpur |   Singapore |
|-------:|-----------:|---------:|------------:|---------------:|------------:|
|   2010 |     288997 | 145527   |      404735 |       226787   |      529407 |
|   2011 |     304628 | 169868   |      428990 |       244053   |      583921 |
|   2012 |     312828 | 259444   |      400596 |       272093   |      614155 |
|   2013 |     306783 | 257263   |      353895 |       272804   |      592886 |
|   2014 |     309318 | 244776   |      330521 |       261438   |      620419 |
|   2015 |     286202 | 263378   |      290292 |       252906   |      633862 |
|   2016 |     285973 | 236419   |      309556 |       175858   |      614172 |
|   2017 |     314405 | 226048   |      340216 |       199868   |      662505 |
|   2018 |     126712 |  91611.2 |      134540 |        74667.5 |      250653 |
```

Save the table as a csv:

```python
pivot.save_csv("2010s_freight_sources_top5.csv")
```

## Design philosophy

- Avoid boilerplate at all costs. Make it as simple as possible but no simpler.

- Don't reinvent the wheel: `results` uses sqlalchemy for database connections, existing excel parsing libraries for excel parsing, etc etc. `results` brings it all together, sprinkles some sugar on top, and puts it at your fingertips.

- Eat your own dogfood: We use this ourselves every day.

## Documentation

This README.md is currently all there is :( But we'll add more soon, we promise!

## Credits

- [Rob](https://github.com/djrobstep)
- [Jason](https://github.com/jasongi)
- [Nick](https://github.com/nmcl23)

## Contributions

Yes please!
