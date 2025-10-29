#!/usr/bin/env python3
"""
Macchanger Integration for Fern WiFi Cracker
Advanced MAC address spoofing capabilities
"""

import os
import re
import subprocess
import threading
import time
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

class MacchangerIntegration:
    """Advanced MAC address spoofing integration"""

    def __init__(self):
        self.macchanger_available = self._check_macchanger()
        self.current_interface = None
        self.original_macs = {}

    def _check_macchanger(self) -> bool:
        """Check if macchanger is available"""
        try:
            result = subprocess.run(['macchanger', '--version'],
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def get_current_mac(self, interface: str) -> Optional[str]:
        """Get current MAC address of interface"""
        try:
            result = subprocess.run(['cat', f'/sys/class/net/{interface}/address'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # Fallback using ifconfig/ip
        try:
            result = subprocess.run(['ip', 'link', 'show', interface],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                match = re.search(r'link/ether\s+([0-9a-f:]{17})', result.stdout, re.IGNORECASE)
                if match:
                    return match.group(1)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return None

    def backup_original_mac(self, interface: str) -> bool:
        """Backup original MAC address"""
        current_mac = self.get_current_mac(interface)
        if current_mac:
            self.original_macs[interface] = current_mac
            return True
        return False

    def restore_original_mac(self, interface: str) -> bool:
        """Restore original MAC address"""
        if interface in self.original_macs:
            return self.set_mac_address(interface, self.original_macs[interface])
        return False

    def set_mac_address(self, interface: str, mac_address: str) -> bool:
        """Set specific MAC address"""
        if not self.macchanger_available:
            return False

        if not self._validate_mac(mac_address):
            return False

        try:
            # Bring interface down
            subprocess.run(['ip', 'link', 'set', interface, 'down'],
                         capture_output=True, timeout=10)

            # Change MAC address
            result = subprocess.run(['macchanger', '-m', mac_address, interface],
                                  capture_output=True, timeout=15)

            # Bring interface up
            subprocess.run(['ip', 'link', 'set', interface, 'up'],
                         capture_output=True, timeout=10)

            return result.returncode == 0

        except subprocess.TimeoutExpired:
            return False

    def generate_random_mac(self, vendor_prefix: str = None) -> str:
        """Generate a random MAC address"""
        if vendor_prefix and len(vendor_prefix) == 8:  # XX:XX:XX format
            prefix = vendor_prefix.replace(':', '')
        else:
            # Generate completely random
            prefix = ''.join(random.choices('0123456789abcdef', k=6))

        # Ensure it's a unicast address (second bit of first byte should be 0)
        first_byte = int(prefix[:2], 16)
        first_byte &= 0xFE  # Clear multicast bit
        first_byte |= 0x02  # Set locally administered bit
        prefix = f"{first_byte:02x}{prefix[2:]}"

        suffix = ''.join(random.choices('0123456789abcdef', k=6))
        return f"{prefix[:2]}:{prefix[2:4]}:{prefix[4:6]}:{suffix[:2]}:{suffix[2:4]}:{suffix[4:6]}"

    def spoof_random_mac(self, interface: str) -> Optional[str]:
        """Spoof with a random MAC address"""
        random_mac = self.generate_random_mac()
        if self.set_mac_address(interface, random_mac):
            return random_mac
        return None

    def spoof_vendor_mac(self, interface: str, vendor_code: str) -> Optional[str]:
        """Spoof MAC with specific vendor prefix"""
        vendor_mac = self.generate_random_mac(vendor_code)
        if self.set_mac_address(interface, interface, vendor_mac):
            return vendor_mac
        return None

    def get_vendor_info(self, mac_address: str) -> Optional[Dict]:
        """Get vendor information for MAC address"""
        if not self._validate_mac(mac_address):
            return None

        # Extract OUI (first 3 bytes)
        oui = mac_address.replace(':', '')[:6].upper()

        # Common vendor mappings (could be expanded)
        vendors = {
            '001A11': {'vendor': 'Google', 'country': 'US'},
            '0022F1': {'vendor': 'Apple', 'country': 'US'},
            '0023DF': {'vendor': 'Apple', 'country': 'US'},
            '002436': {'vendor': 'Apple', 'country': 'US'},
            '002500': {'vendor': 'Apple', 'country': 'US'},
            '00254B': {'vendor': 'Apple', 'country': 'US'},
            '00264A': {'vendor': 'Apple', 'country': 'US'},
            '0026BB': {'vendor': 'Apple', 'country': 'US'},
            '0016CB': {'vendor': 'Apple', 'country': 'US'},
            '0017F2': {'vendor': 'Apple', 'country': 'US'},
            '0019E3': {'vendor': 'Apple', 'country': 'US'},
            '001B63': {'vendor': 'Apple', 'country': 'US'},
            '001EC2': {'vendor': 'Apple', 'country': 'US'},
            '001F5B': {'vendor': 'Apple', 'country': 'US'},
            '001FF3': {'vendor': 'Apple', 'country': 'US'},
            '002034': {'vendor': 'Apple', 'country': 'US'},
            '0020F2': {'vendor': 'Apple', 'country': 'US'},
            '002241': {'vendor': 'Apple', 'country': 'US'},
            '002312': {'vendor': 'Apple', 'country': 'US'},
            '002332': {'vendor': 'Apple', 'country': 'US'},
            '00236C': {'vendor': 'Apple', 'country': 'US'},
            '0023E8': {'vendor': 'Apple', 'country': 'US'},
            '0024D2': {'vendor': 'Apple', 'country': 'US'},
            '00254F': {'vendor': 'Apple', 'country': 'US'},
            '0025BC': {'vendor': 'Apple', 'country': 'US'},
            '002608': {'vendor': 'Apple', 'country': 'US'},
            '00264A': {'vendor': 'Apple', 'country': 'US'},
            '0026B0': {'vendor': 'Apple', 'country': 'US'},
            '0016C4': {'vendor': 'Cisco', 'country': 'US'},
            '00175A': {'vendor': 'Cisco', 'country': 'US'},
            '001839': {'vendor': 'Cisco', 'country': 'US'},
            '001B2A': {'vendor': 'Cisco', 'country': 'US'},
            '001C58': {'vendor': 'Cisco', 'country': 'US'},
            '001D4F': {'vendor': 'Cisco', 'country': 'US'},
            '001E7A': {'vendor': 'Cisco', 'country': 'US'},
            '001FCA': {'vendor': 'Cisco', 'country': 'US'},
            '00215C': {'vendor': 'Intel', 'country': 'US'},
            '00216B': {'vendor': 'Intel', 'country': 'US'},
            '0022FA': {'vendor': 'Intel', 'country': 'US'},
            '002314': {'vendor': 'Intel', 'country': 'US'},
            '0024D2': {'vendor': 'Intel', 'country': 'US'},
            '001F3B': {'vendor': 'Intel', 'country': 'US'},
            'A4C494': {'vendor': 'Intel', 'country': 'US'},
            'B8B81E': {'vendor': 'Intel', 'country': 'US'},
            '002268': {'vendor': 'Microsoft', 'country': 'US'},
            '00144F': {'vendor': 'Microsoft', 'country': 'US'},
            '0017FA': {'vendor': 'Microsoft', 'country': 'US'},
            '0019DB': {'vendor': 'Microsoft', 'country': 'US'},
            '001B8F': {'vendor': 'Microsoft', 'country': 'US'},
            '001DB7': {'vendor': 'Microsoft', 'country': 'US'},
            '001E8F': {'vendor': 'Microsoft', 'country': 'US'},
            '0021FE': {'vendor': 'Microsoft', 'country': 'US'},
            '00225D': {'vendor': 'Microsoft', 'country': 'US'},
            '002369': {'vendor': 'Microsoft', 'country': 'US'},
            '0023BE': {'vendor': 'Microsoft', 'country': 'US'},
            '00242E': {'vendor': 'Microsoft', 'country': 'US'},
            '002438': {'vendor': 'Microsoft', 'country': 'US'},
            '0024AF': {'vendor': 'Microsoft', 'country': 'US'},
            '002519': {'vendor': 'Microsoft', 'country': 'US'},
            '00252F': {'vendor': 'Microsoft', 'country': 'US'},
            '0025AD': {'vendor': 'Microsoft', 'country': 'US'},
            '0025E5': {'vendor': 'Microsoft', 'country': 'US'},
            '00265A': {'vendor': 'Microsoft', 'country': 'US'},
            'E0CB4E': {'vendor': 'Microsoft', 'country': 'US'},
        }

        return vendors.get(oui, {'vendor': 'Unknown', 'country': 'Unknown'})

    def _validate_mac(self, mac_address: str) -> bool:
        """Validate MAC address format"""
        pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
        return bool(pattern.match(mac_address))

    def list_interfaces(self) -> List[str]:
        """List available network interfaces"""
        try:
            result = subprocess.run(['ls', '/sys/class/net'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                interfaces = [iface for iface in result.stdout.strip().split('\n')
                            if iface and not iface.startswith('lo')]
                return interfaces
        except subprocess.TimeoutExpired:
            pass
        return []

    def get_interface_info(self, interface: str) -> Optional[Dict]:
        """Get detailed interface information"""
        info = {
            'name': interface,
            'mac_address': None,
            'status': 'unknown',
            'type': 'unknown'
        }

        # Get MAC address
        info['mac_address'] = self.get_current_mac(interface)

        # Get interface status
        try:
            result = subprocess.run(['ip', 'link', 'show', interface],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                if 'UP' in result.stdout:
                    info['status'] = 'up'
                else:
                    info['status'] = 'down'

                if 'LOOPBACK' in result.stdout:
                    info['type'] = 'loopback'
                elif 'ETHER' in result.stdout:
                    info['type'] = 'ethernet'
                elif 'WLAN' in result.stdout:
                    info['type'] = 'wireless'
        except subprocess.TimeoutExpired:
            pass

        return info

class AdvancedMacSpoofingController:
    """Advanced controller for MAC spoofing operations"""

    def __init__(self):
        self.macchanger = MacchangerIntegration()
        self.active_spoofs = {}

    def start_mac_rotation(self, interface: str, interval: int = 300) -> str:
        """Start automatic MAC address rotation"""
        spoof_id = f"rotation_{interface}_{int(time.time())}"

        def rotate_mac():
            while spoof_id in self.active_spoofs:
                new_mac = self.macchanger.spoof_random_mac(interface)
                if new_mac:
                    self.active_spoofs[spoof_id]['current_mac'] = new_mac
                    self.active_spoofs[spoof_id]['last_change'] = time.time()
                time.sleep(interval)

        if self.macchanger.backup_original_mac(interface):
            thread = threading.Thread(target=rotate_mac, daemon=True)
            thread.start()

            self.active_spoofs[spoof_id] = {
                'interface': interface,
                'type': 'rotation',
                'interval': interval,
                'start_time': time.time(),
                'thread': thread,
                'status': 'running'
            }

            return spoof_id

        return None

    def spoof_specific_vendor(self, interface: str, vendor_code: str) -> Optional[str]:
        """Spoof MAC address for specific vendor"""
        spoof_id = f"vendor_{interface}_{int(time.time())}"

        if self.macchanger.backup_original_mac(interface):
            new_mac = self.macchanger.spoof_vendor_mac(interface, vendor_code)
            if new_mac:
                self.active_spoofs[spoof_id] = {
                    'interface': interface,
                    'type': 'vendor_spoof',
                    'vendor_code': vendor_code,
                    'new_mac': new_mac,
                    'start_time': time.time(),
                    'status': 'active'
                }
                return spoof_id

        return None

    def stop_spoofing(self, spoof_id: str) -> bool:
        """Stop MAC spoofing and restore original"""
        if spoof_id in self.active_spoofs:
            spoof_info = self.active_spoofs[spoof_id]
            interface = spoof_info['interface']

            # Stop rotation thread if running
            if spoof_info.get('thread'):
                spoof_info['status'] = 'stopped'
                del self.active_spoofs[spoof_id]

            # Restore original MAC
            success = self.macchanger.restore_original_mac(interface)
            return success

        return False

    def get_spoof_status(self, spoof_id: str) -> Optional[Dict]:
        """Get status of spoofing operation"""
        return self.active_spoofs.get(spoof_id)

class MacSpoofingAnalyzer:
    """Analyzer for MAC spoofing detection and analysis"""

    def __init__(self):
        self.macchanger = MacchangerIntegration()

    def detect_spoofing_attempts(self, interface: str, duration: int = 60) -> List[Dict]:
        """Monitor for MAC address changes on interface"""
        changes = []
        start_time = time.time()
        last_mac = self.macchanger.get_current_mac(interface)

        while time.time() - start_time < duration:
            current_mac = self.macchanger.get_current_mac(interface)
            if current_mac != last_mac:
                changes.append({
                    'timestamp': time.time(),
                    'old_mac': last_mac,
                    'new_mac': current_mac,
                    'interface': interface
                })
                last_mac = current_mac
            time.sleep(1)

        return changes

    def analyze_mac_pattern(self, mac_address: str) -> Dict:
        """Analyze MAC address patterns"""
        analysis = {
            'is_multicast': False,
            'is_locally_administered': False,
            'is_globally_unique': True,
            'vendor_info': None
        }

        if self.macchanger._validate_mac(mac_address):
            # Check multicast bit (least significant bit of first byte)
            first_byte = int(mac_address.replace(':', '')[:2], 16)
            analysis['is_multicast'] = bool(first_byte & 0x01)

            # Check locally administered bit (second least significant bit)
            analysis['is_locally_administered'] = bool(first_byte & 0x02)

            # Get vendor info
            analysis['vendor_info'] = self.macchanger.get_vendor_info(mac_address)

        return analysis

# Example usage:
if __name__ == "__main__":
    macchanger = MacchangerIntegration()

    if macchanger.macchanger_available:
        print("Macchanger is available!")

        # List interfaces
        interfaces = macchanger.list_interfaces()
        print(f"Available interfaces: {interfaces}")

        if interfaces:
            interface = interfaces[0]
            print(f"Using interface: {interface}")

            # Get current MAC
            current_mac = macchanger.get_current_mac(interface)
            print(f"Current MAC: {current_mac}")

            if current_mac:
                # Get vendor info
                vendor_info = macchanger.get_vendor_info(current_mac)
                print(f"Vendor info: {vendor_info}")

                # Generate random MAC
                random_mac = macchanger.generate_random_mac()
                print(f"Generated random MAC: {random_mac}")

                # Note: Actually changing MAC requires root privileges
                # and should be done carefully in real usage

    else:
        print("Macchanger not found. Please install macchanger package.")