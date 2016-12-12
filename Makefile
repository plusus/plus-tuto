all:
	echo '### MAKING CORE ###'
	$(MAKE) -C core
	echo '### MAKING FRONTEND ###'
	$(MAKE) -C center-frontend
test:
	echo '### TEST CORE ###'
	$(MAKE) test -C core
	echo '### TEST FRONTEND ###'
	$(MAKE) test -C center-frontend
	echo '### TEST LIBTUTO ###'
	cd tuto-file-handling && python3 run_tests.py
