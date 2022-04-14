TARGET = wdl-utils
VERSION = 0.1.0

.PHONY: clean

all: $(TARGET)

$(TARGET): 
	DOCKER_BUILDKIT=0 COMPOSE_DOCKER_CLI_BUILD=0 pyb

clean:
	pyb clean
	rm -rf __pycache__

install:
	DOCKER_BUILDKIT=0 COMPOSE_DOCKER_CLI_BUILD=0 pyb install

pipinstall: install
	pip install target/dist/$(TARGET)-$(VERSION)
