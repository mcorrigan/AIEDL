"""
Tests for the AIEDL validator.
"""

import os
import tempfile
import unittest

try:
    from .validator import AIEDLValidator
except ImportError:
    from validator import AIEDLValidator


class TestAIEDLValidator(unittest.TestCase):
    """Test cases for validator behavior."""

    def test_validate_file_with_seed(self):
        """SEED metadata is accepted for INPAINT operations."""
        edl_content = """TITLE: Test
FPS: 24
AI_VERSION: 1.0

001  AI       V     INPAINT  00:00:12:00 00:00:14:00
* REGION: (x1:.1, y1:.2, x2:.3, y2:.4)
* ACTION: REMOVE_OBJECT
* SEED: 12345
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.edl', delete=False, encoding='utf-8') as f:
            f.write(edl_content)
            f.flush()
            temp_file = f.name

        try:
            validator = AIEDLValidator(strict=True)
            is_valid, errors, _ = validator.validate_file(temp_file)
            self.assertTrue(is_valid)
            self.assertEqual(errors, [])
        finally:
            os.unlink(temp_file)

    def test_reject_non_integer_seed(self):
        """Validator rejects non-integer seed values."""
        validator = AIEDLValidator(strict=True)
        edit = {'operation': 'INPAINT', 'track': 'V'}
        metadata = {
            'region': {'x1': 0.1, 'y1': 0.2, 'x2': 0.3, 'y2': 0.4},
            'action': 'REMOVE_OBJECT',
            'seed': 1.5,
        }

        validator._validate_metadata(edit, metadata)
        messages = [str(err) for err in validator.errors]
        self.assertTrue(any("SEED must be an integer" in msg for msg in messages))


if __name__ == '__main__':
    unittest.main()
