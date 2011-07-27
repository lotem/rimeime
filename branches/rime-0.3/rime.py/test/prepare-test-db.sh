#!/bin/bash

cd ../data
python zimedb-admin.py -v -i Pinyin.txt -d ../test/test.db
if [ ! -e zhuyin-phrases.txt ]; then
  python make-phrases.py -v zhuyin
fi
python zimedb-admin.py -v -i Zhuyin.txt -d ../test/test.db
