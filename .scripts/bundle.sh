#!/bin/bash
set -e
pip install --upgrade pip
pip install --target ./python -r requirements.txt
zip -r ../lambda.zip .