#!/usr/bin/env bash
# Lock pip modules
pipenv lock -r > requirements.txt
echo '' >> requirements.txt
echo '# dev packages' >> requirements.txt
pipenv lock -r --dev >> requirements.txt