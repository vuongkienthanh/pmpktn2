#!/usr/bin/bash
cd $(dirname $(dirname $(realpath $0)))
poetry run python src/main.py
