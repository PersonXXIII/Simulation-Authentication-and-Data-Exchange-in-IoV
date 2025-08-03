#!/bin/bash

# Compile Contacts
truffle compile

# Start Ganache CLI in the background and log output
ganache-cli > ganache.log 2>&1 &

# Wait for Ganache to initialize
sleep 10

# Run your Python main script
python main.py
