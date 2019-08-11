vfn=tvheadend/__init__.py
dev:
ifeq ($(strip $(VIRTUAL_ENV)),)
	@echo "You need to be in a virtual environment"
else
	buildn=$$(sed -n 's/buildv = \([0-9]\+\)/\1/p' $(vfn) );\
		   buildn=$$(( buildn + 1 ));\
		   sed -i "/buildv =/s/[0-9]\+/$$buildn/" $(vfn)
	git add $(vfn)
	git commit -m "bumping build version"
	pip install -e .
endif

install:
	pip3 install . --user

uninstall:
	pip3 uninstall .


sdist:
	rm -rf dist/
	rm -rf build/
	python setup.py sdist

bdist: sdist
	python setup.py bdist_wheel

upload: bdist
	twine upload --repository testpypi dist/*

pypi: bdist
	twine upload dist/*
