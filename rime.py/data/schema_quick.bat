@call ..\env.bat
@echo installing schema Quick.

..\WeaselServer.exe /q
python make-phrases.py quick
python zimedb-admin.py -vi Quick.txt

@pause
