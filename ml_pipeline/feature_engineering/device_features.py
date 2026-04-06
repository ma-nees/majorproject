"""
Device Features
Extracts features from device fingerprinting, browser characteristics, and hardware attributes.
"""

import hashlib
import re
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np

class DeviceFeatureExtractor:
    """
    Extracts features from device information:
    - Browser/OS fingerprint
    - Screen resolution patterns
    - User agent parsing
    - Device ID consistency
    - Known device check
    """
    
    def __init__(self, known_devices_db: Optional[pd.DataFrame] = None):
        """
        Args:
            known_devices_db: DataFrame with historical device info for users
        """
        self.known_devices = known_devices_db if known_devices_db is not None else pd.DataFrame()
    
    def extract_features(self, device_info: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract device-based features.
        
        Args:
            device_info: Dictionary with device attributes:
                - device_id (optional)
                - user_agent
                - screen_resolution
                - language
                - timezone
                - platform
                - browser_name
                - browser_version
                - os_name
                - os_version
                - is_mobile
                - is_tablet
                - is_desktop
                - touch_support
            user_id: User identifier for checking known devices
        
        Returns:
            Dictionary of device features
        """
        features = {}
        
        # Device ID features
        device_id = device_info.get('device_id')
        features['has_device_id'] = int(device_id is not None and device_id != '')
        
        # User agent parsing
        ua = device_info.get('user_agent', '')
        parsed = self._parse_user_agent(ua)
        features.update(parsed)
        
        # Screen resolution
        resolution = device_info.get('screen_resolution', '')
        features.update(self._screen_features(resolution))
        
        # Browser language
        language = device_info.get('language', '')
        features['browser_language'] = language[:2] if len(language) >= 2 else 'unknown'
        features['is_common_language'] = int(language[:2] in ['en', 'es', 'fr', 'de', 'zh', 'ja'])
        
        # Timezone
        tz = device_info.get('timezone', '')
        features['has_timezone'] = int(bool(tz))
        features['timezone_offset'] = self._parse_timezone_offset(tz)
        
        # Hardware/platform
        features['is_mobile'] = int(device_info.get('is_mobile', False))
        features['is_tablet'] = int(device_info.get('is_tablet', False))
        features['is_desktop'] = int(device_info.get('is_desktop', True))
        features['touch_support'] = int(device_info.get('touch_support', False))
        
        # Device fingerprint (hash of key attributes)
        fingerprint_str = f"{ua}|{resolution}|{language}|{tz}"
        features['device_fingerprint'] = hashlib.md5(fingerprint_str.encode()).hexdigest()[:16]
        
        # Known device check for user
        if user_id and device_id and not self.known_devices.empty:
            user_devices = self.known_devices[self.known_devices['user_id'] == user_id]
            features['is_known_device'] = int((user_devices['device_id'] == device_id).any())
            features['user_device_count'] = int(user_devices['device_id'].nunique())
        else:
            features['is_known_device'] = 0
            features['user_device_count'] = 0
        
        # Emulator/virtual machine detection
        features.update(self._detect_emulator(ua, device_info))
        
        # Suspicious patterns in device info
        features['suspicious_device_flags'] = self._detect_suspicious(device_info)
        
        return features
    
    def _parse_user_agent(self, ua: str) -> Dict[str, Any]:
        """Parse user agent string for browser, OS, and version."""
        features = {
            'browser': 'unknown',
            'browser_version': 'unknown',
            'os': 'unknown',
            'os_version': 'unknown',
            'is_bot': 0
        }
        
        if not ua:
            return features
        
        ua_lower = ua.lower()
        
        # Bot detection
        bot_patterns = ['bot', 'crawler', 'spider', 'scraper', 'headless', 'phantom', 'selenium']
        features['is_bot'] = int(any(p in ua_lower for p in bot_patterns))
        
        # Browser detection
        browsers = {
            'chrome': r'chrome/(\d+)',
            'firefox': r'firefox/(\d+)',
            'safari': r'safari/(\d+)',
            'edge': r'edg/(\d+)',
            'opera': r'opr/(\d+)'
        }
        for browser, pattern in browsers.items():
            match = re.search(pattern, ua_lower)
            if match:
                features['browser'] = browser
                features['browser_version'] = match.group(1)
                break
        
        # OS detection
        os_patterns = {
            'windows': r'windows nt (\d+\.?\d*)',
            'mac': r'mac os x (\d+[._]\d+)',
            'linux': r'linux',
            'android': r'android (\d+\.?\d*)',
            'ios': r'iphone os (\d+[._]\d+)'
        }
        for os_name, pattern in os_patterns.items():
            match = re.search(pattern, ua_lower)
            if match:
                features['os'] = os_name
                if len(match.groups()) > 0:
                    features['os_version'] = match.group(1).replace('_', '.')
                break
        
        return features
    
    def _screen_features(self, resolution: str) -> Dict[str, Any]:
        """Extract features from screen resolution string."""
        features = {
            'screen_width': 0,
            'screen_height': 0,
            'screen_aspect_ratio': 0,
            'is_common_resolution': 0
        }
        
        if resolution and 'x' in resolution:
            try:
                parts = resolution.split('x')
                width = int(parts[0])
                height = int(parts[1])
                features['screen_width'] = width
                features['screen_height'] = height
                features['screen_aspect_ratio'] = width / height if height > 0 else 0
                
                # Common resolutions
                common = [(1920,1080), (1366,768), (1440,900), (1536,864), (1280,720), (375,667), (414,896)]
                features['is_common_resolution'] = int((width, height) in common)
            except:
                pass
        
        return features
    
    def _parse_timezone_offset(self, tz: str) -> float:
        """Parse timezone string to offset in hours."""
        if not tz:
            return 0
        # Simple extraction: look for UTC+/-HH:MM
        match = re.search(r'UTC([+-]\d{1,2}(?::\d{2})?)', tz)
        if match:
            offset_str = match.group(1)
            if ':' in offset_str:
                hours, minutes = offset_str.split(':')
                return float(hours) + float(minutes)/60
            else:
                return float(offset_str)
        return 0
    
    def _detect_emulator(self, ua: str, device_info: Dict) -> Dict[str, Any]:
        """Detect if device is an emulator/virtual machine."""
        emulator_indicators = [
            'android emulator', 'genymotion', 'bluestacks', 'nox', 'memu',
            'virtualbox', 'vmware', 'qemu', 'kvm', 'xen'
        ]
        ua_lower = ua.lower()
        is_emulator = int(any(ind in ua_lower for ind in emulator_indicators))
        
        # Also check for common emulator screen sizes
        width = device_info.get('screen_width', 0)
        emulator_resolutions = [(720,1280), (1080,1920), (768,1024), (800,1280)]
        if (width, device_info.get('screen_height', 0)) in emulator_resolutions:
            is_emulator = 1
        
        return {'is_emulator': is_emulator}
    
    def _detect_suspicious(self, device_info: Dict) -> int:
        """Count suspicious device flags."""
        flags = 0
        # Missing critical info
        if not device_info.get('user_agent'):
            flags += 1
        if not device_info.get('screen_resolution'):
            flags += 1
        # Headless browser detection
        if device_info.get('is_bot', False):
            flags += 2
        if device_info.get('is_emulator', False):
            flags += 2
        return min(flags, 5)

# Batch feature extraction
def extract_device_features_batch(transactions_df: pd.DataFrame, 
                                   known_devices_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Extract device features for a batch of transactions."""
    extractor = DeviceFeatureExtractor(known_devices_df)
    device_info_cols = ['device_id', 'user_agent', 'screen_resolution', 'language', 'timezone',
                        'is_mobile', 'is_tablet', 'is_desktop', 'touch_support']
    
    features_list = []
    for _, row in transactions_df.iterrows():
        device_info = {col: row.get(col, '') for col in device_info_cols}
        features = extractor.extract_features(device_info, row.get('customer_id'))
        features_list.append(features)
    
    features_df = pd.DataFrame(features_list)
    return pd.concat([transactions_df.reset_index(drop=True), features_df], axis=1)

if __name__ == "__main__":
    sample_device = {
        'device_id': 'abc123',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0',
        'screen_resolution': '1920x1080',
        'language': 'en-US',
        'timezone': 'UTC-05:00',
        'is_mobile': False,
        'is_tablet': False,
        'is_desktop': True,
        'touch_support': False
    }
    extractor = DeviceFeatureExtractor()
    features = extractor.extract_features(sample_device)
    print("Device Features:", features)