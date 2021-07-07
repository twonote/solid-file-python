help:
	cat Makefile

init:
	pip install -r requirements.txt
	python3 -m pip install --upgrade pip
	python3 -m pip install --upgrade build
	python3 -m pip install --upgrade twine

test:
	PYTHONPATH=. pytest tests

build:
	python3 -m build

pypi:
	twine upload dist/*

testpypi:
	python3 -m twine upload --repository testpypi dist/*


