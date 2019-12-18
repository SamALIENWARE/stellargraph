#!/bin/bash

set -xeo pipefail

# FIXME: testing
sed -i 's/tensorflow/tensorflow-gpu/g' requirements.txt setup.py

pip install -q --no-cache-dir -r requirements.txt -e .
py.test -ra --cov=stellargraph tests/ --doctest-modules --doctest-modules --cov-report=term-missing -p no:cacheprovider --junitxml=./"${BUILDKITE_BUILD_NUMBER}".xml
