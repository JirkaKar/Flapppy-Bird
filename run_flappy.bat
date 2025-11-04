@echo off
pushd "%~dp0"
call ".venv\Scripts\activate"
python flappy_bird.py
popd
