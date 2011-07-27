@call ..\env.bat
@echo installing schema Zhuyin.

..\WeaselServer.exe /q
python zimedb-admin.py -vi Zhuyin.txt

@pause
