.PHONY: install-requirements build-seprate build-bundle

all: install-requirements build-bundle

install-requirements:
	pip install -r requirements.txt

build-seprate:
	python -m PyInstaller --windowed --uac-admin --add-binary "IPMICFG-Win.exe;." --onefile supermicro-x-series.py

build-bundle:
	python -m PyInstaller fan-lord.spec
