RM		:= rm -f
LN		:= ln -sf
MKDIR_P		:= mkdir -p

IDA_USER_DIR	?= ~/.idapro
USER_PLUGIN_DIR	:= $(IDA_USER_DIR)/plugins

PLUGIN_FILE	:= screenshot.py

.PHONY:
all:
	$(error There is no default target; see Makefile)

.PHONY: uninstall
uninstall:
	$(RM) $(USER_PLUGIN_DIR)/$(PLUGIN_FILE)

.PHONY: install
install: uninstall
	$(MKDIR_P) $(USER_PLUGIN_DIR)
	$(LN) $(shell pwd)/$(PLUGIN_FILE) $(USER_PLUGIN_DIR)
