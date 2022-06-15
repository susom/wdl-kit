TARGET = wdl-kit

TARGETDIR = $(WDL_DIR)/$(TARGET)/$(VERSION)
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

# Installs processed WDL files to WDL_DIR (might need root)
install: $(TARGETDIR) $(OBJECTS)

push: $(TARGET)
	docker tag $(IMAGE) $(REGISTRY)/$(IMAGE)
	docker push $(REGISTRY)/$(IMAGE)

$(TARGETDIR):
	install -m 0755 -d $(TARGETDIR)

$(TARGETDIR)/%.wdl: $(WDLSRC)/%.wdl $(TARGETDIR)
	envsubst < $< > $@
