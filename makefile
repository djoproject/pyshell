
#TODO make egg, quick install, exec, ...

PYTHON=python
TEST_TARGET=

.PHONY: all test clean exec devtest

clean:
	@find . -name "*~" -exec rm {} \;
	@find . -name "*.pyc" -exec rm {} \;
	@find . -name "__pycache__" -exec rmdir {} \;
	@find . -name ".Dstore" -exec rm {} \;

testall:
	@for f in `find ./pyshell -name "test.sh" -print0 | xargs -0 -n1 dirname | sort --unique`; do\
		echo "####### ENTERING testing directory $$f #######"; \
		cd $$f; \
		./test.sh || exit 1; \
		cd -; \
		echo "####### EXITING testing directory $$f #######"; \
	done

test:
	@if [ -z $(TEST_TARGET) ]; then\
		make testall ; \
	else \
		cd ./pyshell/$(TEST_TARGET)/test/ || exit 1 ; \
		./test.sh ; \
	fi
	
devtest:
	@chsum1=""; \
	while true; do \
		chsum2=`find ./pyshell/ -name "*.py" -exec md5sum {} \;`; \
		if [ "$$chsum1" != "$$chsum2" ] ; then \
		    reset; \
			make testall; \
			chsum1=$$chsum2; \
			echo ""; \
			echo "!!! THIS TOOLS WILL ITERATE EACH TIME A PYTHON FILE WILL BE UPDATED IN THE SOURCE DIRECTORY. CTRL-C TO EXIT !!!" ; \
		fi; \
		sleep 2; \
	done \
	
install:
	$(PYTHON) setup.py install

