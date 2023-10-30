TARGET = install
VERSION = 1.7.0

.PHONY: clean docker pip

all: docker install

docker:
	docker build -t wdl-kit:$(VERSION) .

install: 
	pip install -r requirements.txt
	pip3 install target/dist/stanford-wdl-kit-$(VERSION)/dist/stanford-wdl-kit-$(VERSION).tar.gz
	
clean:
	pyb clean
	rm -rf __pycache__

check: 
	$(MAKE) -C tests check

yaml: 
	$(MAKE) -C tests yaml
