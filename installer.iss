#define MyAppName "MA1_Autograder"
#define MyAppVersion "2.0"
#define MyAppPublisher "Internal"
#define MyAppExeName "MA1_Autograder.exe"

[Setup]
AppId={{8A07F2E2-5A1F-4B3A-9E8F-9D8B9F1F1111}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}

OutputDir=installer_output
OutputBaseFilename={#MyAppName}_Setup_{#MyAppVersion}

Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

; ✅ Installer EXE icon
SetupIconFile={#SourcePath}\app.ico

; ✅ “Apps & Features” icon (points to installed EXE)
UninstallDisplayIcon={app}\{#MyAppExeName}

[Tasks]
Name: "desktopicon"; Description: "Create a &Desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
; ✅ Pull everything from your PyInstaller dist folder
Source: "dist\{#MyAppName}\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
; ✅ Start Menu shortcut (forces icon)
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppExeName}"

; ✅ Desktop shortcut (forces icon)
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\{#MyAppExeName}"

[Run]
; ✅ Launch after install (checkbox)
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
