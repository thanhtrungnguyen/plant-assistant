#!/bin/bash
# Pre-commit Setup Script for Linux/Unix Development
# This script configures pre-commit for Linux local development and CI

show_help() {
    echo -e "\033[32mPre-commit Setup Script\033[0m"
    echo ""
    echo -e "\033[33mUsage:\033[0m"
    echo "  ./scripts/setup-precommit.sh windows   # Setup for Windows local development"
    echo "  ./scripts/setup-precommit.sh linux     # Setup for Linux/CI (GitHub Actions)"
    echo "  ./scripts/setup-precommit.sh help      # Show this help"
    echo ""
    echo -e "\033[33mDescription:\033[0m"
    echo "  This script manages dual pre-commit configurations:"
    echo "  - Windows config uses PowerShell commands for local development"
    echo "  - Linux config uses sh commands for CI/GitHub Actions"
    echo ""
    echo -e "\033[33mFiles managed:\033[0m"
    echo "  - .pre-commit-config.yaml (active config, defaults to Linux)"
    echo "  - .pre-commit-config.windows.yaml (Windows commands)"
    echo "  - .pre-commit-config.linux.yaml (Linux/CI commands)"
}

set_windows_config() {
    echo -e "\033[32mSetting up pre-commit for Windows local development...\033[0m"
    
    if [ -f ".pre-commit-config.windows.yaml" ]; then
        cp ".pre-commit-config.windows.yaml" ".pre-commit-config.yaml"
        echo -e "\033[32m✅ Configured pre-commit for Windows (PowerShell commands)\033[0m"
        echo -e "\033[33mRun: pre-commit run --all-files\033[0m"
    else
        echo -e "\033[31m❌ Windows config file not found: .pre-commit-config.windows.yaml\033[0m"
        exit 1
    fi
}

set_linux_config() {
    echo -e "\033[32mSetting up pre-commit for Linux/CI...\033[0m"
    
    if [ -f ".pre-commit-config.linux.yaml" ]; then
        cp ".pre-commit-config.linux.yaml" ".pre-commit-config.yaml"
        echo -e "\033[32m✅ Configured pre-commit for Linux (sh commands)\033[0m"
        echo -e "\033[33mThis is used in GitHub Actions CI\033[0m"
    else
        echo -e "\033[31m❌ Linux config file not found: .pre-commit-config.linux.yaml\033[0m"
        exit 1
    fi
}

# Main logic
case "${1:-}" in
    "windows")
        set_windows_config
        ;;
    "linux")
        set_linux_config
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        echo -e "\033[31mPlease specify 'windows' or 'linux'. Use 'help' for more information.\033[0m"
        show_help
        exit 1
        ;;
esac
