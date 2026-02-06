Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RepoRoot

Write-Host "Installing Rust target for Windows GNU..."
rustup target add x86_64-pc-windows-gnu

if (-not $Env:VCPKG_ROOT) {
  $Env:VCPKG_ROOT = Join-Path $Env:USERPROFILE "vcpkg"
}

if (-not (Test-Path $Env:VCPKG_ROOT)) {
  Write-Host "Cloning vcpkg to $Env:VCPKG_ROOT..."
  git clone https://github.com/microsoft/vcpkg $Env:VCPKG_ROOT
}

Set-Location $Env:VCPKG_ROOT
if (-not (Test-Path ".\vcpkg.exe")) {
  Write-Host "Bootstrapping vcpkg..."
  .\bootstrap-vcpkg.bat
}

Write-Host "Installing vcpkg dependencies (x64-windows-static)..."
.\vcpkg.exe install libvpx:x64-windows-static libyuv:x64-windows-static opus:x64-windows-static aom:x64-windows-static

Set-Location $RepoRoot
Write-Host "Building MultiDesk..."
cargo build --release --bin multidesk --target x86_64-pc-windows-gnu

Write-Host "Build complete:"
Write-Host "  target\release\multidesk.exe"
