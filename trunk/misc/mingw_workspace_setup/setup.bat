@echo off

rem TODO: replace this with your google code account
set SVN_ACCOUNT=chen.sst@gmail.com

set CODE=\code
set MINGW=%SystemDrive%\MinGW
set OPT=%SystemDrive%\opt

if defined SVN_ACCOUNT (
  set SVN_CHECKOUT_CMD=svn checkout https://rimeime.googlecode.com/svn/trunk/librime librime --username %SVN_ACCOUNT%
) else (
  set SVN_CHECKOUT_CMD=svn checkout http://rimeime.googlecode.com/svn/trunk/librime librime 
)

set DEV_PATH=%MINGW%\bin;%OPT%\cmake-win32\bin;%OPT%\svn-win32\bin
set OLD_PATH=%PATH%

set BACK=%CD%

echo downloading devtools...

set MISSING=

if not exist mingw-get-inst-20110316.exe (
  set MISSING=%MISSING% http://jaist.dl.sourceforge.net/project/mingw/Automated%20MinGW%20Installer/mingw-get-inst/mingw-get-inst-20110316/mingw-get-inst-20110316.exe
)
if not exist svn-win32-1.6.16.zip (
  set MISSING=%MISSING% http://jaist.dl.sourceforge.net/project/win32svn/1.6.16/svn-win32-1.6.16.zip 
)
if not exist cmake-2.8.4-win32-x86.zip (
  set MISSING=%MISSING% http://www.cmake.org/files/v2.8/cmake-2.8.4-win32-x86.zip
)

if defined MISSING (
  curl --remote-name-all %MISSING%
  if not errorlevel 0 goto error
)

echo downloading third party libraries...

set MISSING=

if not exist yaml-cpp-0.2.6.tar.gz (
  set MISSING=%MISSING% http://yaml-cpp.googlecode.com/files/yaml-cpp-0.2.6.tar.gz
)

if not exist gtest-1.6.0.zip (
  set MISSING=%MISSING% http://googletest.googlecode.com/files/gtest-1.6.0.zip
)

if not exist boost_1_47_0.7z (
  set MISSING=%MISSING% http://jaist.dl.sourceforge.net/project/boost/boost/1.46.1/boost_1_47_0.7z
)

if defined MISSING (
  curl --remote-name-all %MISSING%
  if not errorlevel 0 goto error
)

echo preparing devtools...

if not exist %MINGW% (
  echo TODO: install MinGW to %MINGW%
  mingw-get-inst-20110316.exe
  if not errorlevel 0 goto error
  if not exist %MINGW% goto error
  copy %MINGW%\bin\mingw32-make.exe %MINGW%\bin\make.exe
  if not errorlevel 0 goto error
)

if not exist %OPT%\svn-win32 (
  7za x -o%OPT% svn-win32-1.6.16.zip
  if not errorlevel 0 goto error
  rename %OPT%\svn-win32-1.6.16 svn-win32
)

if not exist %OPT%\cmake-win32 (
  7za x -o%OPT% cmake-2.8.4-win32-x86.zip
  if not errorlevel 0 goto error
  rename %OPT%\cmake-2.8.4-win32-x86 cmake-win32
)

set PATH=%DEV_PATH%;%OLD_PATH%
path

echo acquiring source code de la rime...

if not exist %CODE% mkdir %CODE%

if not exist %CODE%\librime (
  cd %CODE%
  %SVN_CHECKOUT_CMD%
  if not errorlevel 0 goto error
  cd %BACK%
) else (
  cd %CODE%
  svn update
  if not errorlevel 0 goto error
  cd %BACK%
)

echo preparing third party libraries...

if not exist %CODE%\yaml-cpp (
  7za x -o. yaml-cpp-0.2.6.tar.gz
  if not errorlevel 0 goto error
  7za x -o%CODE% yaml-cpp-0.2.6.tar
  if not errorlevel 0 goto error
  del yaml-cpp-0.2.6.tar
)

if not exist %CODE%\yaml-cpp\build\libyaml-cpp.a (
  cd %CODE%\yaml-cpp
  if exist build rmdir /s /q build
  mkdir build
  cd build
  cmake -G "MinGW Makefiles" ..
  if not errorlevel 0 goto error
  make
  if not errorlevel 0 goto error
  cd %BACK%
)

if not exist %CODE%\gtest-1.6.0 (
  7za x -o%CODE% gtest-1.6.0.zip
  if not errorlevel 0 goto error
)

if not exist %CODE%\gtest-1.6.0\build\libgtest.a (
  cd %CODE%\gtest-1.6.0
  if exist build rmdir /s /q build
  mkdir build
  cd build
  cmake -G "MinGW Makefiles" -Dgtest_disable_pthreads=ON ..
  if not errorlevel 0 goto error
  make
  if not errorlevel 0 goto error
  cd %BACK%
)

if not exist %CODE%\boost_1_47_0 (
  7za x -o%CODE% boost_1_47_0.7z
  if not errorlevel 0 goto error
)

if not exist %CODE%\boost_1_47_0\bjam.exe (
  cd %CODE%\boost_1_47_0
  bootstrap.bat
  if not errorlevel 0 goto error
  cd %BACK%
)

if not exist %CODE%\boost_1_47_0\stage\lib (
  cd %CODE%\boost_1_47_0
  bjam --toolset=gcc stage
  if not errorlevel 0 goto error
  cd %BACK%
)

echo populating third party libraries...

set THIRDPARTY=%CODE%\librime\thirdparty

if not exist %THIRDPARTY%\include\gtest (
  xcopy /i /s /q %CODE%\gtest-1.6.0\include\gtest %THIRDPARTY%\include\gtest
  if not errorlevel 0 goto error
)
if not exist %THIRDPARTY%\lib\libgtest.a (
  copy %CODE%\gtest-1.6.0\build\libgtest.a %THIRDPARTY%\lib
  if not errorlevel 0 goto error
)
if not exist %THIRDPARTY%\lib\libgtest_main.a (
  copy %CODE%\gtest-1.6.0\build\libgtest_main.a %THIRDPARTY%\lib
  if not errorlevel 0 goto error
)

if not exist %THIRDPARTY%\include\yaml-cpp (
  xcopy /i /s /q %CODE%\yaml-cpp\include\yaml-cpp %THIRDPARTY%\include\yaml-cpp
  if not errorlevel 0 goto error
)
if not exist %THIRDPARTY%\lib\libyaml-cpp.a (
  copy %CODE%\yaml-cpp\build\libyaml-cpp.a %THIRDPARTY%\lib
  if not errorlevel 0 goto error
)

echo updating environment settings...

set ENV_FILE=%CODE%\librime\env.bat
echo rem generated environment settings > %ENV_FILE%
echo (set DEV_PATH=%DEV_PATH%) >> %ENV_FILE%
echo (set RIME_ROOT=%%CD%%) >> %ENV_FILE%
echo (set BOOST_ROOT=%CODE%\boost_1_47_0) >> %ENV_FILE%

echo.
echo ready to rime with the code.
echo.
goto exit

:error
echo.
echo mission failed.
echo.

:exit
set PATH=%OLD_PATH%
cd %BACK%
pause
