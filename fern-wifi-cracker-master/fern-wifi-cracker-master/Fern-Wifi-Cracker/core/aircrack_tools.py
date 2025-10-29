#!/usr/bin/env python3
"""
Advanced Aircrack-ng Suite Integration for Fern WiFi Cracker
Provides comprehensive integration with all Aircrack-ng tools
"""

import os
import re
import time
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

class AircrackSuite:
    """Comprehensive Aircrack-ng suite integration"""

    def __init__(self, interface: Optional[str] = None):
        self.interface = interface
        self.monitor_interface = None
        self.tools_status = self._check_tools_availability()

    def _check_tools_availability(self) -> Dict[str, bool]:
        """Check which Aircrack-ng tools are available"""
        tools = [
            'aircrack-ng', 'airodump-ng', 'aireplay-ng', 'airmon-ng',
            'airbase-ng', 'airdecap-ng', 'airdecloak-ng', 'airolib-ng',
            'airserv-ng', 'buddy-ng', 'easside-ng', 'tkiptun-ng', 'wesside-ng'
        ]

        status = {}
        for tool in tools:
            try:
                result = subprocess.run([tool, '--help'],
                                      capture_output=True,
                                      timeout=5)
                status[tool] = result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError):
                status[tool] = False

        return status

    def enable_monitor_mode(self, interface: str) -> Optional[str]:
        """Enable monitor mode on specified interface"""
        if not self.tools_status.get('airmon-ng', False):
            return None

        try:
            # Kill conflicting processes
            subprocess.run(['airmon-ng', 'check', 'kill'],
                         capture_output=True, timeout=10)

            # Start monitor mode
            result = subprocess.run(['airmon-ng', 'start', interface],
                                  capture_output=True, text=True, timeout=15)

            if result.returncode == 0:
                # Extract monitor interface name
                match = re.search(r'(\w+mon|\w+)', result.stdout)
                if match:
                    self.monitor_interface = match.group(1)
                    return self.monitor_interface

        except subprocess.TimeoutExpired:
            pass

        return None

    def disable_monitor_mode(self, interface: str) -> bool:
        """Disable monitor mode"""
        if not self.tools_status.get('airmon-ng', False):
            return False

        try:
            result = subprocess.run(['airmon-ng', 'stop', interface],
                                  capture_output=True, timeout=10)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False

    def scan_networks(self, interface: str, channel: int = None,
                     output_file: str = None) -> subprocess.Popen:
        """Start network scanning with airodump-ng"""
        if not self.tools_status.get('airodump-ng', False):
            return None

        cmd = ['airodump-ng', '--write-interval', '1', '--output-format', 'csv']

        if channel:
            cmd.extend(['--channel', str(channel)])

        if output_file:
            cmd.extend(['--write', output_file])

        cmd.append(interface)

        return subprocess.Popen(cmd, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

    def deauthenticate_client(self, bssid: str, client_mac: str,
                            interface: str, count: int = 5) -> bool:
        """Deauthenticate a client using aireplay-ng"""
        if not self.tools_status.get('aireplay-ng', False):
            return False

        try:
            cmd = ['aireplay-ng', '-0', str(count), '-a', bssid, '-c', client_mac, interface]
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False

    def fake_authentication(self, bssid: str, interface: str,
                          essid: str = None) -> subprocess.Popen:
        """Perform fake authentication"""
        if not self.tools_status.get('aireplay-ng', False):
            return None

        cmd = ['aireplay-ng', '-1', '0', '-a', bssid]
        if essid:
            cmd.extend(['-e', essid])
        cmd.append(interface)

        return subprocess.Popen(cmd, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

    def arp_replay_attack(self, bssid: str, interface: str) -> subprocess.Popen:
        """Perform ARP replay attack"""
        if not self.tools_status.get('aireplay-ng', False):
            return None

        cmd = ['aireplay-ng', '-3', '-b', bssid, interface]
        return subprocess.Popen(cmd, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

    def chopchop_attack(self, interface: str) -> subprocess.Popen:
        """Perform Chop-Chop attack"""
        if not self.tools_status.get('aireplay-ng', False):
            return None

        cmd = ['aireplay-ng', '-4', '-F', interface]
        return subprocess.Popen(cmd, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

    def fragmentation_attack(self, bssid: str, interface: str) -> subprocess.Popen:
        """Perform fragmentation attack"""
        if not self.tools_status.get('aireplay-ng', False):
            return None

        cmd = ['aireplay-ng', '-5', '-F', '-b', bssid, interface]
        return subprocess.Popen(cmd, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

    def create_rogue_ap(self, essid: str, channel: int, interface: str) -> subprocess.Popen:
        """Create a rogue access point using airbase-ng"""
        if not self.tools_status.get('airbase-ng', False):
            return None

        cmd = ['airbase-ng', '-e', essid, '-c', str(channel), interface]
        return subprocess.Popen(cmd, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

    def decrypt_wep_packets(self, capture_file: str, key: str,
                          output_file: str = None) -> bool:
        """Decrypt WEP packets using airdecap-ng"""
        if not self.tools_status.get('airdecap-ng', False):
            return False

        cmd = ['airdecap-ng', '-w', key, capture_file]
        if output_file:
            cmd.extend(['-o', output_file])

        try:
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False

    def decrypt_wpa_packets(self, capture_file: str, essid: str, key: str,
                          output_file: str = None) -> bool:
        """Decrypt WPA packets using airdecap-ng"""
        if not self.tools_status.get('airdecap-ng', False):
            return False

        cmd = ['airdecap-ng', '-p', essid, '-k', key, capture_file]
        if output_file:
            cmd.extend(['-o', output_file])

        try:
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False

    def reveal_cloaked_ssid(self, capture_file: str) -> Optional[str]:
        """Reveal cloaked SSID using airdecloak-ng"""
        if not self.tools_status.get('airdecloak-ng', False):
            return None

        try:
            result = subprocess.run(['airdecloak-ng', capture_file],
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                # Parse output to find revealed SSID
                match = re.search(r'SSID:\s*(.+)', result.stdout)
                if match:
                    return match.group(1).strip()
        except subprocess.TimeoutExpired:
            pass

        return None

    def test_injection_capabilities(self, interface: str) -> Dict[str, bool]:
        """Test injection capabilities using aireplay-ng"""
        capabilities = {
            'injection_working': False,
            'quality': 'Unknown'
        }

        if not self.tools_status.get('aireplay-ng', False):
            return capabilities

        try:
            result = subprocess.run(['aireplay-ng', '-9', interface],
                                  capture_output=True, text=True, timeout=30)

            if 'Injection is working' in result.stdout:
                capabilities['injection_working'] = True
                # Parse quality information
                match = re.search(r'(\d+/\d+)', result.stdout)
                if match:
                    capabilities['quality'] = match.group(1)

        except subprocess.TimeoutExpired:
            pass

        return capabilities

    def get_interface_info(self) -> Dict[str, str]:
        """Get detailed interface information"""
        info = {}

        try:
            result = subprocess.run(['iwconfig'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                # Parse iwconfig output
                interfaces = re.findall(r'(\w+)\s+IEEE', result.stdout)
                info['wireless_interfaces'] = interfaces
        except subprocess.TimeoutExpired:
            pass

        return info

    def channel_hop(self, interface: str, channels: List[int] = None) -> None:
        """Perform channel hopping for better scanning"""
        if channels is None:
            channels = list(range(1, 15))  # Default 2.4GHz channels

        def hop():
            while True:
                for channel in channels:
                    try:
                        subprocess.run(['iwconfig', interface, 'channel', str(channel)],
                                     capture_output=True, timeout=1)
                        time.sleep(0.5)
                    except subprocess.TimeoutExpired:
                        continue

        threading.Thread(target=hop, daemon=True).start()

class AirmonManager:
    """Advanced airmon-ng management"""

    def __init__(self):
        self.airmon_available = self._check_airmon()

    def _check_airmon(self) -> bool:
        try:
            result = subprocess.run(['airmon-ng', '--help'],
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def get_interface_status(self) -> Dict[str, str]:
        """Get status of all wireless interfaces"""
        status = {}

        if not self.airmon_available:
            return status

        try:
            result = subprocess.run(['airmon-ng'],
                                  capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'mon' in line or 'wlan' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            interface = parts[0]
                            mode = parts[1] if len(parts) > 1 else 'Unknown'
                            status[interface] = mode

        except subprocess.TimeoutExpired:
            pass

        return status

    def kill_conflicting_processes(self) -> bool:
        """Kill processes that interfere with monitor mode"""
        if not self.airmon_available:
            return False

        try:
            result = subprocess.run(['airmon-ng', 'check', 'kill'],
                                  capture_output=True, timeout=15)
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False

# Usage example:
if __name__ == "__main__":
    suite = AircrackSuite()
    print("Available tools:", suite.tools_status)

    # Check interface status
    airmon = AirmonManager()
    print("Interface status:", airmon.get_interface_status())