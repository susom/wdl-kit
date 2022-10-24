TARGET = install
VERSION=1.3.0-slimaye9

.PHONY: clean docker pip

all: docker install

docker:
	docker build -t wdl-kit:$(VERSION) .

install: 
	pip3 install pybuilder==0.13.7
	pyb install 
	pip3 install target/dist/stanford-wdl-kit-$(VERSION)/dist/stanford-wdl-kit-$(VERSION).tar.gz
	pip install "cloud-sql-python-connector[pg8000]"
	pip install sqlalchemy
	pip install pg8000
	
clean:
	pyb clean
	rm -rf __pycache__
