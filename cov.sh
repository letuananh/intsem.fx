#!/bin/bash

python3 -m coverage run --source coolisf --branch -m unittest discover -s test
python3 -m coverage html
firefox htmlcov/index.html
