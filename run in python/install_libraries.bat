@echo off
echo Installing required Python libraries...

REM Install Selenium
pip install selenium

REM Install WebDriver Manager for managing browser drivers
pip install webdriver_manager

REM Tkinter is included with Python standard library, but 'tk' might require the 'pillow' package
pip install pillow

REM Install threading, time, webbrowser, and os (these are included with Python standard library and do not require installation)
echo threading, time, webbrowser, and os are part of the Python standard library and do not require installation.

REM Install tkinter
pip install tk

echo All libraries installed successfully.

pause
