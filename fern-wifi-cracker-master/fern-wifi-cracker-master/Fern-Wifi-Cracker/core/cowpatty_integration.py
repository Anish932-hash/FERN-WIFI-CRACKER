#!/usr/bin/env python3
"""
Cowpatty Integration for Fern WiFi Cracker
Advanced WPA-PSK dictionary attack tool
"""

import os
import re
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

class CowpattyIntegration:
    """Advanced Cowpatty integration for WPA-PSK attacks"""

    def __init__(self):
        self.cowpatty_available = self._check_cowpatty()
        self.genpmk_available = self._check_genpmk()
        self.current_process = None
        self.progress_info = {}

    def _check_cowpatty(self) -> bool:
        """Check if cowpatty is available"""
        try:
            result = subprocess.run(['cowpatty'],
                                  capture_output=True, timeout=5)
            return True  # cowpatty returns error without args, but is available
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _check_genpmk(self) -> bool:
        """Check if genpmk is available"""
        try:
            result = subprocess.run(['genpmk'],
                                  capture_output=True, timeout=5)
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def precompute_pmk(self, ssid: str, wordlist: str,
                      output_file: str = None) -> Optional[str]:
        """Precompute PMKs using genpmk for faster attacks"""
        if not self.genpmk_available:
            return None

        if not output_file:
            output_file = f'/tmp/fern-log/cowpatty_{ssid}_pmk.txt'

        try:
            cmd = ['genpmk', '-f', wordlist, '-d', output_file, '-s', ssid]
            result = subprocess.run(cmd, capture_output=True, timeout=300)  # 5 min timeout

            if result.returncode == 0 and os.path.exists(output_file):
                return output_file

        except subprocess.TimeoutExpired:
            pass

        return None

    def attack_with_pmk_file(self, pmk_file: str, capture_file: str,
                           ssid: str) -> subprocess.Popen:
        """Attack using precomputed PMK file"""
        if not self.cowpatty_available:
            raise RuntimeError("Cowpatty not available")

        cmd = ['cowpatty', '-d', pmk_file, '-r', capture_file, '-s', ssid]

        self.current_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        return self.current_process

    def attack_with_wordlist(self, wordlist: str, capture_file: str,
                           ssid: str) -> subprocess.Popen:
        """Standard cowpatty attack with wordlist"""
        if not self.cowpatty_available:
            raise RuntimeError("Cowpatty not available")

        cmd = ['cowpatty', '-f', wordlist, '-r', capture_file, '-s', ssid]

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

            # Check final result
            if self.current_process and callback:
                result = self._get_final_result()
                if result:
                    callback(result)

        threading.Thread(target=monitor, daemon=True).start()

    def _parse_progress(self, line: str) -> Optional[Dict]:
        """Parse cowpatty output for progress"""
        # Look for key found
        key_match = re.search(r'key\s*found\s*\[\s*(\d+)\s*\]', line, re.IGNORECASE)
        if key_match:
            return {
                'type': 'key_found',
                'key_index': int(key_match.group(1)),
                'status': 'success'
            }

        # Look for progress
        progress_match = re.search(r'(\d+)%', line)
        if progress_match:
            return {
                'type': 'progress',
                'percentage': int(progress_match.group(1))
            }

        # Look for passphrases tested
        tested_match = re.search(r'(\d+)\s+passphrases?\s+tested', line, re.IGNORECASE)
        if tested_match:
            return {
                'type': 'passphrases_tested',
                'count': int(tested_match.group(1))
            }

        return None

    def _get_final_result(self) -> Optional[Dict]:
        """Get final result from completed attack"""
        if not self.current_process:
            return None

        try:
            output, error = self.current_process.communicate(timeout=5)

            # Check for success
            if 'key found' in output.lower():
                key_match = re.search(r'key\s*found\s*\[\s*\d+\s*\]\s*([^\s]+)', output, re.IGNORECASE)
                if key_match:
                    return {
                        'type': 'completed',
                        'status': 'success',
                        'key': key_match.group(1)
                    }

            return {
                'type': 'completed',
                'status': 'failed'
            }

        except subprocess.TimeoutExpired:
            return {
                'type': 'timeout',
                'status': 'failed'
            }

    def stop_attack(self) -> bool:
        """Stop current cowpatty attack"""
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

    def get_supported_formats(self) -> List[str]:
        """Get supported capture file formats"""
        return ['.cap', '.pcap', '.pcapng']

    def validate_capture_file(self, capture_file: str) -> bool:
        """Validate that capture file contains WPA handshake"""
        try:
            # Use cowpatty to check if file is valid
            result = subprocess.run(['cowpatty', '-c', '-r', capture_file],
                                  capture_output=True, text=True, timeout=10)

            return '1 handshake' in result.stdout or 'handshakes' in result.stdout

        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

