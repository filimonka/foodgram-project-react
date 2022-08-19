import csv
import sqlite3

con = sqlite3.connect(
    '/home/filimonka/dev/foodgram-project-react/backend/db.sqlite3'
)
cur = con.cursor()

with open(
    '/home/filimonka/dev/foodgram-project-react/data/ingredients.csv', 'r',
    encoding="utf8"
) as f:
    dr = csv.DictReader(
        f, fieldnames=('name', 'measurement_unit'), delimiter=","
    )
    to_db = [i for i in dr]
print(to_db)
cur.executemany(
    "INSERT INTO recipe_ingredient (name, measurement_unit) VALUES (:name, :measurement_unit);",
    to_db
    )
con.commit()
con.close()
