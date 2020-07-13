# Run `make` for a single test run
# or `make watch` for a continuous pipeline that reruns on changes.
#
# Comments to cyber.security@digital.cabinet-office.gov.uk
# This is free and unencumbered software released into the public domain.

.SILENT: test install upgrade watch checks Pipfile.lock

clean:
	rm -rf __pycache__ .coverage *.egg-info .tox venv .pytest_cache htmlcov **/__pycache__ **/*.pyc .target setup.cfg Pipfile Pipfile.lock *.zip
	echo "✔️ Cleanup of files completed!"

test: checks
	pipenv run pytest -sqx --disable-warnings
	echo "✔️ Tests passed!"

checks: Pipfile.lock
	echo "⏳ running pipeline..."
	set -e
	pipenv run isort --atomic -q .
	pipenv run black -q .
	pipenv run flake8 --max-line-length=88 .  # in line with black
	pipenv run mypy --pretty .
	echo "✔️ Checks pipeline passed!"

Pipfile.lock:
	set -e
	echo "⏳ installing..."
	pipenv install flake8 mypy watchdog pyyaml argh pytest isort
	pipenv install --pre black
	pipenv run mypy_boto3 -q && echo  "✔️ mypy_boto3 stubs installed!"!! || true # ignored if not installed
	echo "✔️ Pip dependencies installed!"

upgrade:
	set -e
	wget -q https://raw.githubusercontent.com/alphagov/cyber-security-tools/master/python/Makefile -O Makefile
	echo "✔️ Upgraded Makefile!"

watch:
	echo "✔️ Watch setup, save a python file to trigger test pipeline"
	pipenv run watchmedo shell-command --drop --ignore-directories --patterns="*.py" --ignore-patterns="*#*" --recursive --command='clear && make --no-print-directory test' .

target_dir:
	rm -rf .target/
	mkdir .target

create_requirements.txt:
	pipenv run pip freeze > requirements/requirements.txt

add_deps: target_dir
	pipenv run python3 -m pip install -r requirements/requirements.txt -t .target

copy_groups_source:
	cp script.py .target/lambda_function.py

build_google_groups_lambda: clean create_requirements.txt target_dir add_deps copy_groups_source
	cd .target; zip -9 get_data_for_google_groups.zip -r . 
	mv .target/get_data_for_google_groups.zip .
	echo "✔️ Google groups lambda zip file built!"

zip:
	make build_google_groups_lambda\