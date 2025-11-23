#!/bin/bash

DB_CONTAINER="gis_db_rimay"
DB_NAME="rimay_gis_db"
DB_USER="rimay_user"
DB_PASSWORD="rimay_secret_password"

echo "🔪 Matando conexiones activas en $DB_NAME..."
docker exec -e PGPASSWORD=$DB_PASSWORD $DB_CONTAINER psql -U $DB_USER -d postgres -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();
"

echo "🧨 Eliminando base de datos $DB_NAME..."
docker exec -e PGPASSWORD=$DB_PASSWORD $DB_CONTAINER psql -U $DB_USER -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"

echo "🛠️ Creando base de datos $DB_NAME..."
docker exec -e PGPASSWORD=$DB_PASSWORD $DB_CONTAINER psql -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME;"

echo "🗺️ Habilitando extensión PostGIS..."
docker exec -e PGPASSWORD=$DB_PASSWORD $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "CREATE EXTENSION IF NOT EXISTS postgis;"

echo "✨ Base de datos restaurada y limpia."
