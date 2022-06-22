#!/usr/bin/bash
cd $(dirname $(dirname $(realpath $0)))/src
poetry run python main.py
