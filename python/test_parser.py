"""
Tests for the AIEDL parser.

Run with: python -m pytest aiedl/test_parser.py
Or: python aiedl/test_parser.py
"""

import unittest
import os
import tempfile

try:
    from .parser import parse_edl_with_ai
except ImportError:
    from parser import parse_edl_with_ai


class TestAIEDLParser(unittest.TestCase):
    """Test cases for the AIEDL parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.sample_file = os.path.join(self.test_dir, 'sample.ai.edl')
    
    def test_parse_sample_file(self):
        """Test parsing the sample AIEDL file."""
        edits = parse_edl_with_ai(self.sample_file)
        self.assertIsInstance(edits, list)
        self.assertGreater(len(edits), 0)
    
    def test_parse_video_cut_edit(self):
        """Test parsing a video cut edit."""
        edl_content = """TITLE: Test
FPS: 24
AI_VERSION: 1.0

001  AX       V     C        00:00:00:00 00:00:05:00 00:00:10:00 00:00:15:00
* FROM CLIP NAME: Scene1
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.edl', delete=False) as f:
            f.write(edl_content)
            temp_file = f.name
        
        try:
            edits = parse_edl_with_ai(temp_file)
            self.assertEqual(len(edits), 1)
            edit = edits[0]
            self.assertEqual(edit['edit_number'], '001')
            self.assertEqual(edit['reel'], 'AX')
            self.assertEqual(edit['track'], 'V')
            self.assertEqual(edit['operation'], 'C')
            self.assertEqual(len(edit['timecodes']), 4)
            self.assertEqual(edit['timecodes'][0], '00:00:00:00')
            self.assertIn('from_clip_name', edit['metadata'])
            self.assertEqual(edit['metadata']['from_clip_name'], 'Scene1')
        finally:
            os.unlink(temp_file)
    
    def test_parse_video_inpaint_edit(self):
        """Test parsing a video inpaint edit with region and action."""
        edl_content = """TITLE: Test
FPS: 24
AI_VERSION: 1.0

001  AI       V     INPAINT  00:00:12:00 00:00:14:00
* REGION: (x1:.1, y1:.2, x2:.3, y2:.4)
* ACTION: REMOVE_OBJECT
* TARGET: Make the chair green
* STRENGTH: 0.8
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.edl', delete=False, encoding='utf-8') as f:
            f.write(edl_content)
            f.flush()
            temp_file = f.name
        
        try:
            edits = parse_edl_with_ai(temp_file)
            self.assertEqual(len(edits), 1)
            edit = edits[0]
            self.assertEqual(edit['edit_number'], '001')
            self.assertEqual(edit['reel'], 'AI')
            self.assertEqual(edit['track'], 'V')
            self.assertEqual(edit['operation'], 'INPAINT')
            
            # Check metadata
            self.assertIn('region', edit['metadata'])
            region = edit['metadata']['region']
            self.assertEqual(region['x1'], 0.1)
            self.assertEqual(region['y1'], 0.2)
            self.assertEqual(region['x2'], 0.3)
            self.assertEqual(region['y2'], 0.4)
            
            self.assertEqual(edit['metadata']['action'], 'REMOVE_OBJECT')
            self.assertEqual(edit['metadata']['target'], 'Make the chair green')
            self.assertEqual(edit['metadata']['strength'], 0.8)
        finally:
            os.unlink(temp_file)
    
    def test_parse_audio_mute_edit(self):
        """Test parsing an audio mute edit."""
        edl_content = """TITLE: Test
FPS: 24
AI_VERSION: 1.0

001  AX       A1    MUTE     00:01:10:12 00:01:12:05 00:01:10:12 00:01:12:05
* DESCRIPTION: Mute profanity in dialogue.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.edl', delete=False) as f:
            f.write(edl_content)
            temp_file = f.name
        
        try:
            edits = parse_edl_with_ai(temp_file)
            self.assertEqual(len(edits), 1)
            edit = edits[0]
            self.assertEqual(edit['edit_number'], '001')
            self.assertEqual(edit['track'], 'A1')
            self.assertEqual(edit['operation'], 'MUTE')
            self.assertEqual(edit['metadata']['description'], 'Mute profanity in dialogue.')
        finally:
            os.unlink(temp_file)
    
    def test_parse_audio_replace_edit(self):
        """Test parsing an audio replace edit."""
        edl_content = """TITLE: Test
FPS: 24
AI_VERSION: 1.0

001  AX       A1    REPLACE  00:02:15:08 00:02:16:20 00:02:15:08 00:02:16:20
* REPLACEMENT: "[CENSORED]"
* DESCRIPTION: Replace explicit word.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.edl', delete=False) as f:
            f.write(edl_content)
            temp_file = f.name
        
        try:
            edits = parse_edl_with_ai(temp_file)
            self.assertEqual(len(edits), 1)
            edit = edits[0]
            self.assertEqual(edit['operation'], 'REPLACE')
            self.assertEqual(edit['metadata']['replacement'], '"[CENSORED]"')
            self.assertEqual(edit['metadata']['description'], 'Replace explicit word.')
        finally:
            os.unlink(temp_file)
    
    def test_parse_audio_channel_specific_edit(self):
        """Test parsing an audio edit with channel specification."""
        edl_content = """TITLE: Test
