@call ..\env.bat
@echo installing schema Wu.

..\WeaselServer.exe /q
python make-phrases.py wu
type wu-extra-phrases.txt >> wu-phrases.txt
python zimedb-admin.py -vi Wu.txt
rem python zimedb-admin.py -vi Wu-Lopha.txt

@pause
