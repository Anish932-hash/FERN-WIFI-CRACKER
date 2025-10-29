#!/usr/bin/env python3
"""
Wifite Integration for Fern WiFi Cracker
Automated wireless auditing tool integration
"""

import os
import re
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Union

class WifiteIntegration:
    """Advanced Wifite integration for automated wireless attacks"""

    def __init__(self):
        self.wifite_available = self._check_wifite()
        self.wifite2_available = self._check_wifite2()
        self.current_process = None
        self.attack_results = {}

    def _check_wifite(self) -> bool:
        """Check if original wifite is available"""
        try:
            result = subprocess.run(['wifite', '--version'],
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _check_wifite2(self) -> bool:
        """Check if wifite2 (python version) is available"""
        try:
            result = subprocess.run(['python3', '-c', 'import wifite'],
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def get_available_interfaces(self) -> List[str]:
        """Get list of available wireless interfaces"""
        try:
            result = subprocess.run(['iwconfig'],
                                  capture_output=True, text=True, timeout=10)
            interfaces = re.findall(r'(\w+)\s+IEEE 802\.11', result.stdout)
            return interfaces
        except subprocess.TimeoutExpired:
            return []

    def start_automated_attack(self, interface: str, options: Dict = None) -> subprocess.Popen:
        """Start automated Wifite attack"""
        if not (self.wifite_available or self.wifite2_available):
            raise RuntimeError("Wifite not available")

        cmd = []

        if self.wifite2_available:
            cmd = ['python3', '-c', 'from wifite import main; main()']
        else:
            cmd = ['wifite']

        # Add interface
        cmd.extend(['-i', interface])

        # Add custom options
        if options:
            if options.get('aggressive', False):
                cmd.append('--aggressive')
            if options.get('wps_only', False):
                cmd.append('--wps-only')
            if options.get('wep_only', False):
                cmd.append('--wep-only')
            if options.get('wpa_only', False):
                cmd.append('--wpa-only')
            if options.get('no_wps', False):
                cmd.append('--no-wps')
            if options.get('pixie_dust', False):
                cmd.append('--pixie')
            if options.get('bully', False):
                cmd.append('--bully')

            # Dictionary file
            if options.get('dictionary'):
                cmd.extend(['-dict', options['dictionary']])

            # Target specific BSSID
            if options.get('bssid'):
                cmd.extend(['-b', options['bssid']])

            # Channel
            if options.get('channel'):
                cmd.extend(['-c', str(options['channel'])])

            # ESSID
            if options.get('essid'):
                cmd.extend(['-e', options['essid']])

        # Start the process
        self.current_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        return self.current_process

    def monitor_attack_progress(self, callback=None) -> None:
        """Monitor attack progress and call callback with updates"""
        if not self.current_process:
            return

        def monitor():
            while self.current_process and self.current_process.poll() is None:
                if self.current_process.stdout:
                    line = self.current_process.stdout.readline()
                    if line:
                        # Parse progress information
                        progress_info = self._parse_progress(line.strip())
                        if progress_info and callback:
                            callback(progress_info)
                time.sleep(0.1)

            # Process completed
            if callback:
                callback({'status': 'completed'})

        threading.Thread(target=monitor, daemon=True).start()

    def _parse_progress(self, line: str) -> Optional[Dict]:
        """Parse Wifite output for progress information"""
        # Look for various progress indicators
        patterns = {
            'target_found': r'\[\+\] (\d+) target\(s\) found',
            'attacking': r'\[\+\] attacking (\w+) on channel (\d+) \(([\w\s]+)\)',
            'wps_pin': r'\[\+\] WPS PIN found: (\d+)',
            'wpa_key': r'\[\+\] WPA key found: ([^\s]+)',
            'wep_key': r'\[\+\] WEP key found: ([^\s]+)',
            'progress': r'(\d+)% complete',
            'attempts': r'(\d+) attempts remaining'
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                if key == 'target_found':
                    return {'type': 'targets_found', 'count': int(match.group(1))}
                elif key == 'attacking':
                    return {
                        'type': 'attacking',
                        'encryption': match.group(1),
                        'channel': int(match.group(2)),
                        'bssid': match.group(3)
                    }
                elif key in ['wps_pin', 'wpa_key', 'wep_key']:
                    return {'type': 'key_found', 'key_type': key, 'key': match.group(1)}
                elif key == 'progress':
                    return {'type': 'progress', 'percentage': int(match.group(1))}
                elif key == 'attempts':
                    return {'type': 'attempts', 'remaining': int(match.group(1))}

        return None

    def stop_attack(self) -> bool:
        """Stop current Wifite attack"""
        if self.current_process:
            try:
                self.current_process.terminate()
                # Wait a bit for graceful termination
                self.current_process.wait(timeout=5)
                return True
            except subprocess.TimeoutExpired:
                # Force kill if needed
                self.current_process.kill()
                return True
            except Exception:
                return False
        return False

    def get_attack_results(self) -> Dict:
        """Get results from completed attacks"""
        if self.current_process and self.current_process.poll() is not None:
            # Read any remaining output
            if self.current_process.stdout:
                remaining = self.current_process.stdout.read()
                if remaining:
                    # Parse final results
                    pass

        return self.attack_results

    def list_available_attacks(self) -> List[str]:
        """List available attack types in Wifite"""
        attacks = []

        if self.wifite_available or self.wifite2_available:
            attacks.extend([
                'WPS (Pixie Dust)',
                'WPS (PIN Brute Force)',
                'WPA Handshake Capture',
                'WPA Dictionary Attack',
                'WEP Attacks',
                'WPA PMKID Attack'
            ])

        return attacks

    def configure_attack(self, attack_type: str, **kwargs) -> Dict:
        """Configure specific attack parameters"""
        config = {}

        if attack_type == 'WPS (Pixie Dust)':
            config = {
                'wps_only': True,
                'pixie_dust': True,
                'aggressive': True
            }
        elif attack_type == 'WPS (PIN Brute Force)':
            config = {
                'wps_only': True,
                'bully': True,
                'aggressive': True
            }
        elif attack_type == 'WPA Dictionary Attack':
            config = {
                'wpa_only': True,
                'dictionary': kwargs.get('dictionary', '/usr/share/wordlists/rockyou.txt'),
                'aggressive': True
            }
        elif attack_type == 'WEP Attacks':
            config = {
                'wep_only': True,
                'aggressive': True
            }
        elif attack_type == 'WPA PMKID Attack':
            config = {
                'wpa_only': True,
                'pmkid': True,
                'aggressive': True
            }

        # Apply any additional kwargs
        config.update(kwargs)
        return config

class WifiteController:
    """Controller for managing multiple Wifite instances"""

    def __init__(self):
        self.wifite = WifiteIntegration()
        self.active_attacks = {}

    def start_targeted_attack(self, interface: str, bssid: str,
                            attack_type: str, **kwargs) -> str:
        """Start a targeted attack on specific BSSID"""
        attack_id = f"{bssid}_{int(time.time())}"

        config = self.wifite.configure_attack(attack_type, bssid=bssid, **kwargs)

        try:
            process = self.wifite.start_automated_attack(interface, config)
            self.active_attacks[attack_id] = {
                'process': process,
                'bssid': bssid,
                'attack_type': attack_type,
                'start_time': time.time()
            }

            # Start monitoring
            self.wifite.monitor_attack_progress(
                lambda info: self._handle_progress_update(attack_id, info)
            )

            return attack_id

        except Exception as e:
            raise RuntimeError(f"Failed to start attack: {e}")

    def _handle_progress_update(self, attack_id: str, info: Dict):
        """Handle progress updates from attacks"""
        if attack_id in self.active_attacks:
            attack_info = self.active_attacks[attack_id]
            attack_info['last_update'] = time.time()

            if info.get('type') == 'key_found':
                attack_info['result'] = info
                attack_info['status'] = 'completed'
            elif info.get('type') == 'progress':
                attack_info['progress'] = info.get('percentage', 0)

    def stop_attack(self, attack_id: str) -> bool:
        """Stop specific attack"""
        if attack_id in self.active_attacks:
            success = self.wifite.stop_attack()
            if success:
                self.active_attacks[attack_id]['status'] = 'stopped'
            return success
        return False

    def get_attack_status(self, attack_id: str) -> Optional[Dict]:
        """Get status of specific attack"""
        return self.active_attacks.get(attack_id)

    def cleanup_completed_attacks(self):
        """Clean up completed/stopped attacks"""
        current_time = time.time()
        to_remove = []

        for attack_id, info in self.active_attacks.items():
            if info.get('status') in ['completed', 'stopped']:
                # Keep completed attacks for 5 minutes
                if current_time - info.get('last_update', 0) > 300:
                    to_remove.append(attack_id)

        for attack_id in to_remove:
            del self.active_attacks[attack_id]

# Example usage:
if __name__ == "__main__":
    wifite = WifiteIntegration()

    if wifite.wifite_available or wifite.wifite2_available:
        print("Wifite available!")
        interfaces = wifite.get_available_interfaces()
        print(f"Available interfaces: {interfaces}")

        attacks = wifite.list_available_attacks()
        print(f"Available attacks: {attacks}")
    else:
        print("Wifite not found. Please install wifite or wifite2.")