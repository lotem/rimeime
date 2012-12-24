0. 這套工具幫你把第三方輸入方案製作成安裝程序
1. 安裝 NSIS (nsis-2.46.3-Unicode-setup.exe)
2. 將要分發的輸入方案及詞典 (*.schema.yaml, *.dict.yaml) 置於 data 目錄中
3. 編輯 product.nsi，修改 TODO 部份
4. 右擊 product.nsi，選擇「Compile Unicode NSIS Script」製作安裝程序
5. 檢查 NSIS 輸出結果，若有錯誤，回到 3.
6. 測試安裝程序；輸入方案會部署到小狼毫的用戶目錄
7. 分發生成的安裝程序；用戶不需要安裝NSIS，但需要事先安裝小狼毫輸入法
