RUN=docker-compose run --rm partial pipenv run

all:
	docker-compose build

run:
	docker-compose run --service-ports --rm partial

run-all:
	docker-compose up project

shell:
	docker-compose run --rm partial /bin/bash

test:
	$(RUN) pytest -x -vvv --pdb

report:
	$(RUN) pytest --cov=apps/ -x --pdb

report-html:
	$(RUN) pytest --cov-report html --cov=apps/ -x --pdb

sort:
	$(RUN) isort --recursive apps project

check-sort:
	$(RUN) isort --recursive --diff apps project

stop:
	docker-compose down

extract:
	docker-compose run --rm packages ./extract_packages.sh

lock:
	docker-compose run --rm packages ./lock.sh