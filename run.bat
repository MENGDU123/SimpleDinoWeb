@echo off
setlocal enabledelayedexpansion

if exist ".\static\hidden\latest.log" (
    ren ".\static\hidden\latest.log" "run_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log"
)

set "USER_ARGS="
if exist "user_args.txt" (
    for /f "usebackq delims=" %%i in (`powershell -Command "$content = Get-Content user_args.txt | Where-Object { $_ -match '^\s*[^#]' -and $_ -notmatch '^\s*$' } | Select-Object -First 1; if ($content) { $content } else { '--debug --extra' }"`) do set "USER_ARGS=%%i"
) else (
    set "USER_ARGS=--debug --extra"
)

cmd /c "python app.py %USER_ARGS% 2>&1" | powershell -Command "$input | Tee-Object -FilePath .\static\hidden\latest.log"

pause