# Diagnostic script to check why multidesk.exe isn't running

Write-Host "=== MultiDesk Diagnostic Tool ===" -ForegroundColor Cyan
Write-Host ""

# Check if executable exists
$exePath = ".\multidesk.exe"
if (-not (Test-Path $exePath)) {
    Write-Host "ERROR: multidesk.exe not found in current directory" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
    Write-Host "Please run this script from the directory containing multidesk.exe" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Found multidesk.exe" -ForegroundColor Green
Write-Host ""

# Check file size
$fileInfo = Get-Item $exePath
Write-Host "File size: $([math]::Round($fileInfo.Length / 1MB, 2)) MB" -ForegroundColor Cyan
Write-Host "Last modified: $($fileInfo.LastWriteTime)" -ForegroundColor Cyan
Write-Host ""

# Check for sciter.dll (required for UI)
$sciterDll = Join-Path (Split-Path $exePath) "sciter.dll"
if (Test-Path $sciterDll) {
    Write-Host "✓ Found sciter.dll" -ForegroundColor Green
} else {
    Write-Host "✗ MISSING: sciter.dll (required for UI)" -ForegroundColor Red
    Write-Host "  Download from: https://raw.githubusercontent.com/c-smile/sciter-sdk/master/bin.win/x64/sciter.dll" -ForegroundColor Yellow
    Write-Host "  Place it in the same directory as multidesk.exe" -ForegroundColor Yellow
}
Write-Host ""

# Check Visual C++ Runtime
Write-Host "Checking Visual C++ Runtime..." -ForegroundColor Cyan
$vcRedist = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*" | 
    Where-Object { $_.DisplayName -like "*Visual C++*Redistributable*" -or $_.DisplayName -like "*Microsoft Visual C++*" }
if ($vcRedist) {
    Write-Host "✓ Visual C++ Redistributables found:" -ForegroundColor Green
    $vcRedist | ForEach-Object { Write-Host "  - $($_.DisplayName)" -ForegroundColor Gray }
} else {
    Write-Host "⚠ Visual C++ Redistributables not found in registry" -ForegroundColor Yellow
    Write-Host "  (This doesn't necessarily mean they're missing)" -ForegroundColor Gray
}
Write-Host ""

# Try to get DLL dependencies
Write-Host "Checking DLL dependencies..." -ForegroundColor Cyan
try {
    # Use dumpbin if available (part of Visual Studio)
    $dumpbin = Get-Command dumpbin -ErrorAction SilentlyContinue
    if ($dumpbin) {
        Write-Host "Using dumpbin to check dependencies..." -ForegroundColor Gray
        $deps = & dumpbin /dependents $exePath 2>&1 | Select-String "\.dll"
        if ($deps) {
            Write-Host "Dependencies found:" -ForegroundColor Green
            $deps | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
        }
    } else {
        Write-Host "⚠ dumpbin not available (install Visual Studio Build Tools to use it)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Could not check DLL dependencies" -ForegroundColor Yellow
}
Write-Host ""

# Try to run the executable and capture error
Write-Host "Attempting to run multidesk.exe..." -ForegroundColor Cyan
Write-Host ""

try {
    $process = Start-Process -FilePath $exePath -NoNewWindow -PassThru -Wait -ErrorAction Stop
    Write-Host "✓ Process started and exited with code: $($process.ExitCode)" -ForegroundColor Green
    if ($process.ExitCode -ne 0) {
        Write-Host "  Exit code $($process.ExitCode) indicates an error occurred" -ForegroundColor Yellow
    }
} catch {
    $errorMsg = $_.Exception.Message
    Write-Host "✗ ERROR running executable:" -ForegroundColor Red
    Write-Host "  $errorMsg" -ForegroundColor Red
    Write-Host ""
    
    # Common error messages and solutions
    if ($errorMsg -like "*sciter*") {
        Write-Host "SOLUTION: Download sciter.dll and place it next to multidesk.exe" -ForegroundColor Yellow
    } elseif ($errorMsg -like "*VCRUNTIME*" -or $errorMsg -like "*MSVCP*" -or $errorMsg -like "*api-ms-win*") {
        Write-Host "SOLUTION: Install Visual C++ Redistributable:" -ForegroundColor Yellow
        Write-Host "  https://aka.ms/vs/17/release/vc_redist.x64.exe" -ForegroundColor Cyan
    } elseif ($errorMsg -like "*cannot find*" -or $errorMsg -like "*not found*") {
        Write-Host "SOLUTION: Missing DLL dependency. Check the error message above for the specific DLL." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=== Diagnostic Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "If the executable still doesn't work:" -ForegroundColor Yellow
Write-Host "1. Check Windows Event Viewer for application errors" -ForegroundColor Gray
Write-Host "2. Run from Command Prompt to see error messages: multidesk.exe" -ForegroundColor Gray
Write-Host "3. Check GitHub Actions logs for build warnings" -ForegroundColor Gray
