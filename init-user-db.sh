#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER reopt WITH PASSWORD 'reopt';
    ALTER USER reopt CREATEDB;
    CREATEDB reopt reopt;
    GRANT ALL PRIVILEGES ON DATABASE reopt TO reopt;
EOSQL
