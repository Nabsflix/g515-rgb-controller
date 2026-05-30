#define MyAppName "RGB by Nabs"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Nabs"
#define MyAppExeName "G515-RGB-by-Nabs.exe"
#define MyAppDir "D:\App\Razer"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL=https://github.com/Nabsflix/g515-rgb-controller
AppSupportURL=https://github.com/Nabsflix/g515-rgb-controller/issues
AppUpdatesURL=https://github.com/Nabsflix/g515-rgb-controller
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir={#MyAppDir}\installer_output
OutputBaseFilename=RGB-by-Nabs-Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesInstallIn64BitMode=x64compatible
SetupIconFile=
MinVersion=10.0


[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startuprun";  Description: "Lancer automatiquement au démarrage de Windows"; GroupDescription: "Options :"

[Files]
; L'application principale
Source: "{#MyAppDir}\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Dossier presets inclus
Source: "{#MyAppDir}\presets\gaming.json";  DestDir: "{app}\presets"; Flags: ignoreversion onlyifdoesntexist
Source: "{#MyAppDir}\presets\rainbow.json"; DestDir: "{app}\presets"; Flags: ignoreversion onlyifdoesntexist

[Icons]
; Menu Démarrer
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Désinstaller {#MyAppName}"; Filename: "{uninstallexe}"
; Bureau (optionnel)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
; Démarrage automatique Windows si l'utilisateur a coché la case
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; \
  ValueType: string; ValueName: "G515 RGB Controller"; \
  ValueData: """{app}\{#MyAppExeName}"""; \
  Flags: uninsdeletevalue; Tasks: startuprun

[Run]
; Lancer l'app à la fin de l'installation
Filename: "{app}\{#MyAppExeName}"; \
  Description: "Lancer {#MyAppName}"; \
  Flags: nowait postinstall skipifsilent

[UninstallRun]
; Tuer le processus avant désinstallation
Filename: "taskkill.exe"; Parameters: "/F /IM {#MyAppExeName}"; Flags: runhidden

[Code]
// Vérification : LGHUB est-il installé ?
function LGHUBInstalled(): Boolean;
begin
  Result := FileExists('C:\Program Files\LGHUB\lghub.exe') or
            FileExists(ExpandConstant('{localappdata}\LGHUB\lghub.exe'));
end;

function InitializeSetup(): Boolean;
begin
  Result := True;
  if not LGHUBInstalled() then
  begin
    if MsgBox(
      'Logitech G HUB n''est pas détecté sur votre système.' + #13#10 + #13#10 +
      'RGB by Nabs nécessite que LGHUB soit installé et lancé' + #13#10 +
      'pour contrôler les LEDs du clavier G515.' + #13#10 + #13#10 +
      'Voulez-vous continuer l''installation quand même ?',
      mbConfirmation, MB_YESNO) = IDNO then
      Result := False;
  end;
end;
