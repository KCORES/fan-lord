.PHONY: install-requirements build-bundle

all: install-requirements build-bundle

install-requirements:
	pip install -r requirements.txt
build-bundle:
	python -m PyInstaller fan-lord.spec
