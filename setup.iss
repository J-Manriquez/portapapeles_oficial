[Setup]
AppName=Clipboard Manager
AppVersion=1.0
DefaultDirName={pf}\Clipboard Manager
DefaultGroupName=Clipboard Manager
OutputDir=Output
OutputBaseFilename=ClipboardManagerSetup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\ClipboardManager.exe

[Files]
; Cambiar la ruta para usar la carpeta dist correcta
Source: "dist\ClipboardManager\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "autorun.vbs"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Clipboard Manager"; Filename: "{app}\ClipboardManager.exe"; IconFilename: "{app}\icon.ico"
Name: "{commondesktop}\Clipboard Manager"; Filename: "{app}\ClipboardManager.exe"; IconFilename: "{app}\icon.ico"
Name: "{userstartup}\Clipboard Manager"; Filename: "{app}\autorun.vbs"

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "Clipboard Manager"; ValueData: """{app}\autorun.vbs"""; Flags: uninsdeletevalue

[Run]
Filename: "{app}\ClipboardManager.exe"; Description: "Launch Clipboard Manager"; Flags: postinstall nowait

[UninstallDelete]
Type: files; Name: "{userappdata}\clipboard_data.json"
Type: files; Name: "{app}\autorun.vbs"
