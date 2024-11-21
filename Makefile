TARGET = install
VERSION = 1.9.6

.PHONY: clean docker pip

all: docker install

docker:
	docker build -t wdl-kit:$(VERSION) .

install: 
	pip install -r requirements.txt
	pip3 install target/dist/stanford-wdl-kit-$(VERSION)/dist/stanford_wdl_kit-$(VERSION).tar.gz
	
clean:
	pyb clean
	rm -rf __pycache__

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
