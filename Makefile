clean:
	rm -rf build
	rm -rf .coverage\.*
	rm -rf .pytest_cache
	find . -name __pycache__i -o -name '*.pyc' -depth -exec rm -rf {} \;
	find ./src -not -name pyfluent -maxdepth 1 -mindepth 1 -exec rm -rf {} \;

sdist:
	python setup.py clean --all sdist bdist_wheel

tests:
	$(shell cat .env) python3 -B -mpytest --cov=pyfluent --cov-report=term-missing tests/src/

.PHONY: clean sdist tests
