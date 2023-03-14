import oracledb
import os

un = "UBD3722"
pw = "Xbox36098"
host = "afrodita.lcc.uma.es"
sid = "APOLO"

connection = oracledb.connect(user=un, password=pw, host=host, sid=sid)
cursor = connection.cursor()

query = """
INSERT INTO RECIPES (RECIPE_ID, RECIPE_NAME)
VALUES(1, 'Taco')
        """
cursor.execute(query)

query = """
SELECT * FROM RECIPES"""

rows = cursor.execute(query)
for row in rows:
    print(row)

connection.commit()

cursor.close()

connection.close()




with oracledb.connect(user=un, password=pw, host=host, sid=sid) as connection:
    with connection.cursor() as cursor:
        sql = """select sysdate from dual"""
        for r in cursor.execute(sql):
            print(r)
