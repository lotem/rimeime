@echo off
rem rime build script for mingw toolchain.
rem see HowToRimeWithTheCode wiki for explanations.
rem 
rem 2011-04-04 <chen.sst@gmail.com>
rem 2011-04-07 <chen.sst@gmail.com>  this should work

set RIME_ROOT=%CD%
echo RIME_ROOT=%RIME_ROOT%

echo.

echo TODO: set appropriate path to mingw and cmake
set PATH=C:\Python27;C:\MinGW\bin;%ProgramFiles%\gnuwin32\bin
echo PATH=%PATH%

echo.

echo TODO: set appropriate path to boost libraries
set BOOST_ROOT=D:\code\boost_1_43_0
echo BOOST_ROOT=%BOOST_ROOT%

echo.

echo TODO: populate this folder with third-party library header files.
set CMAKE_INCLUDE_PATH=%RIME_ROOT%\thirdparty\include
echo CMAKE_INCLUDE_PATH=%CMAKE_INCLUDE_PATH%

echo.

echo TODO: populate this folder with third-party libraries.
set CMAKE_LIBRARY_PATH=%RIME_ROOT%\thirdparty\lib
echo CMAKE_LIBRARY_PATH=%CMAKE_LIBRARY_PATH%

echo.

rem TODO: select a cmake generator
rem set CMAKE_GENERATOR="MinGW Makefiles"
set CMAKE_GENERATOR="Eclipse CDT4 - MinGW Makefiles"

set BUILD_DIR=%RIME_ROOT%\build
if exist %BUILD_DIR% goto BUILD
mkdir %BUILD_DIR%

:BUILD
cd %BUILD_DIR%
cmake -G %CMAKE_GENERATOR% %RIME_ROOT%
if %ERRORLEVEL% NEQ 0 goto ERROR
make
if %ERRORLEVEL% NEQ 0 goto ERROR
make test
if %ERRORLEVEL% NEQ 0 goto ERROR

goto EXIT

:ERROR
echo.
echo error building la rime.
echo.

:EXIT
cd %RIME_ROOT%
pause
