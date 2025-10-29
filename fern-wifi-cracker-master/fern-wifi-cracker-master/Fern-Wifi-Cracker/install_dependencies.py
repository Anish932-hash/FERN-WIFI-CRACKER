#!/usr/bin/env python3
"""
Fern WiFi Cracker - Kali Linux Dependency Installer
Automatically installs all required tools and dependencies for Kali Linux
"""

import sys
import os

# Add core directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

try:
    from kali_dependency_manager import KaliDependencyManager
except ImportError:
    print("❌ Error: kali_dependency_manager.py not found in core directory")
    print("   Please ensure all core files are present")
    sys.exit(1)

def main():
    """Main installation function"""
    print("🛠️  Fern WiFi Cracker - Kali Linux Setup")
    print("=" * 50)
    print("This script will install all required dependencies for Fern WiFi Cracker")
    print("on Kali Linux systems.\n")

    # Check if running on Kali Linux
    manager = KaliDependencyManager()

    if not manager.is_kali:
        print("❌ This installer is designed for Kali Linux only!")
        print("   Detected OS is not Kali Linux.")
        print("   Please run this on a Kali Linux system.")
        print("\nFor other Linux distributions, please install tools manually:")
        print("   - aircrack-ng suite")
        print("   - wifite")
        print("   - cowpatty")
        print("   - crunch")
        print("   - macchanger")
        print("   - mdk3/mdk4")
        print("   - kismet")
        print("   - reaver/pixiewps")
        print("   - hashcat (optional)")
        sys.exit(1)

    print("✅ Kali Linux detected")
    print("🔄 Starting dependency installation...\n")

    # Install all tools
    tool_results = manager.install_all_tools()

    # Install Python dependencies
    python_results = manager.install_python_dependencies()

    # Generate and save report
    manager.save_report("fern_installation_report.txt")

    # Final summary
    successful_tools = sum(1 for r in tool_results.values() if r)
    successful_python = sum(1 for r in python_results.values() if r)

    print("\n" + "=" * 50)
    print("🎉 Installation Complete!")
    print(f"   Tools installed: {successful_tools}/{len(tool_results)}")
    print(f"   Python packages: {successful_python}/{len(python_results)}")

    total_successful = successful_tools + successful_python
    total_total = len(tool_results) + len(python_results)

    if successful_tools == len(tool_results) and successful_python == len(python_results):
        print("   ✅ All dependencies successfully installed!")
        print("   🚀 Fern WiFi Cracker is ready to use!")
        print("\nTo start Fern WiFi Cracker:")
        print("   python3 execute.py")
        print("\nTo verify installations:")
        print("   python3 -c \"from core.kali_dependency_manager import KaliDependencyManager; KaliDependencyManager().verify_all_tools()\"")
    else:
        print("   ⚠️  Some dependencies may need manual installation.")
        print("   📄 Check 'fern_installation_report.txt' for details.")
        print("\nTo troubleshoot:")
        print("   1. Check internet connection")
        print("   2. Run 'sudo apt update' manually")
        print("   3. Try installing failed packages individually")
        print("   4. Check 'fern_installation_report.txt' for specific errors")

    print("\n📋 Installation report saved to: fern_installation_report.txt")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation interrupted by user")
        print("   You can resume by running this script again")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Installation failed with error: {e}")
        print("   Please check your system and try again")
        sys.exit(1)