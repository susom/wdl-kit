TARGET = wdl-kit
VERSION = 1.0.0
REGISTRY = UNSET
WDL_DIR = /usr/local

export WDL_KIT_VERSION = $(VERSION)

TARGETDIR = /usr/local/$(TARGET)/$(VERSION)
WDLSRC = src/main/wdl

WDL = $(wildcard $(WDLSRC)/*.wdl)
OBJECTS = $(patsubst $(WDLSRC)/%.wdl, $(TARGETDIR)/%.wdl, $(WDL))

.PHONY: clean

all: $(TARGET)

$(TARGET): 
	DOCKER_BUILDKIT=0 COMPOSE_DOCKER_CLI_BUILD=0 pyb install

clean:
	pyb clean
	rm -rf __pycache__

# Installs locally as executables
pipinstall: $(TARGET)
	pip install target/dist/$(TARGET)-$(VERSION)

# Installs processed WDL files to WDL_DIR
install: $(TARGETDIR) $(OBJECTS)

$(TARGETDIR):
	install -m 0755 -d $(TARGETDIR)

$(TARGETDIR)/%.wdl: $(WDLSRC)/%.wdl $(TARGETDIR)
	envsubst < $< > $@
