TARGET = wdl-kit
VERSION=1.2.0

.PHONY: clean docker pip

all: docker install

docker:
	docker build -t wdl-kit:$(VERSION) .

install: 
	pip3 install pybuilder==0.13.5
	pyb install 
	pip3 install target/dist/wdl-kit-$(VERSION)/dist/wdl-kit-$(VERSION).tar.gz

clean:
	pyb clean
	rm -rf __pycache__
