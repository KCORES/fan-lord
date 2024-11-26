build-seprate-exe:
	python -m PyInstaller --windowed --uac-admin --add-binary "IPMICFG-Win.exe;." --onefile supermicro-x-series.py

build-one-exe:
	python -m PyInstaller fan-lord.spec