FPS: 24
AI_VERSION: 1.0

001  AX       A1    MUTE     00:01:10:12 00:01:12:05 00:01:10:12 00:01:12:05
* CHANNEL: 2
* DESCRIPTION: Mute channel 2 only.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.edl', delete=False) as f:
            f.write(edl_content)
            temp_file = f.name
        
        try:
            edits = parse_edl_with_ai(temp_file)
            self.assertEqual(len(edits), 1)
            edit = edits[0]
            self.assertEqual(edit['metadata']['channel'], 2)
            self.assertEqual(edit['metadata']['description'], 'Mute channel 2 only.')
        finally:
            os.unlink(temp_file)
    
    def test_parse_caption_replace_edit(self):
        """Test parsing a caption replace edit."""
        edl_content = """TITLE: Test
FPS: 24
AI_VERSION: 1.0

001  AX       S     REPLACE  00:03:00:00 00:03:05:00 00:03:00:00 00:03:05:00
* ORIGINAL_TEXT: "What the hell are you doing?"
* REPLACEMENT: "What are you doing?"
* DESCRIPTION: Replace profanity in captions.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.edl', delete=False) as f:
            f.write(edl_content)
            temp_file = f.name
        
        try:
            edits = parse_edl_with_ai(temp_file)
            self.assertEqual(len(edits), 1)
            edit = edits[0]
            self.assertEqual(edit['track'], 'S')
            self.assertEqual(edit['operation'], 'REPLACE')
            self.assertEqual(edit['metadata']['original_text'], '"What the hell are you doing?"')
            self.assertEqual(edit['metadata']['replacement'], '"What are you doing?"')
            self.assertEqual(edit['metadata']['description'], 'Replace profanity in captions.')
        finally:
            os.unlink(temp_file)
    
    def test_parse_caption_mute_edit(self):
        """Test parsing a caption mute edit."""
        edl_content = """TITLE: Test
FPS: 24
AI_VERSION: 1.0

001  AX       S     MUTE     00:05:20:00 00:05:22:00 00:05:20:00 00:05:22:00
* DESCRIPTION: Hide captions during this time period.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.edl', delete=False) as f:
            f.write(edl_content)
            temp_file = f.name
        
        try:
            edits = parse_edl_with_ai(temp_file)
            self.assertEqual(len(edits), 1)
            edit = edits[0]
            self.assertEqual(edit['track'], 'S')
            self.assertEqual(edit['operation'], 'MUTE')
            self.assertEqual(edit['metadata']['description'], 'Hide captions during this time period.')
        finally:
            os.unlink(temp_file)
    
    def test_parse_caption_modify_edit(self):
        """Test parsing a caption modify edit."""
        edl_content = """TITLE: Test
FPS: 24
AI_VERSION: 1.0

001  AX       S     MODIFY   00:06:15:00 00:06:18:00 00:06:15:00 00:06:18:00
* ORIGINAL_TEXT: "He said a bad word"
* REPLACEMENT: "He said something inappropriate"
* DESCRIPTION: Modify caption text.
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.edl', delete=False) as f:
            f.write(edl_content)
            temp_file = f.name
        
        try:
            edits = parse_edl_with_ai(temp_file)
            self.assertEqual(len(edits), 1)
            edit = edits[0]
            self.assertEqual(edit['operation'], 'MODIFY')
            self.assertEqual(edit['metadata']['original_text'], '"He said a bad word"')
            self.assertEqual(edit['metadata']['replacement'], '"He said something inappropriate"')
        finally:
            os.unlink(temp_file)
    
    def test_parse_multiple_edits(self):
        """Test parsing multiple edits in sequence."""
        edl_content = """TITLE: Test
FPS: 24
AI_VERSION: 1.0

001  AX       V     C        00:00:00:00 00:00:05:00 00:00:10:00 00:00:15:00
* FROM CLIP NAME: Scene1

002  AX       A1    MUTE     00:01:10:12 00:01:12:05 00:01:10:12 00:01:12:05
* DESCRIPTION: Mute profanity.

