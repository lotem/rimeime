@echo off
copy ..\opencc.dll .
copy ..\opencc.h .
copy ..\opencc_types.h .
copy ..\vc10\*.* .
cl test_opencc.cc opencc.lib /I ..\..\..\librime\thirdparty\include
if ERRORLEVEL 1 goto ERROR
test_opencc < test_input.hant > test_output.hans
if ERRORLEVEL 1 goto ERROR
notepad test_output.hans
goto END
:ERROR
echo "Error happend, sigh."
:END

