$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$gradle = Get-Command gradle -ErrorAction SilentlyContinue
if (-not $gradle) {
    throw "Gradle 8.9 is required. Install Gradle and Android SDK Platform 35, or use the GitHub Actions workflow."
}

Push-Location $repoRoot
try {
    & gradle --no-daemon -p (Join-Path $PSScriptRoot "android") assembleDebug
    if ($LASTEXITCODE -ne 0) { throw "Android APK build failed." }

    $builtApk = Join-Path $PSScriptRoot "android\app\build\outputs\apk\debug\app-debug.apk"
    Copy-Item -LiteralPath $builtApk -Destination (Join-Path $PSScriptRoot "Daymark.apk") -Force
    Write-Output "APK created: $(Join-Path $PSScriptRoot 'Daymark.apk')"
}
finally {
    Pop-Location
}
