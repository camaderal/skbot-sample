# Variables
APP_NAME = "skbot"
DEPLOY_DIR = dist/$(APP_NAME)
PACKAGE_NAME = $(APP_NAME)-package.zip
SRC_MODULE_DIR="src/semantic_kernel_chatbot"

APP_SERVICE_NAME="appservice-skbot-christeena"
RESOURCE_GROUP="rg-skbot-christeena"

.PHONY: clean build package all lint-all check-all

# Step 1: Clean previous artifacts
clean:
	rm -rf dist
	rm -f $(PACKAGE_NAME)

# Step 2: Build deployable folder
build:
	mkdir -p $(DEPLOY_DIR)
	rsync -av --exclude='__pycache__' --exclude='*.pyc' $(SRC_MODULE_DIR)/ $(DEPLOY_DIR)/
	cp requirements.txt $(DEPLOY_DIR)/

# Step 3: Zip the contents
package: build
	cd dist && zip -r $(PACKAGE_NAME) $(APP_NAME)

# One-shot command
all: clean package

lint-all:
	black .
	ruff check --fix .
	mypy .
	pydoclint .
	pymarkdown scan .
	yamllint . -c .yamllint.yaml

check-all:
	black . --check
	ruff check .
	mypy .
	pydoclint .
	pymarkdown scan .
	yamllint . -c .yamllint.yaml

