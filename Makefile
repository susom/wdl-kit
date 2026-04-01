TARGET = install
VERSION = 1.9.7

.PHONY: clean docker install build publish

all: docker install

docker:
	docker build -t wdl-kit:$(VERSION) .

install:
	uv sync
	uv pip install -e .

build:
	uv build

publish: build
	uvx twine upload dist/*

clean:
	rm -rf dist/ .venv/ __pycache__

check: 
	$(MAKE) -C tests check

yaml: 
	$(MAKE) -C tests yaml

flush:
	$(info Flushing the WDL run and call caches)
	rm -rf _LAST 
	rm -rf 20[2-9][2-9][0-9][0-9][0-9][0-9]_*_*
	rm -rf cromwell-executions
	rm -rf cromwell-workflow-logs
	rm -rf ~/.cache/miniwdl/*
