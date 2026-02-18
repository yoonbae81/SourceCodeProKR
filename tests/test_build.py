import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import font_variants, hangul_bearing_adjustment


class TestConfig(unittest.TestCase):
    """Test cases for config.py"""

    def test_font_variants_exists(self):
        """Test that font_variants is defined"""
        self.assertIsInstance(font_variants, list)

    def test_hangul_bearing_adjustment_exists(self):
        """Test that hangul_bearing_adjustment is defined"""
        self.assertIsInstance(hangul_bearing_adjustment, int)


if __name__ == '__main__':
    unittest.main()
