REQ_DIR        = requirements
PROD           = $(REQ_DIR)/production.txt
DEV            = $(REQ_DIR)/development.txt
DOCKER_IMAGE   = CodeCrafters/app

.PHONY: \
	install-prod install-dev \
	test \
	sync-dev sync-prod diff-dev diff-prod \
	update_database reset-db psql \
	docker-build docker-run up down logs \
	gis-up gis-down gis-restart gis-logs \
	secret_key


# ======================================================
# 🐍 PYTHON / DJANGO
# ======================================================

install-prod:
	pip install -r $(PROD)

install-dev:
	pip install -r $(DEV)

test:
	coverage run manage.py test
	coverage report
	coverage xml

secret_key:
	python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'


# ======================================================
# 📦 DEPENDENCIAS / REQUIREMENTS
# ======================================================

sync-dev:
	@echo "↪️  Guardando dependencias del entorno actual a develop.tmp.txt..."
	pip freeze | grep -v "pkg-resources" > $(REQ_DIR)/develop.tmp.txt
	@echo "✅ Revisar $(REQ_DIR)/develop.tmp.txt y reemplazar develop.txt si es correcto."

sync-prod:
	@echo "↪️  Guardando dependencias del entorno actual a production.tmp.txt..."
	pip freeze | grep -v "pkg-resources" > $(REQ_DIR)/production.tmp.txt
	@echo "✅ Revisar $(REQ_DIR)/production.tmp.txt y reemplazar production.txt si es correcto."

diff-dev:
	@echo "🔍 Comparando develop.txt con develop.tmp.txt..."
	@diff -u $(REQ_DIR)/develop.txt $(REQ_DIR)/develop.tmp.txt || echo "✔️ No hay diferencias."

diff-prod:
	@echo "🔍 Comparando production.txt con production.tmp.txt..."
	@diff -u $(REQ_DIR)/production.txt $(REQ_DIR)/production.tmp.txt || echo "✔️ No hay diferencias."


# ======================================================
# 🗄️ BASE DE DATOS
# ======================================================

update_database:
	@echo "🔄 Ejecutando migraciones..."
	python manage.py makemigrations
	python manage.py migrate

reset-db:
	@echo "⚠️  Limpiando base de datos completa (DROP + CREATE)..."
	bash scripts/reset_db.sh
	@echo "🔄 Ejecutando migraciones..."
	make update_database
	@echo "✨ Base de datos limpia y migraciones aplicadas."

psql:
	docker exec -it codecrafters_postgres psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)


# ======================================================
# 🐳 DOCKER
# ======================================================

docker-build:
	docker build -t $(DOCKER_IMAGE) .

docker-run:
	docker run -p 8000:8000 $(DOCKER_IMAGE)

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f


# ======================================================
# 🗺️ GIS / DOCKER COMPOSE ESPECIAL
# ======================================================

gis-up:
	docker compose -f docker-compose.gis.yml -p rimay_gis up -d

gis-down:
	docker compose -f docker-compose.gis.yml -p rimay_gis down

gis-restart:
	docker compose -f docker-compose.gis.yml -p rimay_gis down
	docker compose -f docker-compose.gis.yml -p rimay_gis up -d

gis-logs:
	docker compose -f docker-compose.gis.yml -p rimay_gis logs -f
