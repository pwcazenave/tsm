#!/bin/bash

cd $HOME/Code/tsm/app
while sleep 1; do
    . ../venv/bin/activate
    DEBUG=1 python3 main.py
done
