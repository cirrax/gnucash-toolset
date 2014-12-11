
all:
	python setup.py build

install:
	python setup.py install

clean:
	python setup.py clean
	rm -rf build
	rm -rf develop
	rm -rf dist
	rm -rf openstackcirrax.egg-info

test:
	python setup.py test

develop:
	python -m virtualenv develop
	develop/bin/python setup.py develop