003  AX       S     REPLACE  00:03:00:00 00:03:05:00 00:03:00:00 00:03:05:00
* ORIGINAL_TEXT: "Bad word"
* REPLACEMENT: "Good word"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.edl', delete=False) as f:
            f.write(edl_content)
            temp_file = f.name
        
        try:
            edits = parse_edl_with_ai(temp_file)
            self.assertEqual(len(edits), 3)
            self.assertEqual(edits[0]['edit_number'], '001')
            self.assertEqual(edits[1]['edit_number'], '002')
            self.assertEqual(edits[2]['edit_number'], '003')
            
            # Check that metadata is properly separated
            self.assertIn('from_clip_name', edits[0]['metadata'])
            self.assertNotIn('from_clip_name', edits[1]['metadata'])
            self.assertIn('description', edits[1]['metadata'])
            self.assertNotIn('description', edits[0]['metadata'])
        finally:
            os.unlink(temp_file)
    
    def test_parse_region_with_comments(self):
        """Test parsing region metadata with comments."""
        edl_content = """TITLE: Test
FPS: 24
AI_VERSION: 1.0

001  AI       V     INPAINT  00:00:12:00 00:00:14:00
* REGION: (x1:.1, y1:.2, x2:.3, y2:.4) # percentages
* ACTION: REMOVE_OBJECT
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.edl', delete=False, encoding='utf-8') as f:
            f.write(edl_content)
            f.flush()
            temp_file = f.name
        
        try:
            edits = parse_edl_with_ai(temp_file)
            self.assertEqual(len(edits), 1)
            region = edits[0]['metadata']['region']
            self.assertEqual(region['x1'], 0.1)
            self.assertEqual(region['y2'], 0.4)
        finally:
            os.unlink(temp_file)
    
    def test_parse_action_with_comments(self):
        """Test parsing action metadata with inline comments."""
        edl_content = """TITLE: Test
FPS: 24
AI_VERSION: 1.0

001  AI       V     INPAINT  00:00:12:00 00:00:14:00
* ACTION: REMOVE_OBJECT # This is a comment
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.edl', delete=False, encoding='utf-8') as f:
            f.write(edl_content)
            f.flush()
            temp_file = f.name
        
        try:
            edits = parse_edl_with_ai(temp_file)
            self.assertEqual(len(edits), 1)
            self.assertEqual(edits[0]['metadata']['action'], 'REMOVE_OBJECT')
        finally:
            os.unlink(temp_file)
    
    def test_parse_empty_file(self):
        """Test parsing an empty file."""
        edl_content = """TITLE: Test
FPS: 24
AI_VERSION: 1.0
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.edl', delete=False) as f:
            f.write(edl_content)
            temp_file = f.name
        
        try:
            edits = parse_edl_with_ai(temp_file)
            self.assertEqual(len(edits), 0)
        finally:
            os.unlink(temp_file)
    
    def test_parse_edit_without_metadata(self):
        """Test parsing an edit without any metadata."""
        edl_content = """TITLE: Test
FPS: 24
AI_VERSION: 1.0

001  AX       V     C        00:00:00:00 00:00:05:00 00:00:10:00 00:00:15:00
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.edl', delete=False) as f:
            f.write(edl_content)
            temp_file = f.name
        
        try:
            edits = parse_edl_with_ai(temp_file)
            self.assertEqual(len(edits), 1)
            self.assertEqual(len(edits[0]['metadata']), 0)
        finally:
            os.unlink(temp_file)
    
    def test_parse_skips_comments(self):
        """Test that comment lines are skipped."""
        edl_content = """TITLE: Test
FPS: 24
AI_VERSION: 1.0

# This is a comment
001  AX       V     C        00:00:00:00 00:00:05:00 00:00:10:00 00:00:15:00
# Another comment
* FROM CLIP NAME: Scene1
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.edl', delete=False) as f:
            f.write(edl_content)
            temp_file = f.name
        
        try:
            edits = parse_edl_with_ai(temp_file)
            self.assertEqual(len(edits), 1)
            self.assertEqual(edits[0]['metadata']['from_clip_name'], 'Scene1')
        finally:
            os.unlink(temp_file)
    
    def test_parse_skips_empty_lines(self):
        """Test that empty lines are skipped."""
        edl_content = """TITLE: Test
FPS: 24
AI_VERSION: 1.0


001  AX       V     C        00:00:00:00 00:00:05:00 00:00:10:00 00:00:15:00


* FROM CLIP NAME: Scene1

