@echo off
REM 43V3R CORE Health Monitor Windows Task Scheduler Setup
REM Run this script as Administrator to create a scheduled task

set TASK_NAME=43V3R-HealthMonitor
set SCRIPT_PATH=C:\Users\p3rc\Desktop\newdev\43V3RMUS1C\43V3RMUS1C\backend\health_monitor.py
set PYTHON_PATH=C:\Users\p3rc\AppData\Local\Programs\Python\Python312\python.exe

echo Creating Windows Task for 43V3R Health Monitor...
echo.

REM Create task that runs every 5 minutes
schtasks /Create /TN "%TASK_NAME%" /TR "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\" --interval 300 --no-alerts" /SC MINUTE /MO 5 /RU "SYSTEM" /RL HIGHEST /F

if %ERRORLEVEL% EQU 0 (
    echo.
    echo SUCCESS: Task '%TASK_NAME%' created successfully!
    echo The monitor will run every 5 minutes and log to the Windows Event Log.
    echo.
    echo To view logs: Event Viewer -> Windows Logs -> Application
    echo To disable: schtasks /Change /TN "%TASK_NAME%" /DISABLE
    echo To enable:  schtasks /Change /TN "%TASK_NAME%" /EN
    echo To delete:  schtasks /Delete /TN "%TASK_NAME%" /F
) else (
    echo ERROR: Failed to create task. Run this script as Administrator.
)

echo.
pause