@call ..\env.bat
@echo installing schema Pinyin.

..\WeaselServer.exe /q
python zimedb-admin.py -vi Pinyin.txt
python zimedb-admin.py -ki DoublePinyin.txt
python zimedb-admin.py -ki ComboPinyin.txt

@pause
