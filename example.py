import results

# load a csv (in this example, some airport data)
sheet = results.from_file("tests/FIXTURES/airports.csv")

# do general cleanup
sheet.standardize_spaces()
sheet.set_blanks_to_none()

# give the keys lowercase-with-underscore names to keep the database happy
cleaned = sheet.with_standardized_keys()

# Then, create a database:

# create a database
DB = "postgresql:///resultsdemo"

db = results.db(DB)

# create it if it doesn't exist
db.create_database()

# Then create a table for the data, automatically guessing the columns and creating a table to match.

# guess the column types
guessed = cleaned.guessed_sql_column_types()

# create a table for the data
create_table_statement = results.create_table_statement("data", guessed)

# create or auto-update the table structure in the database
# syncing requires a copy of postgres running locally with your current user set up as superuser
db.sync_db_structure_to_definition(create_table_statement, confirm=False)

# Then insert the data and freely query it.

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

# Create a pivot table, then print it as markdown or save it as csv.

# create a pivot table
pivot = query_result.pivoted()

# print the pivot table in markdown format
print(pivot.md)

# |   year |   Auckland |    Dubai |   Hong Kong |   Kuala Lumpur |   Singapore |
# |-------:|-----------:|---------:|------------:|---------------:|------------:|
# |   2010 |     288997 | 145527   |      404735 |       226787   |      529407 |
# |   2011 |     304628 | 169868   |      428990 |       244053   |      583921 |
# |   2012 |     312828 | 259444   |      400596 |       272093   |      614155 |
# |   2013 |     306783 | 257263   |      353895 |       272804   |      592886 |
# |   2014 |     309318 | 244776   |      330521 |       261438   |      620419 |
# |   2015 |     286202 | 263378   |      290292 |       252906   |      633862 |
# |   2016 |     285973 | 236419   |      309556 |       175858   |      614172 |
# |   2017 |     314405 | 226048   |      340216 |       199868   |      662505 |
# |   2018 |     126712 |  91611.2 |      134540 |        74667.5 |      250653 |


# save the table as a csv
pivot.save_csv("2010s_freight_sources_top5.csv")
