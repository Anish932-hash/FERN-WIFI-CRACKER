# Fern WiFi Cracker - Kali Linux Setup Guide

## 🚀 Quick Start for Kali Linux

Fern WiFi Cracker has been enhanced with advanced capabilities and all requested tools. This guide will help you get everything working on Kali Linux.

## 📋 Prerequisites

- **Kali Linux** (2020.1 or later recommended)
- **Root privileges** (sudo access)
- **Internet connection** for downloading dependencies
- **Compatible wireless adapter** (supports monitor mode)

## 🛠️ One-Command Installation

### Step 1: Run the Automated Installer

```bash
cd Fern-Wifi-Cracker
sudo python3 install_dependencies.py
```

This will automatically:
- ✅ Detect Kali Linux environment
- ✅ Update package repositories
- ✅ Install all required tools
- ✅ Install Python dependencies
- ✅ Generate installation report

### Step 2: Verify Installation

```bash
python3 -c "from core.kali_dependency_manager import KaliDependencyManager; dm = KaliDependencyManager(); print('Tools available:', sum(dm.verify_all_tools().values()))"
```

## 📦 Tools Installed

The installer will install all these tools:

### Core WiFi Cracking Tools
- **Aircrack-ng Suite**: Complete WiFi cracking toolkit
  - `airodump-ng`, `aireplay-ng`, `aircrack-ng`, `airmon-ng`
  - `airbase-ng`, `airdecap-ng`, `airdecloak-ng`

- **Wifite**: Automated wireless auditor
- **Cowpatty**: WPA-PSK dictionary attacks + genpmk
- **Crunch**: Advanced wordlist generator
- **Macchanger**: MAC address spoofing
- **MDK3/MDK4**: WiFi stress testing and DoS attacks

### Advanced Tools
- **Kismet**: Passive wireless network detection
- **Reaver**: WPS brute force attacks
- **Pixiewps**: WPS offline PIN recovery
- **Hashcat**: GPU-accelerated password cracking
- **John the Ripper**: Alternative password cracker
- **Pyrit**: WPA/WPA2 attack enhancement

### Network Analysis Tools
- **Tshark**: Wireshark CLI for packet analysis
- **Bettercap**: MITM framework
- **Hostapd**: Software AP creation
- **Dnsmasq**: DHCP/DNS server for rogue APs

### Social Engineering Tools
- **Wifiphisher**: Automated phishing attacks
- **Fluxion**: Social engineering WPA attacks

## 🐍 Python Dependencies

The installer also installs:
- `scapy` - Packet manipulation
- `PyQt5` - GUI framework
- `requests` - HTTP requests
- `psutil` - System monitoring
- `netifaces` - Network interface info

## 🚀 Running Fern WiFi Cracker

### After Installation:

```bash
# Start Fern WiFi Cracker
sudo python3 execute.py
```

### Alternative Launch Methods:

```bash
# Direct execution
sudo ./execute.py

# With specific Python
sudo python3 execute.py
```

## 🔧 Manual Installation (If Automated Fails)

If the automated installer fails, install tools manually:

```bash
# Update system
sudo apt update

# Install core tools
sudo apt install -y aircrack-ng wifite cowpatty crunch macchanger kismet

# Install advanced tools
sudo apt install -y mdk3 mdk4 reaver pixiewps hashcat john pyrit

# Install network tools
sudo apt install -y tshark bettercap hostapd dnsmasq

# Install social engineering tools
sudo apt install -y wifiphisher fluxion

# Install Python dependencies
sudo pip3 install scapy PyQt5 requests psutil netifaces
```

## 🔍 Troubleshooting

### Common Issues:

#### 1. "Tool not found" errors
```bash
# Check if tools are installed
which aircrack-ng
which wifite

# Re-run installer
sudo python3 install_dependencies.py
```

#### 2. Permission errors
```bash
# Ensure you're running as root
sudo su

# Or use sudo with all commands
sudo python3 execute.py
```

#### 3. Wireless adapter issues
```bash
# Check wireless interfaces
iwconfig

# Enable monitor mode manually
sudo airmon-ng start wlan0

# Check monitor interface
iwconfig
```

#### 4. Python import errors
```bash
# Install missing Python packages
sudo pip3 install scapy PyQt5

# Check Python path
python3 -c "import sys; print(sys.path)"
```

### Installation Verification:

```bash
# Check all tools
python3 -c "
from core.kali_dependency_manager import KaliDependencyManager
dm = KaliDependencyManager()
results = dm.verify_all_tools()
installed = sum(results.values())
total = len(results)
print(f'Tools installed: {installed}/{total}')
for tool, available in results.items():
    status = '✅' if available else '❌'
    print(f'{status} {tool}')
"
```

## 📊 Installation Report

After installation, check `fern_installation_report.txt` for detailed status:

```
📋 Fern WiFi Cracker - Kali Linux Installation Report
============================================================
Generated: 2025-10-29 04:31:25

Overall Status: 15/15 tools installed

✅ aircrack-ng
   Available: aircrack-ng, airodump-ng, aireplay-ng, airmon-ng, airbase-ng, airdecap-ng, airdecloak-ng

✅ wifite
   Available: wifite

✅ cowpatty
   Available: cowpatty, genpmk

[... continues for all tools ...]
```

## 🎯 Advanced Features Now Available

With all tools installed, you now have access to:

### Enhanced WPA2 Cracking
- Dictionary attacks with Cowpatty
- GPU acceleration with Hashcat
- Hybrid attacks (Dictionary + Rules)
- PMK precomputation

### Advanced WPS Attacks
- PixieWPS offline recovery
- Reaver brute force
- Bully alternative implementation

### WiFi Stress Testing
- MDK3/MDK4 comprehensive attacks
- Deauthentication floods
- Beacon flooding
- Authentication DoS

### Passive Network Analysis
- Kismet wireless detection
- Tshark packet analysis
- Real-time monitoring

### Rogue Access Points
- Hostapd software APs
- Dnsmasq DHCP/DNS
- Bettercap MITM capabilities

### Social Engineering
- Wifiphisher automated phishing
- Fluxion social engineering attacks

## 🔐 Security Notes

- **Legal Use Only**: These tools are for authorized security testing
- **Ethical Use**: Obtain explicit permission before testing networks
- **Responsible Disclosure**: Report vulnerabilities appropriately
- **Educational Purpose**: Use for learning wireless security

## 📞 Support

If you encounter issues:

1. Check the installation report: `fern_installation_report.txt`
2. Verify Kali version: `cat /etc/os-release`
3. Check wireless adapter compatibility
4. Ensure root privileges for all operations

## 🎉 Success!

Once everything is installed and working, you'll have a comprehensive wireless security assessment toolkit with enterprise-level capabilities!

---

**Fern WiFi Cracker Team**
*Advanced Wireless Security Testing Framework*
