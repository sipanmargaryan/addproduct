# AddProduct

## Python3.6 Django2 Celery4.2 Postgres10 Redis3.2

## Setup

Make sure you have `docker` and `docker-compose` installed on your machine.

Create `.env` file using `.env_template`.

Commands

To build the project

    make

To run the project

    make run

To jump into container

    $ make shell
    root@<containerid>:/project#

To setup git hooks

    python3 -m pip install --user -r requirements/requirements-test.txt
    ln -s ../../pre-commit .git/hooks/pre-commit

To run tests

    make test

To see coverage report

    make report
    
To build coverage report html

    make report-html

To check import ordering

    make check-sort
    
To fix import ordering

    make sort

To stop running containers

    make stop