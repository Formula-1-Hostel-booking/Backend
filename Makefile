ifeq ($(OS),Windows_NT)
	create_env := fsutil file createnew .env 0
else
	create_env := touch .env
endif

.PHONY: init
init:
	$(create_env)
	pip install -r requirements.txt
	# create roles

.PHONY: start
start:
	flask run

.PHONY: run
run: start


.PHONY: migrate
migrate: 
	flask db migrate
	flask db upgrade

.PHONY: clean
clean: 
	python utils/clean.py

.PHONY: freeze
freeze: 
	pip freeze > requirements.txt

.PHONY: release
release:
	flask db init && flask db migrate && flask db upgrade
