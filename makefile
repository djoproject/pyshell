
PYTHON=python
TEST_TARGET=

.PHONY: all test clean exec

clean:
	@find . -name "*~" -exec rm {} \;
	@find . -name "*.pyc" -exec rm {} \;
	@find . -name "__pycache__" -exec rmdir {} \;
	@find . -name ".Dstore" -exec rm {} \;

testall:
	@for f in `find ./pyshell -name "test.sh" -print0 | xargs -0 -n1 dirname | sort --unique`; do\
		echo "####### ENTERING testing directory $$f #######"; \
		cd $$f; \
		./test.sh || exit; \
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
	
install:
	$(PYTHON) setup.py install

