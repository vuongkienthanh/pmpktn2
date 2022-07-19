#!/usr/bin/bash
cd $(dirname $(dirname $(realpath $0)))
poetry run python -OO src/main.py