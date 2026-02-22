; Inno Setup script for Bloc Note Epinglé
; Génère un installateur avec choix du dossier, icône, licence et option démarrage auto

[Setup]
AppName=Bloc Note Epinglé
AppVersion=1.0.0
AppPublisher=T4zor
DefaultDirName={pf}\BlocNoteEpinglé
DefaultGroupName=Bloc Note Epinglé
OutputBaseFilename=BlocNoteEpinglé-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
LicenseFile=LICENSE.txt
SetupIconFile=icon.ico
DisableDirPage=no

[Files]
Source: "dist\BlocNoteEpinglé.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "app image\*"; DestDir: "{app}\app image"; Flags: recursesubdirs createallsubdirs
Source: "nav\*"; DestDir: "{app}\nav"; Flags: recursesubdirs createallsubdirs
Source: "fonts\*"; DestDir: "{app}\fonts"; Flags: recursesubdirs createallsubdirs
; Licence copiée pour consultation
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Bloc Note Epinglé"; Filename: "{app}\BlocNoteEpinglé.exe"; IconFilename: "{app}\icon.ico"
Name: "{commondesktop}\Bloc Note Epinglé"; Filename: "{app}\BlocNoteEpinglé.exe"; IconFilename: "{app}\icon.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le bureau"; Flags: unchecked
Name: "autoStart"; Description: "Lancer au démarrage de Windows"; Flags: unchecked

[Run]
Filename: "{app}\BlocNoteEpinglé.exe"; Description: "Lancer Bloc Note Epinglé"; Flags: nowait postinstall skipifsilent

[Registry]
; Optionnel : entrée Run (clé utilisateur) si la tâche autoStart est cochée
Root: HKCU; Subkey: "Software\\Microsoft\\Windows\\CurrentVersion\\Run"; ValueType: string; ValueName: "BlocNoteEpinglé"; ValueData: """{app}\\BlocNoteEpinglé.exe"""; Flags: uninsdeletevalue; Tasks: autoStart
