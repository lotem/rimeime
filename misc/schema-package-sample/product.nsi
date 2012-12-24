; weasel expansion installation script
!include FileFunc.nsh
!include LogicLib.nsh
!include x64.nsh

; TODO 擴展包標識
!define PACKAGE_ID "sample"
; TODO 擴展包版本
!define PACKAGE_VERSION 1.0.0
; 必須補足 4 個整數
!define PACKAGE_BUILD ${PACKAGE_VERSION}.0
; TODO 擴展包名稱
!define PACKAGE_NAME "RIME 輸入方案【樣例】"
; TODO 發行者
!define PACKAGE_PUBLISHER "編碼匠"

; The name of the installer
Name "${PACKAGE_NAME} ${PACKAGE_VERSION}"

; The file to write
OutFile "${PACKAGE_ID}-${PACKAGE_BUILD}.exe"

VIProductVersion "${PACKAGE_BUILD}"
VIAddVersionKey /LANG=2052 "ProductName" "${PACKAGE_NAME}"
VIAddVersionKey /LANG=2052 "CompanyName" "${PACKAGE_PUBLISHER}"
VIAddVersionKey /LANG=2052 "Comments" "Powered by RIME | 中州韻輸入法引擎"
VIAddVersionKey /LANG=2052 "LegalCopyright" "Copyleft RIME Contributors 2012"
VIAddVersionKey /LANG=2052 "FileDescription" "${PACKAGE_NAME}"
VIAddVersionKey /LANG=2052 "FileVersion" "${PACKAGE_VERSION}"

Icon product.ico
SetCompressor /SOLID lzma

; The default installation directory
InstallDir "$APPDATA\Rime"

LoadLanguageFile "${NSISDIR}\Contrib\Language Files\SimpChinese.nlf"

;--------------------------------

; Pages

;Page components
Page directory
Page instfiles

;--------------------------------

Var WEASEL_ROOT

Function .onInit
  ; 讀取小狼毫安裝目錄
  ReadRegStr $R0 HKLM SOFTWARE\Rime\Weasel "WeaselRoot"
  StrCmp $R0 "" 0 done

  ; 找不到小狼毫安裝目錄，只好放這裏了
  StrCpy $R0 "$INSTDIR\${PACKAGE_ID}-${PACKAGE_VERSION}"

  MessageBox MB_OKCANCEL|MB_ICONINFORMATION \
  "找不到【小狼毫】安裝在哪裏。$\n$\n還要繼續安裝「${PACKAGE_NAME}」嗎？" \
  IDOK done
  Abort

done:
  StrCpy $WEASEL_ROOT $R0

  ; 讀取用戶目錄
  ReadRegStr $R0 HKCU SOFTWARE\Rime\Weasel "RimeUserDir"
  StrCmp $R0  "" 0 +2
  StrCpy $R0 "$APPDATA\Rime"
  StrCpy $INSTDIR $R0

FunctionEnd

; The stuff to install
Section "Package"

  SectionIn RO

  IfFileExists "$WEASEL_ROOT\WeaselServer.exe" 0 +2
  ExecWait '"$WEASEL_ROOT\WeaselServer.exe" /quit'

  SetOverwrite try
  ; install tools
  SetOutPath $INSTDIR
  File rime_deployer.exe
  File libglog.dll
  File opencc.dll
  File zlib1.dll

  ; TODO copy data files
  SetOutPath  $INSTDIR
  File "data\*.schema.yaml"
  File "data\*.dict.yaml"
  ; We can even replace config files
  ;File default.custom.yaml
  ;File weasel.custom.yaml

  SetOutPath $INSTDIR
  ; TODO add your schema(s) to the user's schema list
  ExecWait '"$INSTDIR\rime_deployer.exe" --add-schema luna_pinyin sample'
  ; TODO select your schema by default
  ExecWait '"$INSTDIR\rime_deployer.exe" --set-active-schema sample'

  ; deploy
  IfFileExists "$WEASEL_ROOT\WeaselDeployer.exe" 0 +2
  ExecWait '"$WEASEL_ROOT\WeaselDeployer.exe" /deploy'

SectionEnd

;--------------------------------
