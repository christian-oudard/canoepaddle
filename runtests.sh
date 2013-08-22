#! /bin/sh

rm -f .coverage  # For some reason this occasionally reveals more uncovered lines.
nosetests-3.3 --verbosity=2 --with-id --with-doctest --with-coverage --cover-tests \
    --cover-package canoepaddle \
    --cover-package tests \
    $@

passed=$?
if [ $passed -eq 0 ] ; then
    echo
    echo 'Running flake8...'
    flake8 canoepaddle/*.py tests/*.py examples/*.py

    echo
    echo 'Running examples...'
    for file in examples/*.py; do
        python $file > $file.svg
    done
fi
