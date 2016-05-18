develop:
	python setup.py develop --user

install:
	python setup.py install --user

clean-pyc:
	find . -name '*.pyc' | xargs -I{} rm {}
