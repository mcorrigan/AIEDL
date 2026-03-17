"""
Validator for AIEDL (AI Edit Decision List) files.

Validates format, timecodes, required fields, and constraints.
"""

import re
from typing import List, Dict, Tuple, Optional

try:
    from .parser import parse_edl_with_ai
except ImportError:
    from parser import parse_edl_with_ai


class ValidationError(Exception):
    """Exception raised for validation errors."""
    def __init__(self, message: str, line_number: Optional[int] = None):
        self.message = message
        self.line_number = line_number
        if line_number:
            super().__init__(f"Line {line_number}: {message}")
        else:
            super().__init__(message)


class AIEDLValidator:
    """Validates AIEDL files against the specification."""
    
    # Valid reel types
    VALID_REELS = {'AX', 'AI'}
    
    # Valid track types
    VALID_TRACKS = {'V', 'S'} | {f'A{i}' for i in range(1, 33)}  # A1-A32
    
    # Valid operations by track type
    VALID_OPERATIONS = {
        'V': {'C', 'INPAINT'},
        'A1': {'MUTE', 'REPLACE'},
        'A2': {'MUTE', 'REPLACE'},
        'S': {'REPLACE', 'MUTE', 'MODIFY'}
    }
    # Add operations for A3-A32
    for i in range(3, 33):
        VALID_OPERATIONS[f'A{i}'] = {'MUTE', 'REPLACE'}
    
    # Valid INPAINT actions
    VALID_INPAINT_ACTIONS = {
        'REMOVE_OBJECT', 'ADD_OBJECT', 'REPLACE_OBJECT', 
        'ADD_COLOR', 'RESTORE'
    }
    
    def __init__(self, strict: bool = True):
        """
        Initialize validator.
        
        Args:
            strict: If True, enforce strict validation (required fields, etc.)
        """
        self.strict = strict
        self.errors: List[ValidationError] = []
        self.warnings: List[str] = []
    
    def validate_file(self, filename: str) -> Tuple[bool, List[ValidationError], List[str]]:
        """
        Validate an AIEDL file.
        
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        
        try:
            # Parse the file
            edits = parse_edl_with_ai(filename)
            
            # Validate header
            self._validate_header(filename)
            
            # Validate each edit
            edit_numbers = set()
            for i, edit in enumerate(edits):
                self._validate_edit(edit, i + 1)
                
                # Check for duplicate edit numbers
                edit_num = edit['edit_number']
                if edit_num in edit_numbers:
                    self.errors.append(ValidationError(
                        f"Duplicate edit number: {edit_num}",
                        line_number=None
                    ))
                edit_numbers.add(edit_num)
            
            # Check for sequential numbering (warning, not error)
            if edit_numbers:
                sorted_nums = sorted([int(n) for n in edit_numbers])
                expected = list(range(1, len(edit_numbers) + 1))
                if sorted_nums != expected:
                    self.warnings.append(
                        "Edit numbers are not sequential starting from 001"
                    )
            
            return len(self.errors) == 0, self.errors, self.warnings
            
        except FileNotFoundError:
            self.errors.append(ValidationError(f"File not found: {filename}"))
            return False, self.errors, self.warnings
        except Exception as e:
            self.errors.append(ValidationError(f"Parse error: {str(e)}"))
            return False, self.errors, self.warnings
    
    def _validate_header(self, filename: str):
        """Validate file header."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            self.errors.append(ValidationError(f"Cannot read file: {str(e)}"))
            return
        
        has_title = False
        has_fps = False
        has_version = False
        
        for i, line in enumerate(lines[:10], 1):  # Check first 10 lines
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            
            if stripped.startswith('TITLE:'):
                has_title = True
                if self.strict and len(stripped.split(':', 1)) < 2:
                    self.errors.append(ValidationError(
                        "TITLE field is empty",
                        line_number=i
                    ))
            elif stripped.startswith('FPS:'):
                has_fps = True
                fps_str = stripped.split(':', 1)[1].strip()
                try:
                    fps = float(fps_str)
                    if fps <= 0 or fps > 120:
                        self.errors.append(ValidationError(
                            f"FPS value out of valid range (0-120): {fps}",
                            line_number=i
                        ))
                except ValueError:
                    self.errors.append(ValidationError(
                        f"Invalid FPS value: {fps_str}",
                        line_number=i
                    ))
            elif stripped.startswith('AI_VERSION:'):
                has_version = True
                version_str = stripped.split(':', 1)[1].strip()
                if version_str != '1.0':
                    self.warnings.append(
                        f"AI_VERSION is {version_str}, expected 1.0"
                    )
        
        if self.strict:
            if not has_title:
                self.errors.append(ValidationError("Missing required header: TITLE"))
            if not has_fps:
                self.errors.append(ValidationError("Missing required header: FPS"))
            if not has_version:
                self.errors.append(ValidationError("Missing required header: AI_VERSION"))
    
    def _validate_edit(self, edit: Dict, edit_index: int):
        """Validate a single edit entry."""
        # Validate edit number format
        edit_num = edit.get('edit_number', '')
        if not re.match(r'^\d{3}$', edit_num):
            self.errors.append(ValidationError(
                f"Edit number must be 3 digits, got: {edit_num}",
                line_number=None
            ))
        
        # Validate reel
        reel = edit.get('reel', '')
        if reel not in self.VALID_REELS:
            self.errors.append(ValidationError(
                f"Invalid reel type: {reel}. Must be one of {self.VALID_REELS}",
                line_number=None
            ))
        
        # Validate track
        track = edit.get('track', '')
        if track not in self.VALID_TRACKS:
            self.errors.append(ValidationError(
                f"Invalid track type: {track}. Must be V, S, or A1-A32",
                line_number=None
            ))
        
        # Validate operation
        operation = edit.get('operation', '')
        valid_ops = self.VALID_OPERATIONS.get(track, set())
        if operation not in valid_ops:
            self.errors.append(ValidationError(
                f"Invalid operation '{operation}' for track '{track}'. "
                f"Valid operations: {valid_ops}",
                line_number=None
            ))
        
        # Validate timecodes
        timecodes = edit.get('timecodes', [])
        if not timecodes:
            self.errors.append(ValidationError(
                "Edit missing timecodes",
                line_number=None
            ))
        else:
            for tc in timecodes:
                self._validate_timecode(tc)
            
            # Validate timecode logic
            if len(timecodes) >= 2:
                source_in = self._timecode_to_frames(timecodes[0])
                source_out = self._timecode_to_frames(timecodes[1])
                if source_in and source_out and source_in >= source_out:
                    self.errors.append(ValidationError(
                        f"SOURCE_IN ({timecodes[0]}) must be before SOURCE_OUT ({timecodes[1]})",
                        line_number=None
                    ))
            
            if len(timecodes) >= 4:
                record_in = self._timecode_to_frames(timecodes[2])
                record_out = self._timecode_to_frames(timecodes[3])
                if record_in and record_out and record_in >= record_out:
                    self.errors.append(ValidationError(
                        f"RECORD_IN ({timecodes[2]}) must be before RECORD_OUT ({timecodes[3]})",
                        line_number=None
                    ))
        
        # Validate metadata based on operation
        metadata = edit.get('metadata', {})
        self._validate_metadata(edit, metadata)
    
    def _validate_timecode(self, timecode: str) -> bool:
        """Validate timecode format HH:MM:SS:FF."""
        if not re.match(r'^\d{2}:\d{2}:\d{2}:\d{2}$', timecode):
            self.errors.append(ValidationError(
                f"Invalid timecode format: {timecode}. Expected HH:MM:SS:FF",
                line_number=None
            ))
            return False
        
        parts = timecode.split(':')
        hours, minutes, seconds, frames = map(int, parts)
        
        if hours > 23:
            self.errors.append(ValidationError(
                f"Hours out of range (0-23): {hours}",
                line_number=None
            ))
        if minutes > 59:
            self.errors.append(ValidationError(
                f"Minutes out of range (0-59): {minutes}",
                line_number=None
            ))
        if seconds > 59:
            self.errors.append(ValidationError(
                f"Seconds out of range (0-59): {seconds}",
                line_number=None
            ))
        if frames > 29:  # Max for 30fps
            self.errors.append(ValidationError(
                f"Frames out of range (0-29): {frames}",
                line_number=None
            ))
        
        return True
    
    def _timecode_to_frames(self, timecode: str) -> Optional[int]:
        """Convert timecode to total frames. Returns None if invalid."""
        if not re.match(r'^\d{2}:\d{2}:\d{2}:\d{2}$', timecode):
            return None
        
        parts = timecode.split(':')
        hours, minutes, seconds, frames = map(int, parts)
        
        # Assuming 30fps for calculation (could be improved with FPS from header)
        total_frames = (hours * 3600 + minutes * 60 + seconds) * 30 + frames
        return total_frames
    
    def _validate_metadata(self, edit: Dict, metadata: Dict):
        """Validate metadata fields based on operation."""
        operation = edit.get('operation', '')
        track = edit.get('track', '')
        
        # Validate INPAINT metadata
        if operation == 'INPAINT':
            if 'region' not in metadata:
                self.errors.append(ValidationError(
                    "INPAINT operation requires REGION metadata",
                    line_number=None
                ))
            else:
                region = metadata['region']
                if isinstance(region, dict):
                    for key in ['x1', 'y1', 'x2', 'y2']:
                        if key not in region:
                            self.errors.append(ValidationError(
                                f"REGION missing required coordinate: {key}",
                                line_number=None
                            ))
                        else:
                            val = region[key]
                            if not (0.0 <= val <= 1.0):
                                self.errors.append(ValidationError(
                                    f"REGION {key} must be between 0.0 and 1.0, got: {val}",
                                    line_number=None
                                ))
            
            if 'action' not in metadata:
                self.errors.append(ValidationError(
                    "INPAINT operation requires ACTION metadata",
                    line_number=None
                ))
            else:
                action = metadata['action']
                if action not in self.VALID_INPAINT_ACTIONS:
                    self.errors.append(ValidationError(
                        f"Invalid INPAINT ACTION: {action}. "
                        f"Valid actions: {self.VALID_INPAINT_ACTIONS}",
                        line_number=None
                    ))
            
            if 'strength' in metadata:
                strength = metadata['strength']
                if not isinstance(strength, (int, float)):
                    self.errors.append(ValidationError(
                        f"STRENGTH must be a number, got: {type(strength)}",
                        line_number=None
                    ))
                elif not (0.0 <= strength <= 1.0):
                    self.errors.append(ValidationError(
                        f"STRENGTH must be between 0.0 and 1.0, got: {strength}",
                        line_number=None
                    ))
            
            if 'seed' in metadata:
                seed = metadata['seed']
                if type(seed) is not int:
                    self.errors.append(ValidationError(
                        f"SEED must be an integer, got: {type(seed)}",
                        line_number=None
                    ))
        
        # Validate REPLACE metadata for captions
        if operation == 'REPLACE' and track == 'S':
            if 'original_text' not in metadata:
                self.warnings.append(
                    "Caption REPLACE operation should include ORIGINAL_TEXT"
                )
            if 'replacement' not in metadata:
                self.errors.append(ValidationError(
                    "Caption REPLACE operation requires REPLACEMENT metadata",
                    line_number=None
                ))
        
        # Validate MODIFY metadata for captions
        if operation == 'MODIFY' and track == 'S':
            if 'original_text' not in metadata:
                self.errors.append(ValidationError(
                    "Caption MODIFY operation requires ORIGINAL_TEXT metadata",
                    line_number=None
                ))
            if 'replacement' not in metadata:
                self.errors.append(ValidationError(
                    "Caption MODIFY operation requires REPLACEMENT metadata",
                    line_number=None
                ))
        
        # Validate CHANNEL metadata
        if 'channel' in metadata:
            channel = metadata['channel']
            if not isinstance(channel, int) or channel < 1:
                self.errors.append(ValidationError(
                    f"CHANNEL must be a positive integer, got: {channel}",
                    line_number=None
                ))


def validate_file(filename: str, strict: bool = True) -> Tuple[bool, List[ValidationError], List[str]]:
    """
    Convenience function to validate an AIEDL file.
    
    Args:
        filename: Path to AIEDL file
        strict: If True, enforce strict validation
    
    Returns:
        Tuple of (is_valid, errors, warnings)
    """
    validator = AIEDLValidator(strict=strict)
    return validator.validate_file(filename)


if __name__ == '__main__':
    import sys
    import os
    
    if len(sys.argv) < 2:
        print("Usage: python validator.py <aiedl_file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    if not os.path.exists(filename):
        print(f"Error: File not found: {filename}")
        sys.exit(1)
    
    is_valid, errors, warnings = validate_file(filename)
    
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
        print()
    
    if errors:
        print("Errors:")
        for error in errors:
            print(f"  - {error}")
        print()
        print(f"Validation failed: {len(errors)} error(s) found")
        sys.exit(1)
    else:
        print("Validation passed!")
        if warnings:
            print(f"({len(warnings)} warning(s))")
        sys.exit(0)

