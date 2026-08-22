; NSIS Script for Yalda Gym Management Application
Unicode True
!include "MUI2.nsh"
!include "FileFunc.nsh"

!define PRODUCT_NAME "نرم‌افزار مدیریت باشگاه یلدا"
!define PRODUCT_NAME_EN "Yalda Gym"
!define PRODUCT_VERSION "2.2.0"
!define PRODUCT_PUBLISHER "ابوالفضل صمدی کوچکسرائی"
!define PRODUCT_WEB_SITE "https://github.com/AbolfazlSamadi2006/Yalda-Gym-App"
!define PRODUCT_EXE "Yalda.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\YaldaGym"

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "dist\Yalda_Setup_v${PRODUCT_VERSION}.exe"
InstallDir "$LOCALAPPDATA\Programs\YaldaGym"
InstallDirRegKey HKCU "${PRODUCT_UNINST_KEY}" "InstallLocation"
RequestExecutionLevel user

SetCompressor /SOLID lzma
SetCompressorDictSize 64

!define MUI_ICON "resources\images\app_icon.ico"
!define MUI_UNICON "resources\images\app_icon.ico"
!define MUI_ABORTWARNING

; Standard English Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

!define MUI_FINISHPAGE_RUN "$INSTDIR\${PRODUCT_EXE}"
!define MUI_FINISHPAGE_RUN_TEXT "Run ${PRODUCT_NAME}"
!insertmacro MUI_PAGE_FINISH

; Uninstaller Pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; English UI (Default)
!insertmacro MUI_LANGUAGE "English"

VIProductVersion "2.2.0.0"
VIAddVersionKey "ProductName" "${PRODUCT_NAME}"
VIAddVersionKey "CompanyName" "${PRODUCT_PUBLISHER}"
VIAddVersionKey "FileDescription" "${PRODUCT_NAME}"
VIAddVersionKey "FileVersion" "${PRODUCT_VERSION}"
VIAddVersionKey "ProductVersion" "${PRODUCT_VERSION}"

Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    SetOverwrite on
    File /r "dist\Yalda\*.*"

    SetOverwrite off
    CreateDirectory "$INSTDIR\data"
    CreateDirectory "$INSTDIR\data\backups"
    CreateDirectory "$INSTDIR\data\pdf"
    CreateDirectory "$INSTDIR\data\uploads"
    CreateDirectory "$INSTDIR\data\uploads\profile-photos"
    CreateDirectory "$INSTDIR\data\uploads\progress-photos"
    CreateDirectory "$INSTDIR\data\uploads\exercise-media"
    SetOverwrite on

    WriteUninstaller "$INSTDIR\Uninstall.exe"

    CreateDirectory "$SMPROGRAMS\باشگاه یلدا"
    CreateShortcut "$SMPROGRAMS\باشگاه یلدا\نرم‌افزار باشگاه یلدا.lnk" "$INSTDIR\${PRODUCT_EXE}"
    CreateShortcut "$SMPROGRAMS\باشگاه یلدا\حذف نرم‌افزار.lnk" "$INSTDIR\Uninstall.exe"
    CreateShortcut "$DESKTOP\نرم‌افزار باشگاه یلدا.lnk" "$INSTDIR\${PRODUCT_EXE}"

    WriteRegStr HKCU "${PRODUCT_UNINST_KEY}" "DisplayName" "${PRODUCT_NAME}"
    WriteRegStr HKCU "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
    WriteRegStr HKCU "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
    WriteRegStr HKCU "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
    WriteRegStr HKCU "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\${PRODUCT_EXE},0"
    WriteRegStr HKCU "${PRODUCT_UNINST_KEY}" "UninstallString" '"$INSTDIR\Uninstall.exe"'
    WriteRegStr HKCU "${PRODUCT_UNINST_KEY}" "InstallLocation" "$INSTDIR"
    WriteRegDWORD HKCU "${PRODUCT_UNINST_KEY}" "NoModify" 1
    WriteRegDWORD HKCU "${PRODUCT_UNINST_KEY}" "NoRepair" 1

    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
    IntFmt $0 "0x%08X" $0
    WriteRegDWORD HKCU "${PRODUCT_UNINST_KEY}" "EstimatedSize" "$0"
SectionEnd

Section "Uninstall"
    Delete "$DESKTOP\نرم‌افزار باشگاه یلدا.lnk"
    Delete "$SMPROGRAMS\باشگاه یلدا\نرم‌افزار باشگاه یلدا.lnk"
    Delete "$SMPROGRAMS\باشگاه یلدا\حذف نرم‌افزار.lnk"
    RMDir "$SMPROGRAMS\باشگاه یلدا"

    MessageBox MB_YESNO|MB_ICONQUESTION "Are you sure you want to completely remove ${PRODUCT_NAME} and its databases?" IDNO keep_data
    RMDir /r "$INSTDIR\data"
    Goto remove_program_files

keep_data:

remove_program_files:
    Delete "$INSTDIR\${PRODUCT_EXE}"
    Delete "$INSTDIR\Uninstall.exe"
    RMDir /r "$INSTDIR\_internal"
    RMDir "$INSTDIR"

    DeleteRegKey HKCU "${PRODUCT_UNINST_KEY}"
SectionEnd