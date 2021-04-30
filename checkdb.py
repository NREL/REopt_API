import psycopg2
import os
from keys import *
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


dbname = os.getenv("DB_NAME")
dbhost = dev_database_host
dbuser = dev_user
dbpass = dev_user_password
env = os.getenv('APP_ENV')

if env == 'staging':
    dbhost = staging_database_host
    dbuser = staging_user
    dbpass = staging_user_password
elif env == 'production':
    dbhost = prod_database_host
    dbuser = production_user
    dbpass = production_user_password



conn = psycopg2.connect(
    host=dbhost,
    user=dbuser,
    password=dbpass
)

conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

cur = conn.cursor()
dbnames = []
cur.execute("SELECT datname FROM pg_database;")
for dbn in cur.fetchall():
    dbnames.append(dbn)

if dbname not in dbnames:
    cur.execute("CREATE DATABASE {};".format(dbname))
    conn.commit()

cur.close()
conn.close()
