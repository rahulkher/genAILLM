@echo off

setlocal
set "ollama_path="

:: Check if Ollama is installed
for /F "tokens=*" %%i in ('where ollama 2^>nul') do (
    set "ollama_path=%%i"
)

if not defined ollama_path (
    echo Ollama is not installed or not in the system PATH.
    echo Make sure you have ollama installed and added to system PATH
    goto end
)

:: Check if Ollama is running
set process_name=ollama.exe
tasklist /FI "IMAGENAME eq %process_name%" | find /I "%process_name%" >nul 2>&1
if "%ERRORLEVEL%"=="0" (
    echo Ollama is already running.
) else (
    echo Ollama is not running. Starting Ollama server
    start "Ollama" cmd /c "ollama serve
)

endlocal

setlocal
set "python_path="
set "venv_path=.genai\Scripts\activate.bat"
set "streamlit_app_path=app.py"

for /F "tokens=*" %%i in ('where python 2^>nul') do (
    	set "python_path=%%i"
	)
	if defined python_path (
    		echo Found Python installed at -> %python_path%.
		echo Starting Application....
		call .genai\Scripts\activate.bat

		cd D:\development\genAILLM

		streamlit run app.py
		
	) else (
    		echo Python is not installed. Please install python.
	)

pause
:end	
endlocal 


