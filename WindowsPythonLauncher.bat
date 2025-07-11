@echo off
setlocal

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Running the Python application...
call python src\main.py

echo Deactivating virtual environment...
call deactivate

echo Application has finished running.
pause
endlocal
