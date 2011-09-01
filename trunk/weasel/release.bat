call env.bat
set OUTPUT=output\weasel
set SERVER=%OUTPUT%\WeaselServer.exe

if exist %SERVER% %SERVER% /q
rmdir /s /q %OUTPUT%
mkdir %OUTPUT%
mkdir %OUTPUT%\data
copy ..\rime.py\data\*.bat %OUTPUT%\data
copy ..\rime.py\data\*.py %OUTPUT%\data
copy ..\rime.py\data\*.txt %OUTPUT%\data
mkdir %OUTPUT%\engine
mkdir %OUTPUT%\engine\ibus
copy ..\rime.py\engine\*.py %OUTPUT%\engine
copy ..\rime.py\weasel\*.py %OUTPUT%\engine
copy ..\rime.py\weasel\ibus\*.py %OUTPUT%\engine\ibus
copy misc\*.conf %OUTPUT%\engine
copy misc\*.bat %OUTPUT%
copy misc\*.js %OUTPUT%
copy misc\*.py %OUTPUT%
copy misc\*.reg %OUTPUT%
copy misc\*.txt %OUTPUT%
copy Release\WeaselServer.exe %OUTPUT%
copy Release\weasel.ime %OUTPUT%\weasels.ime
copy ReleaseHant\weasel.ime %OUTPUT%\weaselt.ime
rem for installer
copy misc\zhung.* output
pause