class AdvancedCowpattyController:
    """Advanced controller for Cowpatty operations"""

    def __init__(self):
        self.cowpatty = CowpattyIntegration()
        self.active_attacks = {}

    def start_optimized_attack(self, ssid: str, capture_file: str,
                             wordlist: str, use_precomputation: bool = True) -> str:
        """Start optimized cowpatty attack"""
        attack_id = f"cowpatty_{ssid}_{int(time.time())}"

        try:
            if use_precomputation and self.cowpatty.genpmk_available:
                # Precompute PMKs
                pmk_file = self.cowpatty.precompute_pmk(ssid, wordlist)
                if pmk_file:
                    process = self.cowpatty.attack_with_pmk_file(pmk_file, capture_file, ssid)
                else:
                    # Fallback to standard attack
                    process = self.cowpatty.attack_with_wordlist(wordlist, capture_file, ssid)
            else:
                process = self.cowpatty.attack_with_wordlist(wordlist, capture_file, ssid)

            self.active_attacks[attack_id] = {
                'process': process,
                'ssid': ssid,
                'capture_file': capture_file,
                'wordlist': wordlist,
                'start_time': time.time(),
                'status': 'running'
            }

            # Start monitoring
            self.cowpatty.monitor_attack_progress(
                lambda info: self._handle_progress(attack_id, info)
            )

            return attack_id

        except Exception as e:
            raise RuntimeError(f"Failed to start cowpatty attack: {e}")

    def _handle_progress(self, attack_id: str, info: Dict):
        """Handle progress updates"""
        if attack_id in self.active_attacks:
            attack_info = self.active_attacks[attack_id]
            attack_info['last_update'] = time.time()

            if info.get('type') == 'key_found':
                attack_info.update({
                    'status': 'completed',
                    'result': info
                })
            elif info.get('type') == 'completed':
                attack_info.update({
                    'status': 'completed',
                    'result': info
                })
            elif info.get('type') == 'progress':
                attack_info['progress'] = info.get('percentage', 0)

    def get_attack_status(self, attack_id: str) -> Optional[Dict]:
        """Get status of specific attack"""
        return self.active_attacks.get(attack_id)

    def stop_attack(self, attack_id: str) -> bool:
        """Stop specific attack"""
        if attack_id in self.active_attacks:
            success = self.cowpatty.stop_attack()
            if success:
                self.active_attacks[attack_id]['status'] = 'stopped'
            return success
        return False

    def cleanup_attacks(self):
        """Clean up old completed attacks"""
        current_time = time.time()
        to_remove = []

        for attack_id, info in self.active_attacks.items():
            if info.get('status') in ['completed', 'stopped', 'failed']:
                if current_time - info.get('last_update', 0) > 600:  # 10 minutes
                    to_remove.append(attack_id)

        for attack_id in to_remove:
            del self.active_attacks[attack_id]

class CowpattyBenchmark:
    """Benchmarking tool for Cowpatty performance"""

    def __init__(self):
        self.cowpatty = CowpattyIntegration()

    def benchmark_attack_speed(self, wordlist: str, capture_file: str,
                              ssid: str, duration: int = 60) -> Dict:
        """Benchmark cowpatty attack speed"""
        results = {
            'passphrases_per_second': 0,
            'total_tested': 0,
            'time_elapsed': duration
        }

        if not self.cowpatty.cowpatty_available:
            return results

        try:
            process = self.cowpatty.attack_with_wordlist(wordlist, capture_file, ssid)
            start_time = time.time()

            while time.time() - start_time < duration:
                if process.poll() is not None:
                    break
                time.sleep(1)

            # Stop the process
            process.terminate()
            process.wait(timeout=5)

            # Try to parse final output
            if process.stdout:
                output = process.stdout.read()
                tested_match = re.search(r'(\d+)\s+passphrases?\s+tested', str(output), re.IGNORECASE)
                if tested_match:
                    results['total_tested'] = int(tested_match.group(1))
                    results['passphrases_per_second'] = results['total_tested'] / duration

        except Exception:
            pass

        return results

# Example usage:
if __name__ == "__main__":
    cowpatty = CowpattyIntegration()

    if cowpatty.cowpatty_available:
        print("Cowpatty is available!")

        if cowpatty.genpmk_available:
            print("Genpmk is also available for PMK precomputation")
        else:
            print("Genpmk not found - precomputation not available")

        # Example benchmark
        benchmark = CowpattyBenchmark()
        # This would require actual files to test
        # results = benchmark.benchmark_attack_speed(wordlist, capture, ssid)
        # print(f"Benchmark results: {results}")

    else:
        print("Cowpatty not found. Please install cowpatty package.")