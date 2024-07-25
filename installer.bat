@echo off
setlocal

rem Set the root folder and destination folder
set "rootFolder=%cd%"
set "destFolder1=C:\Users\%USERNAME%\"
set "destFolder2=C:\Users\%USERNAME%\AppData\Local"

rem set the executable filenames
set "ollamaexe=ollama.exe"
set "pythonexe=python.exe"

rem Function to check if path is already in PATH variable
:check_and_add_to_path
set "searchPath=%~1"
echo %PATH% | findstr /i /c:%searchPath% > nul

if %errorlevel% == 0(
    echo Path %searchPath% already a PATH variable
) else (
    echo Adding %searchPath% to PATH variable
    setx PATH "%PATH%;%searchPath%"
)
goto :eof

rem Loop through all subfolders
for /d %%d in ("%CD%\*") do(
    rem Get folder name
    for %%f in ("%%d") do set "folderName=%%~nxf"

    rem Check the foldername and copy to specific destinantion
     if /i "%folderName%"==".ollama"(
        if not exist "%destinationFolder1%\%folderName%"(
            echo Copying %%d to %destFolder1%
            pause
            xcopy "%%d\*" "%destinationFolder1%\%folderName%\" /E /I /H /Y
        ) else (
            echo Folder %destFolder1%\%folderName% already exists, skipping....
        )
     ) else if /i "%folderName%"=="Ollama"(
        if not exist "%destinationFolder2%\%folderName%"(
            echo Copying %%d to %destFolder2
            xcopy "%%d\*" "%destinationFolder2%\%folderName%\" /E /I /H /Y
        ) else (
            echo Folder %destFolder2%\%folderName% already exists, skipping...
        )
     ) else if /i "%folderName%"=="Python"(
        if not exist "%destinationFolder2%\%folderName%"(
            echo Copying %%d to %destFolder2
            xcopy "%%d\*" "%destinationFolder2%\%folderName%\" /E /I /H /Y
        ) else (
            echo Folder %destFolder2%\%folderName% already exists, skipping...
        )
    )
)

rem Look for specific exe files in the destination folders and check if their paths are already in PATH variable
for /r "%destinationFolder2%" %%d in (%ollamaexe% %pythonexe%) do(
    call :check_and_add_to_path "%%~dpd"
)

endlocal