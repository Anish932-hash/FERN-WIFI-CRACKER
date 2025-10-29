#!/usr/bin/env python3
"""
Kali Linux Dependency Manager for Fern WiFi Cracker
Automatically installs and manages all required tools for Kali Linux
"""

import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

class KaliDependencyManager:
    """Manages Kali Linux dependencies for Fern WiFi Cracker"""

    def __init__(self):
        self.is_kali = self._detect_kali_linux()
        self.installed_tools = {}
        self.required_tools = {
            # Core WiFi cracking tools
            'aircrack-ng': {
                'package': 'aircrack-ng',
                'description': 'Complete suite of WiFi cracking tools',
                'tools': ['aircrack-ng', 'airodump-ng', 'aireplay-ng', 'airmon-ng',
                         'airbase-ng', 'airdecap-ng', 'airdecloak-ng']
            },
            'wifite': {
                'package': 'wifite',
                'description': 'Automated wireless auditor',
                'tools': ['wifite']
            },
            'cowpatty': {
                'package': 'cowpatty',
                'description': 'WPA-PSK dictionary attack tool',
                'tools': ['cowpatty', 'genpmk']
            },
            'crunch': {
                'package': 'crunch',
                'description': 'Wordlist generator',
                'tools': ['crunch']
            },
            'macchanger': {
                'package': 'macchanger',
                'description': 'MAC address spoofing tool',
                'tools': ['macchanger']
            },
            'mdk3': {
                'package': 'mdk3',
                'description': 'WiFi stress testing tool',
                'tools': ['mdk3']
            },
            'mdk4': {
                'package': 'mdk4',
                'description': 'Advanced WiFi testing tool',
                'tools': ['mdk4']
            },
            'kismet': {
                'package': 'kismet',
                'description': 'Wireless network detector and sniffer',
                'tools': ['kismet', 'kismet_server', 'kismet_client']
            },
            'reaver': {
                'package': 'reaver',
                'description': 'WPS brute force attack tool',
                'tools': ['reaver', 'walsh', 'wash']
            },
            'pixiewps': {
                'package': 'pixiewps',
                'description': 'WPS offline PIN recovery tool',
                'tools': ['pixiewps']
            },
            'hashcat': {
                'package': 'hashcat',
                'description': 'Advanced password recovery utility',
                'tools': ['hashcat']
            },
            'john': {
                'package': 'john',
                'description': 'John the Ripper password cracker',
                'tools': ['john', 'johnny']
            },
            'pyrit': {
                'package': 'pyrit',
                'description': 'WPA/WPA2-PSK attack tool',
                'tools': ['pyrit']
            },
            'tshark': {
                'package': 'tshark',
                'description': 'Wireshark CLI packet analyzer',
                'tools': ['tshark']
            },
            'bettercap': {
                'package': 'bettercap',
                'description': 'MITM framework',
                'tools': ['bettercap']
            },
            'hostapd': {
                'package': 'hostapd',
                'description': 'User space IEEE 802.11 AP and authentication server',
                'tools': ['hostapd']
            },
            'dnsmasq': {
                'package': 'dnsmasq',
                'description': 'DNS and DHCP server',
                'tools': ['dnsmasq']
            },
            'wifiphisher': {
                'package': 'wifiphisher',
                'description': 'Automated phishing attacks against WiFi networks',
                'tools': ['wifiphisher']
            },
            'fluxion': {
                'package': 'fluxion',
                'description': 'WiFi social engineering tool',
                'tools': ['fluxion']
            }
        }

        # Python dependencies
        self.python_packages = [
            'scapy', 'PyQt5', 'requests', 'psutil', 'netifaces'
        ]

    def _detect_kali_linux(self) -> bool:
        """Detect if running on Kali Linux"""
        try:
            with open('/etc/os-release', 'r') as f:
                content = f.read().lower()
                return 'kali' in content
        except FileNotFoundError:
            return False

    def _run_command(self, command: str, sudo: bool = False) -> Tuple[int, str, str]:
        """Run a shell command and return exit code, stdout, stderr"""
        if sudo and os.geteuid() != 0:
            command = f"sudo {command}"

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)

    def check_tool_availability(self, tool_name: str) -> bool:
        """Check if a specific tool is available"""
        try:
            result = subprocess.run(
                [tool_name, '--help'],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def update_package_lists(self) -> bool:
        """Update apt package lists"""
        print("🔄 Updating package lists...")
        exit_code, stdout, stderr = self._run_command("apt update", sudo=True)
        if exit_code == 0:
            print("✅ Package lists updated successfully")
            return True
        else:
            print(f"❌ Failed to update package lists: {stderr}")
            return False

    def install_package(self, package_name: str, description: str = "") -> bool:
        """Install a specific package"""
        desc = f" ({description})" if description else ""
        print(f"📦 Installing {package_name}{desc}...")

        exit_code, stdout, stderr = self._run_command(
            f"apt install -y {package_name}",
            sudo=True
        )

        if exit_code == 0:
            print(f"✅ Successfully installed {package_name}")
            return True
        else:
            print(f"❌ Failed to install {package_name}: {stderr}")
            return False

    def install_python_package(self, package_name: str) -> bool:
        """Install a Python package via pip"""
        print(f"🐍 Installing Python package {package_name}...")

        exit_code, stdout, stderr = self._run_command(
            f"pip3 install {package_name}",
            sudo=True
        )

        if exit_code == 0:
            print(f"✅ Successfully installed Python package {package_name}")
            return True
        else:
            print(f"❌ Failed to install Python package {package_name}: {stderr}")
            return False

    def check_and_install_tool(self, tool_name: str) -> bool:
        """Check if tool is available, install if not"""
        if tool_name not in self.required_tools:
            print(f"⚠️  Tool '{tool_name}' not in known tools list")
            return False

        tool_info = self.required_tools[tool_name]

        # Check if any of the tools in this package are available
        package_available = any(
            self.check_tool_availability(tool)
            for tool in tool_info['tools']
        )

        if package_available:
            print(f"✅ {tool_name} is already installed")
            self.installed_tools[tool_name] = True
            return True

        # Install the package
        success = self.install_package(
            tool_info['package'],
            tool_info['description']
        )

        if success:
            # Verify installation
            package_available = any(
                self.check_tool_availability(tool)
                for tool in tool_info['tools']
            )

            if package_available:
                self.installed_tools[tool_name] = True
                return True
            else:
                print(f"❌ {tool_name} installation verification failed")
                return False
        else:
            self.installed_tools[tool_name] = False
            return False

    def install_all_tools(self, tools_list: Optional[List[str]] = None) -> Dict[str, bool]:
        """Install all required tools or a specific list"""
        if not self.is_kali:
            print("❌ This dependency manager is designed for Kali Linux only")
            print("   Please run this on a Kali Linux system")
            return {}

        if not self.update_package_lists():
            print("❌ Cannot proceed without updating package lists")
            return {}

        tools_to_install = tools_list if tools_list else list(self.required_tools.keys())

        results = {}
        successful = 0
        total = len(tools_to_install)

        print(f"\n🚀 Starting installation of {total} tools...\n")

        for i, tool_name in enumerate(tools_to_install, 1):
            print(f"[{i}/{total}] Installing {tool_name}...")
            success = self.check_and_install_tool(tool_name)
            results[tool_name] = success
            if success:
                successful += 1

        print(f"\n📊 Installation Summary:")
        print(f"   ✅ Successfully installed: {successful}/{total}")
        print(f"   ❌ Failed to install: {total - successful}/{total}")

        return results

    def install_python_dependencies(self) -> Dict[str, bool]:
        """Install required Python packages"""
        print("\n🐍 Installing Python dependencies...")

        results = {}
        successful = 0

        for package in self.python_packages:
            success = self.install_python_package(package)
            results[package] = success
            if success:
                successful += 1

        print(f"\n📊 Python packages installed: {successful}/{len(self.python_packages)}")
        return results

    def verify_all_tools(self) -> Dict[str, bool]:
        """Verify all tools are properly installed and working"""
        print("\n🔍 Verifying tool installations...")

        verification_results = {}

        for tool_name, tool_info in self.required_tools.items():
            tools_available = all(
                self.check_tool_availability(tool)
                for tool in tool_info['tools']
            )
            verification_results[tool_name] = tools_available

            status = "✅" if tools_available else "❌"
            print(f"   {status} {tool_name}")

        return verification_results

    def get_installation_status(self) -> Dict[str, Dict]:
        """Get detailed installation status"""
        status = {}

        for tool_name, tool_info in self.required_tools.items():
            tool_status = {
                'installed': False,
                'available_tools': [],
                'missing_tools': []
            }

            for tool in tool_info['tools']:
                if self.check_tool_availability(tool):
                    tool_status['available_tools'].append(tool)
                else:
                    tool_status['missing_tools'].append(tool)

            tool_status['installed'] = len(tool_status['available_tools']) > 0
            status[tool_name] = tool_status

        return status

    def create_installation_report(self) -> str:
        """Create a detailed installation report"""
        status = self.get_installation_status()

        report = []
        report.append("📋 Fern WiFi Cracker - Kali Linux Installation Report")
        report.append("=" * 60)
        report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        total_tools = len(status)
        installed_tools = sum(1 for s in status.values() if s['installed'])

        report.append(f"Overall Status: {installed_tools}/{total_tools} tools installed")
        report.append("")

        for tool_name, tool_status in status.items():
            status_icon = "✅" if tool_status['installed'] else "❌"
            report.append(f"{status_icon} {tool_name}")

            if tool_status['available_tools']:
                report.append(f"   Available: {', '.join(tool_status['available_tools'])}")

            if tool_status['missing_tools']:
                report.append(f"   Missing: {', '.join(tool_status['missing_tools'])}")

            report.append("")

        return "\n".join(report)

    def save_report(self, filename: str = "fern_installation_report.txt") -> bool:
        """Save installation report to file"""
        try:
            report = self.create_installation_report()
            with open(filename, 'w') as f:
                f.write(report)
            print(f"📄 Report saved to {filename}")
            return True
        except Exception as e:
            print(f"❌ Failed to save report: {e}")
            return False

def main():
    """Main function for command-line usage"""
    manager = KaliDependencyManager()

    if not manager.is_kali:
        print("❌ This script is designed for Kali Linux only!")
        print("   Please run this on a Kali Linux system.")
        sys.exit(1)

    print("🛠️  Fern WiFi Cracker - Kali Linux Dependency Manager")
    print("=" * 55)

    # Check if running as root
    if os.geteuid() != 0:
        print("⚠️  Some operations require root privileges.")
        print("   You may be prompted for sudo password during installation.\n")

    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Install Fern WiFi Cracker dependencies on Kali Linux")
    parser.add_argument('--verify-only', action='store_true',
                       help='Only verify current installations, do not install')
    parser.add_argument('--tools', nargs='+',
                       help='Install only specific tools (space-separated)')
    parser.add_argument('--report', action='store_true',
                       help='Generate and save installation report')
    parser.add_argument('--python-only', action='store_true',
                       help='Install only Python dependencies')

    args = parser.parse_args()

    if args.python_only:
        print("🐍 Installing Python dependencies only...")
        results = manager.install_python_dependencies()
        successful = sum(1 for r in results.values() if r)
        print(f"\n✅ Python installation complete: {successful}/{len(results)} packages installed")
        return

    if args.verify_only:
        print("🔍 Verifying current tool installations...")
        verification = manager.verify_all_tools()
        installed = sum(1 for v in verification.values() if v)
        total = len(verification)
        print(f"\n📊 Verification complete: {installed}/{total} tools available")
        return

    # Install tools
    tools_to_install = args.tools if args.tools else None
    results = manager.install_all_tools(tools_to_install)

    # Install Python dependencies
    print("\n🐍 Installing Python dependencies...")
    python_results = manager.install_python_dependencies()

    # Generate report if requested
    if args.report:
        manager.save_report()

    # Final summary
    successful_tools = sum(1 for r in results.values() if r)
    successful_python = sum(1 for r in python_results.values() if r)

    print("\n" + "=" * 55)
    print("🎉 Installation Complete!")
    print(f"   Tools: {successful_tools}/{len(results)} installed")
    print(f"   Python packages: {successful_python}/{len(python_results)} installed")

    if successful_tools == len(results) and successful_python == len(python_results):
        print("   ✅ All dependencies successfully installed!")
        print("   🚀 Fern WiFi Cracker is ready to use!")
    else:
        print("   ⚠️  Some dependencies may need manual installation.")
        print("   📄 Check the installation report for details.")

if __name__ == "__main__":
    main()