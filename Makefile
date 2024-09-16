LOCAL_TAG:=$(shell date +"%Y-%m-%d-%H-%M")
LOCAL_IMAGE_NAME:=stock-close-price-forecasting:${LOCAL_TAG}

test:
	pytest tests/

quality_cheks:
	isort dags/
	black dags/
	pylint --recursive=y dags/

build: quality_cheks test
	docker build -t ${LOCAL_IMAGE_NAME} .

integration-test: build
	LOCAL_IMAGE_NAME=${LOCAL_IMAGE_NAME} bash integration-test/run.sh

publish: build integration-test
	LOCAL_IMAGE_NAME=${LOCAL_IMAGE_NAME} bash scripts/publish.sh

setup:
	pipenv install --dev
	pre-commit install
