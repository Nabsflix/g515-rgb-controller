#define MyAppName "RGB by Nabs"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Nabs"
#define MyAppExeName "G515-RGB-by-Nabs.exe"
#define MyAppDir "D:\App\Razer"
#define LGHUBUrl "https://www.logitechg.com/fr-fr/innovation/g-hub.html"

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
MinVersion=10.0
SetupIconFile={#MyAppDir}\icon.ico

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startuprun";  Description: "Lancer automatiquement au démarrage de Windows"; GroupDescription: "Options :"

[Files]
Source: "{#MyAppDir}\dist\{#MyAppExeName}";  DestDir: "{app}"; Flags: ignoreversion
Source: "{#MyAppDir}\presets\gaming.json";   DestDir: "{app}\presets"; Flags: ignoreversion onlyifdoesntexist
Source: "{#MyAppDir}\presets\rainbow.json";  DestDir: "{app}\presets"; Flags: ignoreversion onlyifdoesntexist

[Icons]
Name: "{group}\{#MyAppName}";                  Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Désinstaller {#MyAppName}";     Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}";            Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; \
  ValueType: string; ValueName: "G515 RGB Controller"; \
  ValueData: """{app}\{#MyAppExeName}"""; \
  Flags: uninsdeletevalue; Tasks: startuprun

[Run]
; Lancer LGHUB si installé mais pas encore lancé
Filename: "{code:GetLGHUBExe}"; Description: "Démarrer Logitech G HUB"; \
  Flags: nowait shellexec skipifsilent; Check: ShouldStartLGHUB

; Lancer l'app à la fin
Filename: "{app}\{#MyAppExeName}"; Description: "Lancer {#MyAppName}"; \
  Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "taskkill.exe"; Parameters: "/F /IM {#MyAppExeName}"; Flags: runhidden; RunOnceId: "KillApp"

[Code]

// ── Détection LGHUB ──────────────────────────────────────────────────────────

function GetLGHUBExe(Param: String): String;
begin
  if FileExists('C:\Program Files\LGHUB\lghub.exe') then
    Result := 'C:\Program Files\LGHUB\lghub.exe'
  else if FileExists(ExpandConstant('{localappdata}\LGHUB\lghub.exe')) then
    Result := ExpandConstant('{localappdata}\LGHUB\lghub.exe')
  else
    Result := '';
end;

function LGHUBInstalled(): Boolean;
begin
  Result := (GetLGHUBExe('') <> '');
end;

function LGHUBRunning(): Boolean;
var
  ResultCode: Integer;
begin
  // Utilise tasklist pour vérifier si le processus tourne
  Exec('cmd.exe', '/C tasklist /FI "IMAGENAME eq lghub.exe" | find /I "lghub.exe" >nul 2>&1',
       '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Result := (ResultCode = 0);
end;

function ShouldStartLGHUB(): Boolean;
begin
  Result := LGHUBInstalled() and not LGHUBRunning();
end;

// ── Page personnalisée : prérequis LGHUB ─────────────────────────────────────

var
  LGHUBPage: TWizardPage;
  LGHUBStatusLabel: TNewStaticText;
  LGHUBStatusIcon: TNewStaticText;
  BtnDownload: TNewButton;
  BtnRefresh: TNewButton;

procedure UpdateLGHUBStatus();
begin
  if LGHUBInstalled() then
  begin
    LGHUBStatusIcon.Caption  := '✅';
    LGHUBStatusLabel.Caption :=
      'Logitech G HUB est installé.' + #13#10 +
      'Vous pouvez continuer l''installation.';
    BtnDownload.Visible := False;
    BtnRefresh.Visible  := False;
    WizardForm.NextButton.Enabled := True;
  end
  else
  begin
    LGHUBStatusIcon.Caption  := '⚠️';
    LGHUBStatusLabel.Caption :=
      'Logitech G HUB n''est pas installé.' + #13#10 + #13#10 +
      'RGB by Nabs en a besoin pour communiquer avec votre' + #13#10 +
      'clavier G515. Cliquez sur "Télécharger LGHUB" ci-dessous,' + #13#10 +
      'installez-le, puis cliquez sur "Actualiser".';
    BtnDownload.Visible := True;
    BtnRefresh.Visible  := True;
    WizardForm.NextButton.Enabled := False;
  end;
end;

procedure DownloadLGHUBClick(Sender: TObject);
var
  ErrCode: Integer;
begin
  ShellExec('open', '{#LGHUBUrl}', '', '', SW_SHOWNORMAL, ewNoWait, ErrCode);
end;

procedure RefreshClick(Sender: TObject);
begin
  UpdateLGHUBStatus();
  if LGHUBInstalled() then
    MsgBox('Logitech G HUB détecté ! Vous pouvez continuer.', mbInformation, MB_OK);
end;

procedure InitializeWizard();
var
  Lbl: TNewStaticText;
begin
  // ── Page prérequis LGHUB ──────────────────────────────────────────────────
  LGHUBPage := CreateCustomPage(
    wpWelcome,
    'Prérequis — Logitech G HUB',
    'RGB by Nabs nécessite Logitech G HUB pour fonctionner.'
  );

  // Icône de statut
  LGHUBStatusIcon := TNewStaticText.Create(LGHUBPage);
  LGHUBStatusIcon.Parent  := LGHUBPage.Surface;
  LGHUBStatusIcon.Left    := 0;
  LGHUBStatusIcon.Top     := 8;
  LGHUBStatusIcon.Width   := 32;
  LGHUBStatusIcon.Height  := 32;
  LGHUBStatusIcon.Caption := '...';
  LGHUBStatusIcon.Font.Size := 18;

  // Message de statut
  LGHUBStatusLabel := TNewStaticText.Create(LGHUBPage);
  LGHUBStatusLabel.Parent    := LGHUBPage.Surface;
  LGHUBStatusLabel.Left      := 40;
  LGHUBStatusLabel.Top       := 8;
  LGHUBStatusLabel.Width     := LGHUBPage.SurfaceWidth - 40;
  LGHUBStatusLabel.Height    := 80;
  LGHUBStatusLabel.Caption   := 'Vérification en cours...';
  LGHUBStatusLabel.WordWrap  := True;
  LGHUBStatusLabel.Font.Size := 9;

  // Explication
  Lbl := TNewStaticText.Create(LGHUBPage);
  Lbl.Parent   := LGHUBPage.Surface;
  Lbl.Left     := 0;
  Lbl.Top      := 110;
  Lbl.Width    := LGHUBPage.SurfaceWidth;
  Lbl.Height   := 60;
  Lbl.Caption  :=
    'Logitech G HUB est le logiciel officiel Logitech. Il s''installe en' + #13#10 +
    'arrière-plan et gère la communication avec votre clavier G515.' + #13#10 +
    'RGB by Nabs s''y connecte pour contrôler l''éclairage.';
  Lbl.WordWrap := True;
  Lbl.Font.Color := $666666;

  // Bouton téléchargement
  BtnDownload := TNewButton.Create(LGHUBPage);
  BtnDownload.Parent  := LGHUBPage.Surface;
  BtnDownload.Left    := 0;
  BtnDownload.Top     := 190;
  BtnDownload.Width   := 220;
  BtnDownload.Height  := 30;
  BtnDownload.Caption := '🌐  Télécharger Logitech G HUB';
  BtnDownload.OnClick := @DownloadLGHUBClick;

  // Bouton actualiser
  BtnRefresh := TNewButton.Create(LGHUBPage);
  BtnRefresh.Parent  := LGHUBPage.Surface;
  BtnRefresh.Left    := 230;
  BtnRefresh.Top     := 190;
  BtnRefresh.Width   := 140;
  BtnRefresh.Height  := 30;
  BtnRefresh.Caption := '🔄  Actualiser';
  BtnRefresh.OnClick := @RefreshClick;

  UpdateLGHUBStatus();
end;

// Ré-évaluer le statut chaque fois qu'on arrive sur la page prérequis
procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = LGHUBPage.ID then
    UpdateLGHUBStatus();
end;
