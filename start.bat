@echo off
cd cd /d %~dp0
pip install -r src/requirements.txt
python bootstrap.py