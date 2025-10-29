#!/usr/bin/env python3
"""
Crunch Wordlist Generator Integration for Fern WiFi Cracker
Advanced wordlist generation capabilities
"""

import os
import re
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

class CrunchIntegration:
    """Advanced Crunch wordlist generator integration"""

    def __init__(self):
        self.crunch_available = self._check_crunch()
        self.current_process = None
        self.generation_stats = {}

    def _check_crunch(self) -> bool:
        """Check if crunch is available"""
        try:
            result = subprocess.run(['crunch', '-h'],
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def generate_wordlist(self, min_length: int, max_length: int,
                         charset: str, output_file: str,
                         pattern: Optional[str] = None, **options) -> subprocess.Popen:
        """Generate wordlist using crunch"""
        if not self.crunch_available:
            raise RuntimeError("Crunch not available")

        cmd = ['crunch', str(min_length), str(max_length), charset, '-o', output_file]

        # Add pattern if specified
        if pattern:
            cmd.extend(['-t', pattern])

        # Add additional options
        if options.get('count'):
            cmd.extend(['-c', str(options['count'])])

        if options.get('duplicate'):
            cmd.append('-d')

        if options.get('invert'):
            cmd.append('-i')

        if options.get('literal'):
            cmd.append('-l')

        if options.get('permute'):
            cmd.append('-p')

        # Start generation
        self.current_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        return self.current_process

    def generate_numeric_wordlist(self, min_length: int, max_length: int,
                                output_file: str) -> subprocess.Popen:
        """Generate numeric wordlist (0-9)"""
        return self.generate_wordlist(min_length, max_length, '0123456789', output_file)

    def generate_alpha_wordlist(self, min_length: int, max_length: int,
                              output_file: str, case: str = 'lower') -> subprocess.Popen:
        """Generate alphabetic wordlist"""
        if case == 'upper':
            charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        elif case == 'mixed':
            charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        else:  # lower
            charset = 'abcdefghijklmnopqrstuvwxyz'

        return self.generate_wordlist(min_length, max_length, charset, output_file)

    def generate_alphanumeric_wordlist(self, min_length: int, max_length: int,
                                     output_file: str, case: str = 'lower') -> subprocess.Popen:
        """Generate alphanumeric wordlist"""
        if case == 'upper':
            charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        elif case == 'mixed':
            charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        else:  # lower
            charset = 'abcdefghijklmnopqrstuvwxyz0123456789'

        return self.generate_wordlist(min_length, max_length, charset, output_file)

    def generate_custom_charset_wordlist(self, min_length: int, max_length: int,
                                       charset: str, output_file: str) -> subprocess.Popen:
        """Generate wordlist with custom character set"""
        return self.generate_wordlist(min_length, max_length, charset, output_file)

    def generate_pattern_based_wordlist(self, pattern: str, output_file: str) -> subprocess.Popen:
        """Generate wordlist based on pattern"""
        # Extract charset from pattern and determine lengths
        # @ = lowercase, , = uppercase, % = numbers, ^ = symbols
        charset = ''
        if '@' in pattern:
            charset += 'abcdefghijklmnopqrstuvwxyz'
        if ',' in pattern:
            charset += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if '%' in pattern:
            charset += '0123456789'
        if '^' in pattern:
            charset += '!@#$%^&*()-_+=~`[]{}|\\:;"\'<>,.?/'

        min_length = max_length = len(pattern)

        return self.generate_wordlist(min_length, max_length, charset, output_file, pattern)

    def monitor_generation_progress(self, callback=None) -> None:
        """Monitor wordlist generation progress"""
        if not self.current_process:
            return

        def monitor():
            while self.current_process and self.current_process.poll() is None:
                if self.current_process.stderr:
                    line = self.current_process.stderr.readline()
                    if line:
                        progress = self._parse_progress(line.strip())
                        if progress and callback:
                            callback(progress)
                time.sleep(0.1)

            # Generation completed
            if callback:
                callback({'status': 'completed'})

        threading.Thread(target=monitor, daemon=True).start()

    def _parse_progress(self, line: str) -> Optional[Dict]:
        """Parse crunch output for progress"""
        # Look for percentage
        percent_match = re.search(r'(\d+)%', line)
        if percent_match:
            return {
                'type': 'progress',
                'percentage': int(percent_match.group(1))
            }

        # Look for words generated
        words_match = re.search(r'(\d+)\s+words', line, re.IGNORECASE)
        if words_match:
            return {
                'type': 'words_generated',
                'count': int(words_match.group(1))
            }

        return None

    def stop_generation(self) -> bool:
        """Stop current wordlist generation"""
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

    def estimate_wordlist_size(self, min_length: int, max_length: int,
                             charset_size: int) -> int:
        """Estimate the size of wordlist before generation"""
        total = 0
        for length in range(min_length, max_length + 1):
            total += charset_size ** length
        return total

    def get_charset_info(self) -> Dict[str, str]:
        """Get information about available character sets"""
        return {
            'lowercase': 'abcdefghijklmnopqrstuvwxyz (26 chars)',
            'uppercase': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ (26 chars)',
            'digits': '0123456789 (10 chars)',
            'lowercase_digits': 'abcdefghijklmnopqrstuvwxyz0123456789 (36 chars)',
            'uppercase_digits': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 (36 chars)',
            'mixed_alpha': 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz (52 chars)',
            'alphanumeric': 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 (62 chars)',
            'symbols': '!@#$%^&*()-_+=~`[]{}|\\:;"\'<>,.?/ (32 chars)',
            'all_printable': 'All printable ASCII characters (95 chars)'
        }

class AdvancedCrunchController:
    """Advanced controller for Crunch operations"""

    def __init__(self):
        self.crunch = CrunchIntegration()
        self.active_generations = {}

    def start_smart_wordlist_generation(self, target_info: Dict,
                                      output_file: str) -> str:
        """Generate wordlist based on target information"""
        generation_id = f"crunch_{int(time.time())}"

        try:
            # Analyze target info to determine best generation strategy
            strategy = self._analyze_target(target_info)

            if strategy['type'] == 'pattern':
                process = self.crunch.generate_pattern_based_wordlist(
                    strategy['pattern'], output_file)
            elif strategy['type'] == 'charset':
                process = self.crunch.generate_wordlist(
                    strategy['min_length'], strategy['max_length'],
                    strategy['charset'], output_file)
            else:
                # Default alphanumeric
                process = self.crunch.generate_alphanumeric_wordlist(
                    8, 12, output_file)

            self.active_generations[generation_id] = {
                'process': process,
                'output_file': output_file,
                'strategy': strategy,
                'start_time': time.time(),
                'status': 'running'
            }

            # Start monitoring
            self.crunch.monitor_generation_progress(
                lambda info: self._handle_progress(generation_id, info)
            )

            return generation_id

        except Exception as e:
            raise RuntimeError(f"Failed to start wordlist generation: {e}")

    def _analyze_target(self, target_info: Dict) -> Dict:
        """Analyze target information to determine generation strategy"""
        ssid = target_info.get('ssid', '')
        bssid = target_info.get('bssid', '')

        # Look for patterns in SSID
        if re.search(r'\d{8}', ssid):  # 8 digits (birthday)
            return {
                'type': 'pattern',
                'pattern': '@@@@@@@@',  # 8 lowercase
                'description': 'Birthday pattern (8 digits)'
            }
        elif re.search(r'[A-Z]{3,}', ssid):  # Uppercase words
            return {
                'type': 'charset',
                'charset': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                'min_length': 8,
                'max_length': 12,
                'description': 'Mixed alphanumeric'
            }
        else:
            # Default strategy
            return {
                'type': 'charset',
                'charset': 'abcdefghijklmnopqrstuvwxyz0123456789',
                'min_length': 8,
                'max_length': 16,
                'description': 'Standard alphanumeric'
            }

    def _handle_progress(self, generation_id: str, info: Dict):
        """Handle generation progress updates"""
        if generation_id in self.active_generations:
            gen_info = self.active_generations[generation_id]
            gen_info['last_update'] = time.time()

            if info.get('status') == 'completed':
                gen_info['status'] = 'completed'
            elif info.get('type') == 'progress':
                gen_info['progress'] = info.get('percentage', 0)

    def get_generation_status(self, generation_id: str) -> Optional[Dict]:
        """Get status of wordlist generation"""
        return self.active_generations.get(generation_id)

    def stop_generation(self, generation_id: str) -> bool:
        """Stop specific generation"""
        if generation_id in self.active_generations:
            success = self.crunch.stop_generation()
            if success:
                self.active_generations[generation_id]['status'] = 'stopped'
            return success
        return False

    def cleanup_generations(self):
        """Clean up completed generations"""
        current_time = time.time()
        to_remove = []

        for gen_id, info in self.active_generations.items():
            if info.get('status') in ['completed', 'stopped']:
                if current_time - info.get('last_update', 0) > 300:  # 5 minutes
                    to_remove.append(gen_id)

        for gen_id in to_remove:
            del self.active_generations[gen_id]

class CrunchBenchmark:
    """Benchmarking tool for Crunch performance"""

    def __init__(self):
        self.crunch = CrunchIntegration()

    def benchmark_generation_speed(self, charset: str, length: int,
                                  duration: int = 30) -> Dict:
        """Benchmark wordlist generation speed"""
        results = {
            'words_per_second': 0,
            'total_generated': 0,
            'charset_size': len(charset),
            'word_length': length
        }

        if not self.crunch.crunch_available:
            return results

        try:
            output_file = f'/tmp/crunch_benchmark_{int(time.time())}.txt'
            process = self.crunch.generate_wordlist(length, length, charset, output_file)

            start_time = time.time()
            words_generated = 0

            while time.time() - start_time < duration:
                if process.poll() is not None:
                    break

                # Check file size periodically
                if os.path.exists(output_file):
                    try:
                        with open(output_file, 'r') as f:
                            lines = f.readlines()
                            words_generated = len(lines)
                    except:
                        pass

                time.sleep(1)

            # Stop generation
            process.terminate()
            process.wait(timeout=5)

            elapsed = time.time() - start_time
            results['total_generated'] = words_generated
            results['words_per_second'] = words_generated / elapsed if elapsed > 0 else 0

            # Cleanup
            if os.path.exists(output_file):
                os.remove(output_file)

        except Exception:
            pass

        return results

# Example usage:
if __name__ == "__main__":
    crunch = CrunchIntegration()

    if crunch.crunch_available:
        print("Crunch is available!")

        # Show available charsets
        charsets = crunch.get_charset_info()
        print("Available character sets:")
        for name, desc in charsets.items():
            print(f"  {name}: {desc}")

        # Example generation
        try:
            # Generate a simple numeric wordlist
            process = crunch.generate_numeric_wordlist(4, 6, '/tmp/test_numeric.txt')
            print("Generating numeric wordlist...")

            # Monitor progress
            crunch.monitor_generation_progress(
                lambda info: print(f"Progress: {info}")
            )

            # Wait a bit then stop
            time.sleep(5)
            crunch.stop_generation()
            print("Generation stopped")

        except Exception as e:
            print(f"Error: {e}")

    else:
        print("Crunch not found. Please install crunch package.")