@call ..\env.bat
@echo installing schema Jyutping.

..\WeaselServer.exe /q
python make-phrases.py jyutping
python zimedb-admin.py -vi Jyutping.txt

@pause