"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.edl', delete=False) as f:
            f.write(edl_content)
            temp_file = f.name
        
        try:
            edits = parse_edl_with_ai(temp_file)
            self.assertEqual(len(edits), 1)
            self.assertEqual(edits[0]['metadata']['from_clip_name'], 'Scene1')
        finally:
            os.unlink(temp_file)
    
    def test_parse_timecodes(self):
        """Test that timecodes are correctly parsed."""
        edl_content = """TITLE: Test
FPS: 24
AI_VERSION: 1.0

001  AX       V     C        00:01:23:15 00:01:25:20 00:02:10:05 00:02:12:10
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.edl', delete=False) as f:
            f.write(edl_content)
            temp_file = f.name
        
        try:
            edits = parse_edl_with_ai(temp_file)
            self.assertEqual(len(edits), 1)
            timecodes = edits[0]['timecodes']
            self.assertEqual(len(timecodes), 4)
            self.assertEqual(timecodes[0], '00:01:23:15')
            self.assertEqual(timecodes[1], '00:01:25:20')
            self.assertEqual(timecodes[2], '00:02:10:05')
            self.assertEqual(timecodes[3], '00:02:12:10')
        finally:
            os.unlink(temp_file)
    
    def test_parse_strength_as_float(self):
        """Test that STRENGTH is parsed as a float."""
        edl_content = """TITLE: Test
FPS: 24
AI_VERSION: 1.0

001  AI       V     INPAINT  00:00:12:00 00:00:14:00
* STRENGTH: 0.75
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.edl', delete=False, encoding='utf-8') as f:
            f.write(edl_content)
            f.flush()
            temp_file = f.name
        
        try:
            edits = parse_edl_with_ai(temp_file)
            self.assertEqual(len(edits), 1)
            strength = edits[0]['metadata']['strength']
            self.assertIsInstance(strength, float)
            self.assertEqual(strength, 0.75)
        finally:
            os.unlink(temp_file)

    def test_parse_seed_as_int(self):
        """Test that SEED is parsed as an integer."""
        edl_content = """TITLE: Test
FPS: 24
AI_VERSION: 1.0

001  AI       V     INPAINT  00:00:12:00 00:00:14:00
* REGION: (x1:.1, y1:.2, x2:.3, y2:.4)
* ACTION: REMOVE_OBJECT
* SEED: 123456789 # deterministic output
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.edl', delete=False, encoding='utf-8') as f:
            f.write(edl_content)
            f.flush()
            temp_file = f.name
        
        try:
            edits = parse_edl_with_ai(temp_file)
            self.assertEqual(len(edits), 1)
            seed = edits[0]['metadata']['seed']
            self.assertIsInstance(seed, int)
            self.assertEqual(seed, 123456789)
        finally:
            os.unlink(temp_file)
    
    def test_parse_channel_as_int(self):
        """Test that CHANNEL is parsed as an integer."""
        edl_content = """TITLE: Test
FPS: 24
AI_VERSION: 1.0

001  AX       A1    MUTE     00:01:10:12 00:01:12:05 00:01:10:12 00:01:12:05
* CHANNEL: 5
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.edl', delete=False) as f:
            f.write(edl_content)
            temp_file = f.name
        
        try:
            edits = parse_edl_with_ai(temp_file)
            self.assertEqual(len(edits), 1)
            channel = edits[0]['metadata']['channel']
            self.assertIsInstance(channel, int)
            self.assertEqual(channel, 5)
        finally:
            os.unlink(temp_file)
    
    def test_parse_metadata_isolation(self):
        """Test that metadata from one edit doesn't leak into another."""
        edl_content = """TITLE: Test
FPS: 24
AI_VERSION: 1.0

001  AX       V     C        00:00:00:00 00:00:05:00 00:00:10:00 00:00:15:00
* FROM CLIP NAME: Scene1

002  AX       A1    MUTE     00:01:10:12 00:01:12:05 00:01:10:12 00:01:12:05
* DESCRIPTION: Audio mute
* CHANNEL: 2
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.edl', delete=False) as f:
            f.write(edl_content)
            temp_file = f.name
        
        try:
            edits = parse_edl_with_ai(temp_file)
            self.assertEqual(len(edits), 2)
            
            # First edit should only have from_clip_name
            self.assertIn('from_clip_name', edits[0]['metadata'])
            self.assertNotIn('description', edits[0]['metadata'])
            self.assertNotIn('channel', edits[0]['metadata'])
            
            # Second edit should only have description and channel
            self.assertNotIn('from_clip_name', edits[1]['metadata'])
            self.assertIn('description', edits[1]['metadata'])
            self.assertIn('channel', edits[1]['metadata'])
        finally:
            os.unlink(temp_file)
    
    def test_parse_file_not_found(self):
        """Test that FileNotFoundError is raised for non-existent file."""
        with self.assertRaises(FileNotFoundError):
            parse_edl_with_ai('nonexistent_file.edl')


if __name__ == '__main__':
    unittest.main()

