# Pre-commit Setup Script for Windows Development
# This script configures pre-commit for Windows local development

param(
    [switch]$Windows,
    [switch]$Linux,
    [switch]$Help
)

function Show-Help {
    Write-Host "Pre-commit Setup Script" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\scripts\setup-precommit.ps1 -Windows   # Setup for Windows local development"
    Write-Host "  .\scripts\setup-precommit.ps1 -Linux     # Setup for Linux/CI (GitHub Actions)"
    Write-Host "  .\scripts\setup-precommit.ps1 -Help      # Show this help"
    Write-Host ""
    Write-Host "Description:" -ForegroundColor Yellow
    Write-Host "  This script manages dual pre-commit configurations:"
    Write-Host "  - Windows config uses PowerShell commands for local development"
    Write-Host "  - Linux config uses sh commands for CI/GitHub Actions"
    Write-Host ""
    Write-Host "Files managed:" -ForegroundColor Yellow
    Write-Host "  - .pre-commit-config.yaml (active config, defaults to Linux)"
    Write-Host "  - .pre-commit-config.windows.yaml (Windows commands)"
    Write-Host "  - .pre-commit-config.linux.yaml (Linux/CI commands)"
}

function Set-WindowsConfig {
    Write-Host "Setting up pre-commit for Windows local development..." -ForegroundColor Green
    
    if (Test-Path ".pre-commit-config.windows.yaml") {
        Copy-Item ".pre-commit-config.windows.yaml" ".pre-commit-config.yaml" -Force
        Write-Host "✅ Configured pre-commit for Windows (PowerShell commands)" -ForegroundColor Green
        Write-Host "Run: pre-commit run --all-files" -ForegroundColor Yellow
    } else {
        Write-Host "❌ Windows config file not found: .pre-commit-config.windows.yaml" -ForegroundColor Red
        exit 1
    }
}

function Set-LinuxConfig {
    Write-Host "Setting up pre-commit for Linux/CI..." -ForegroundColor Green
    
    if (Test-Path ".pre-commit-config.linux.yaml") {
        Copy-Item ".pre-commit-config.linux.yaml" ".pre-commit-config.yaml" -Force
        Write-Host "✅ Configured pre-commit for Linux (sh commands)" -ForegroundColor Green
        Write-Host "This is used in GitHub Actions CI" -ForegroundColor Yellow
    } else {
        Write-Host "❌ Linux config file not found: .pre-commit-config.linux.yaml" -ForegroundColor Red
        exit 1
    }
}

# Main logic
if ($Help) {
    Show-Help
    exit 0
}

if ($Windows) {
    Set-WindowsConfig
} elseif ($Linux) {
    Set-LinuxConfig
} else {
    Write-Host "Please specify -Windows or -Linux. Use -Help for more information." -ForegroundColor Red
    Show-Help
    exit 1
}
