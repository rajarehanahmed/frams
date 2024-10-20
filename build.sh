#!/bin/bash

# Update packages and install cmake
apt-get update && apt-get install -y cmake

# Install Python dependencies
pip install -r requirements.txt