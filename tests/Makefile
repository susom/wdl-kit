.PHONY: clean yaml

all: yaml

rwildcard=$(foreach d,$(wildcard $(1:=/*)),$(call rwildcard,$d,$2) $(filter $(subst *,%,$2),$d))
YAML_FILES := $(call rwildcard,.,*.yaml)
YAML_WDL := $(patsubst %,%.wdl,$(join $(dir $(YAML_FILES)),$(patsubst %,.%,$(notdir $(YAML_FILES)))))

.%.yaml.wdl: %.yaml
	yaml2wdl $< $@

yaml: $(YAML_WDL)

clean:
	find . -name '.*.yaml.wdl' -delete

flush:
	$(info Flushing the WDL run and call caches)
	rm -rf _LAST 
	rm -rf 20[2-9][2-9][0-9][0-9][0-9][0-9]_*_*
	rm -rf cromwell-executions
	rm -rf cromwell-workflow-logs
	rm -rf ~/.cache/miniwdl/*

check: yaml
	miniwdl check --strict --suppress UnverifiedStruct,Deprecated *.wdl 
