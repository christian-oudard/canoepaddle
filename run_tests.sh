#! /bin/sh

rm -f .coverage  # For some reason this occasionally reveals more uncovered lines.
nosetests-3.3 --verbosity=2 --with-doctest --with-coverage --cover-tests \
    --cover-package canoepaddle \
    --cover-package test \
    $@

passed=$?
if [ $passed -eq 0 ] ; then
    flake8 canoepaddle/*.py tests/*.py examples/*.py
fi
