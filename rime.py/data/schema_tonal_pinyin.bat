@call ..\env.bat
@echo installing schema TonalPinyin.

..\WeaselServer.exe /q
python zimedb-admin.py -vi TonalPinyin.txt

@pause
