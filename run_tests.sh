#! /bin/sh

rm -f .coverage  # For some reason this occasionally reveals more uncovered lines.
nosetests-3.3 --verbosity=2 --with-doctest --with-coverage --cover-tests \
    --cover-package canoepaddle \
    --cover-package test \
    $@

passed=$?
if [ $passed -eq 0 ] ; then
    echo
    echo 'Running flake8...'
    flake8 canoepaddle/*.py tests/*.py examples/*.py

    echo
    echo 'Running examples...'
    for file in $(ls examples/); do
        echo
        echo examples/$file
        python examples/$file > /dev/null
    done
fi
