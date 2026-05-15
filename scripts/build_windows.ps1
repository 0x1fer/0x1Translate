# Build the Windows ZIP + Inno Setup installer.
#
# Requirements (build host):
#   - Python 3.11+ with requirements.txt + requirements-dev.txt installed
#   - Inno Setup 6 (`iscc.exe` on PATH; install via `choco install innosetup`)
#   - Pillow installed (for scripts/make_icons.py)
#
# Run from the repo root in PowerShell:
#   .\scripts\build_windows.ps1

$ErrorActionPreference = "Stop"

$Root = Resolve-Path "$PSScriptRoot\.."
Set-Location $Root

try {
    $Version = (git describe --tags --always 2>$null)
} catch { $Version = "dev" }
if (-not $Version) { $Version = "dev" }
Write-Host "[build_windows] version=$Version"

# 1. Icons
python scripts\make_icons.py

# 2. PyInstaller
if (Test-Path build) { Remove-Item -Recurse -Force build }
if (Test-Path dist)  { Remove-Item -Recurse -Force dist }
pyinstaller build_windows.spec

# 3. ZIP
$Zip = "TranslateApp-$Version-windows-x64.zip"
if (Test-Path $Zip) { Remove-Item $Zip }
Compress-Archive -Path dist\TranslateApp\* -DestinationPath $Zip
Write-Host "[build_windows] wrote $Zip"

# 4. Inno Setup installer
$Iscc = (Get-Command iscc -ErrorAction SilentlyContinue)
if (-not $Iscc) {
    Write-Warning "iscc (Inno Setup) not on PATH; skipping installer."
    exit 0
}
iscc /DAppVersion="$Version" installer\translateapp.iss
Write-Host "[build_windows] wrote Output\TranslateApp-$Version-setup.exe"
