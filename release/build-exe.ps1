$ErrorActionPreference = "Stop"

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { throw "Python 3.13 is required. Install Python and try again." }
$pythonVersion = & python --version
if ($pythonVersion -notmatch '^Python 3\.13\.') { throw "Python 3.13 is required. Found: $pythonVersion" }

$launcher = Join-Path $PSScriptRoot "windows\daymark_launcher.py"
$dist = $PSScriptRoot
$work = Join-Path $PSScriptRoot ".build"

& python -m pip install "pywebview==6.2.1" "pyinstaller==6.22.3"
if ($LASTEXITCODE -ne 0) { throw "Could not install the Windows packaging tools." }

& python -m PyInstaller --clean --noconfirm --onefile --windowed --name Daymark --icon (Join-Path $repoRoot "static\favicon.ico") --collect-all webview --collect-all clr_loader --collect-all pythonnet --hidden-import=webview.platforms.edgechromium --distpath $dist --workpath $work --specpath $work $launcher
if ($LASTEXITCODE -ne 0) { throw "Windows EXE build failed." }

Write-Output "EXE created: $(Join-Path $PSScriptRoot 'Daymark.exe')"
