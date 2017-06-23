PYTHON=$(shell which python)

.PHONY: setup
setup: 
	cd lacosmic/; $(PYTHON) init_setup_lacosmic.py 
	cd ../../
	$(PYTHON) setup.py develop
