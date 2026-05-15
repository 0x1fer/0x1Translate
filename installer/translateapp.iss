; Inno Setup script for TranslateApp.
;
; Build:
;   iscc /DAppVersion="0.1.0" installer\translateapp.iss
;
; Expects PyInstaller --onedir output at  dist\TranslateApp\  and an icon
; at  assets\icon.ico  (both produced by scripts\build_windows.ps1).

#ifndef AppVersion
  #define AppVersion "dev"
#endif

[Setup]
AppId={{B6D2A1C0-2C9B-4E63-8E08-7FAF1D63CD11}
AppName=TranslateApp
AppVersion={#AppVersion}
AppPublisher=TranslateApp
DefaultDirName={localappdata}\Programs\TranslateApp
DefaultGroupName=TranslateApp
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=Output
OutputBaseFilename=TranslateApp-{#AppVersion}-setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupIconFile=..\assets\icon.ico
UninstallDisplayIcon={app}\TranslateApp.exe
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"

[Tasks]
Name: "desktopicon";  Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\TranslateApp\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\TranslateApp"; Filename: "{app}\TranslateApp.exe"
Name: "{group}\Uninstall TranslateApp"; Filename: "{uninstallexe}"
Name: "{userdesktop}\TranslateApp"; Filename: "{app}\TranslateApp.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\TranslateApp.exe"; Description: "Launch TranslateApp"; Flags: nowait postinstall skipifsilent
