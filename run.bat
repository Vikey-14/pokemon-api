@echo off
rem Get filename input, default to main.py if nothing is passed
set FILE=%1
if "%FILE%"=="" set FILE=main

echo Activating virtual environment…
call venv\Scripts\activate.bat

echo Starting FastAPI server for %FILE%.py…
uvicorn %FILE%:app --reload

pause
