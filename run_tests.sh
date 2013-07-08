#! /bin/sh

nosetests-3.3 --verbosity=2 --with-doctest --with-coverage --cover-tests \
    --cover-package canoepaddle \
    --cover-package test \
    $@

flake8 canoepaddle/*.py tests/*.py examples/*.py
