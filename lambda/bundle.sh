#!/bin/bash
set -e
pip install -r requirements.txt -t package/
cp save_chat_history.py package/
cd package/
zip -r save_chat_history.zip .