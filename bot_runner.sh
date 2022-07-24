#!/bin/sh
cd "$(dirname "$0")";
CWD="$(pwd)"
echo $CWD
python3 telegram_client.py
