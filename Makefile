# Run `make` for a single test run
# or `make watch` for a continuous pipeline that reruns on changes.
#
# Comments to cyber.security@digital.cabinet-office.gov.uk
# This is free and unencumbered software released into the public domain.

.SILENT: test install upgrade watch checks Pipfile.lock

.PHONY: terraform

.EXPORT_ALL_VARIABLES:
CODE_DIR = lambda
PIPENV_PIPFILE = ${CODE_DIR}/Pipfile

watch:
	echo "✔️ Watch setup, save a python file to trigger test pipeline"
	pipenv run watchmedo shell-command --drop --ignore-directories --patterns="*.py;*.tf" --ignore-patterns="*#*" --recursive --command='clear && make -j 32 --no-print-directory test' .

clean:
	rm -rf __pycache__ .coverage *.egg-info .tox venv .pytest_cache htmlcov **/__pycache__ **/*.pyc .target *.zip **/.terraform
	echo "✔️ Cleanup of files completed!"

test: checks terraform
	pipenv run pytest -sqx --disable-warnings
	echo "✔️ Tests passed!"

checks:
	echo "⏳ running pipeline..."
	pipenv run isort --atomic -q ${CODE_DIR}
	pipenv run black -q ${CODE_DIR}
	pipenv run flake8 --max-line-length=88 ${CODE_DIR}  # in line with black
	pipenv run mypy --pretty ${CODE_DIR}
	echo "✔️ Checks pipeline passed!"

setup:
	set -e
	echo "⏳ installing..."
	pipenv install --dev
	echo "✔️ Pip dependencies installed!"


target_dir:
	rm -rf .target/
	mkdir .target

create_requirements.txt:
	pipenv run pip freeze > lambda/requirements.txt

add_deps: target_dir
	pipenv run python3 -m pip install -r lambda/requirements.txt -t .target

copy_groups_source:
	cp lambda/script.py .target/lambda_function.py

post_clean:
	rm -rf .target

build_google_groups_lambda: clean create_requirements.txt target_dir add_deps copy_groups_source
	cd .target; zip -9 get_data_for_google_groups.zip -r .
	mv .target/get_data_for_google_groups.zip .
	echo "✔️ Google groups lambda zip file built!"

zip:
	make build_google_groups_lambda
	make post_clean

terraform: terraform_fmt terraform_module_validate terraform_dev_validate terraform_prod_validate

terraform_fmt:
	@terraform fmt -check -diff -recursive terraform

terraform_module_validate: terraform/modules/ggroup-to-splunk/.terraform
	@cd terraform/modules/ggroup-to-splunk; AWS_DEFAULT_REGION=eu-west-2 terraform validate

terraform_dev_validate: terraform/deployments/dev/.terraform
	@cd terraform/deployments/dev; terraform validate

terraform_prod_validate: terraform/deployments/prod/.terraform
	@cd terraform/deployments/prod; terraform validate

terraform/modules/ggroup-to-splunk/.terraform:
	@cd terraform/modules/ggroup-to-splunk; terraform init -backend=false -reconfigure

terraform/deployments/dev/.terraform:
	@cd terraform/deployments/dev; terraform init -backend=false -reconfigure

terraform/deployments/prod/.terraform:
	@cd terraform/deployments/prod; terraform init -backend=false -reconfigure
