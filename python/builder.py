"""
Builder for creating AIEDL (AI Edit Decision List) files.

Provides a programmatic interface for generating AIEDL files.
"""

from typing import Optional, Dict, List, Union


class AIEDLBuilder:
    """Builder class for creating AIEDL files."""
    
    def __init__(self, output_file: str, title: str, fps: Union[int, float] = 24, ai_version: str = "1.0"):
        """
        Initialize AIEDL builder.
        
        Args:
            output_file: Path to output AIEDL file
            title: Project title
            fps: Frame rate (default: 24)
            ai_version: AIEDL specification version (default: "1.0")
        """
        self.output_file = output_file
        self.title = title
        self.fps = fps
        self.ai_version = ai_version
        self.edits: List[Dict] = []
        self.edit_counter = 0  # Will be incremented to 1 on first use
        
        # Write header
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(f"TITLE: {title}\n")
            f.write(f"FPS: {fps}\n")
            f.write(f"AI_VERSION: {ai_version}\n")
            f.write("\n")
    
    def add_video_cut(self, source_in: str, source_out: str, record_in: str, record_out: str,
                     clip_name: Optional[str] = None) -> int:
        """
        Add a video cut/edit operation.
        
        Args:
            source_in: Source material in point (HH:MM:SS:FF)
            source_out: Source material out point (HH:MM:SS:FF)
            record_in: Record timeline in point (HH:MM:SS:FF)
            record_out: Record timeline out point (HH:MM:SS:FF)
            clip_name: Optional clip name
        
        Returns:
            Edit number
        """
        edit_num = self._get_next_edit_number()
        metadata = {}
        if clip_name:
            metadata['from_clip_name'] = clip_name
        
        self._add_edit('AX', 'V', 'C', [source_in, source_out, record_in, record_out], metadata)
        return edit_num
    
    def add_video_inpaint(self, source_in: str, source_out: str, 
                         region: Dict[str, float], action: str,
                         target: Optional[str] = None, strength: Optional[float] = None,
                         model: Optional[str] = None) -> int:
        """
        Add a video inpaint operation.
        
        Args:
            source_in: Source material in point (HH:MM:SS:FF)
            source_out: Source material out point (HH:MM:SS:FF)
            region: Region dictionary with x1, y1, x2, y2 (0.0-1.0)
            action: Inpaint action (REMOVE_OBJECT, ADD_OBJECT, etc.)
            target: Optional target description
            strength: Optional strength (0.0-1.0)
            model: Optional AI model identifier
        
        Returns:
            Edit number
        """
        edit_num = self._get_next_edit_number()
        metadata = {
            'region': region,
            'action': action
        }
        if target:
            metadata['target'] = target
        if strength is not None:
            metadata['strength'] = strength
        if model:
            metadata['model'] = model
        
        self._add_edit('AI', 'V', 'INPAINT', [source_in, source_out], metadata)
        return edit_num
    
    def add_audio_mute(self, source_in: str, source_out: str, record_in: str, record_out: str,
                      description: str, channel: Optional[int] = None, track: str = 'A1') -> int:
        """
        Add an audio mute operation.
        
        Args:
            source_in: Source material in point (HH:MM:SS:FF)
            source_out: Source material out point (HH:MM:SS:FF)
            record_in: Record timeline in point (HH:MM:SS:FF)
            record_out: Record timeline out point (HH:MM:SS:FF)
            description: Description of why audio is muted
            channel: Optional specific audio channel (1, 2, etc.)
            track: Audio track (default: A1)
        
        Returns:
            Edit number
        """
        edit_num = self._get_next_edit_number()
        metadata = {'description': description}
        if channel:
            metadata['channel'] = channel
        
        self._add_edit('AX', track, 'MUTE', [source_in, source_out, record_in, record_out], metadata)
        return edit_num
    
    def add_audio_replace(self, source_in: str, source_out: str, record_in: str, record_out: str,
                         replacement: str, description: str, track: str = 'A1') -> int:
        """
        Add an audio replace operation.
        
        Args:
            source_in: Source material in point (HH:MM:SS:FF)
            source_out: Source material out point (HH:MM:SS:FF)
            record_in: Record timeline in point (HH:MM:SS:FF)
            record_out: Record timeline out point (HH:MM:SS:FF)
            replacement: Replacement audio content or description
            description: Description of the replacement
            track: Audio track (default: A1)
        
        Returns:
            Edit number
        """
        edit_num = self._get_next_edit_number()
        metadata = {
            'replacement': replacement,
            'description': description
        }
        
        self._add_edit('AX', track, 'REPLACE', [source_in, source_out, record_in, record_out], metadata)
        return edit_num
    
    def add_caption_replace(self, source_in: str, source_out: str, record_in: str, record_out: str,
                           original_text: str, replacement: str, description: str) -> int:
        """
        Add a caption replace operation.
        
        Args:
            source_in: Source material in point (HH:MM:SS:FF)
            source_out: Source material out point (HH:MM:SS:FF)
            record_in: Record timeline in point (HH:MM:SS:FF)
            record_out: Record timeline out point (HH:MM:SS:FF)
            original_text: Original caption text
            replacement: Replacement text
            description: Description of the change
        
        Returns:
            Edit number
        """
        edit_num = self._get_next_edit_number()
        metadata = {
            'original_text': original_text,
            'replacement': replacement,
            'description': description
        }
        
        self._add_edit('AX', 'S', 'REPLACE', [source_in, source_out, record_in, record_out], metadata)
        return edit_num
    
    def add_caption_mute(self, source_in: str, source_out: str, record_in: str, record_out: str,
                        description: str) -> int:
        """
        Add a caption mute operation (hide captions).
        
        Args:
            source_in: Source material in point (HH:MM:SS:FF)
            source_out: Source material out point (HH:MM:SS:FF)
            record_in: Record timeline in point (HH:MM:SS:FF)
            record_out: Record timeline out point (HH:MM:SS:FF)
            description: Description of why captions are hidden
        
        Returns:
            Edit number
        """
        edit_num = self._get_next_edit_number()
        metadata = {'description': description}
        
        self._add_edit('AX', 'S', 'MUTE', [source_in, source_out, record_in, record_out], metadata)
        return edit_num
    
    def add_caption_modify(self, source_in: str, source_out: str, record_in: str, record_out: str,
                          original_text: str, replacement: str, description: str) -> int:
        """
        Add a caption modify operation.
        
        Args:
            source_in: Source material in point (HH:MM:SS:FF)
            source_out: Source material out point (HH:MM:SS:FF)
            record_in: Record timeline in point (HH:MM:SS:FF)
            record_out: Record timeline out point (HH:MM:SS:FF)
            original_text: Original caption text
            replacement: Modified text
            description: Description of the modification
        
        Returns:
            Edit number
        """
        edit_num = self._get_next_edit_number()
        metadata = {
            'original_text': original_text,
            'replacement': replacement,
            'description': description
        }
        
        self._add_edit('AX', 'S', 'MODIFY', [source_in, source_out, record_in, record_out], metadata)
        return edit_num
    
    def _get_next_edit_number(self) -> int:
        """Get the next edit number and increment counter."""
        self.edit_counter += 1
        return self.edit_counter
    
    def _add_edit(self, reel: str, track: str, operation: str, timecodes: List[str], metadata: Dict):
        """Internal method to add an edit."""
        edit = {
            'edit_number': f"{self.edit_counter:03d}",
            'reel': reel,
            'track': track,
            'operation': operation,
            'timecodes': timecodes,
            'metadata': metadata
        }
        self.edits.append(edit)
        self._write_edit(edit)
    
    def _write_edit(self, edit: Dict):
        """Write a single edit to the file."""
        with open(self.output_file, 'a', encoding='utf-8') as f:
            # Write edit line
            edit_num = edit['edit_number']
            reel = edit['reel']
            track = edit['track']
            operation = edit['operation']
            timecodes = edit['timecodes']
            
            # Format timecodes with proper spacing
            timecode_str = ' '.join(timecodes)
            
            f.write(f"{edit_num}  {reel:<8} {track:<5} {operation:<9} {timecode_str}\n")
            
            # Write metadata
            metadata = edit['metadata']
            if 'from_clip_name' in metadata:
                f.write(f"* FROM CLIP NAME: {metadata['from_clip_name']}\n")
            if 'region' in metadata:
                region = metadata['region']
                f.write(f"* REGION: (x1:{region['x1']}, y1:{region['y1']}, x2:{region['x2']}, y2:{region['y2']})\n")
            if 'action' in metadata:
                f.write(f"* ACTION: {metadata['action']}\n")
            if 'target' in metadata:
                f.write(f"* TARGET: {metadata['target']}\n")
            if 'strength' in metadata:
                f.write(f"* STRENGTH: {metadata['strength']}\n")
            if 'replacement' in metadata:
                f.write(f"* REPLACEMENT: {metadata['replacement']}\n")
            if 'original_text' in metadata:
                f.write(f"* ORIGINAL_TEXT: {metadata['original_text']}\n")
            if 'description' in metadata:
                f.write(f"* DESCRIPTION: {metadata['description']}\n")
            if 'channel' in metadata:
                f.write(f"* CHANNEL: {metadata['channel']}\n")
            if 'model' in metadata:
                f.write(f"* MODEL: {metadata['model']}\n")
            
            f.write("\n")
    
    def close(self):
        """Close the builder (no-op, but provided for API consistency)."""
        pass


# Example usage
if __name__ == '__main__':
    builder = AIEDLBuilder('example.ai.edl', 'Example Movie', fps=24)
    
    # Add a video cut
    builder.add_video_cut(
        '00:00:00:00', '00:00:05:00',
        '00:00:10:00', '00:00:15:00',
        clip_name='Scene1'
    )
    
    # Add a video inpaint
    builder.add_video_inpaint(
        '00:00:12:00', '00:00:14:00',
        region={'x1': 0.1, 'y1': 0.2, 'x2': 0.3, 'y2': 0.4},
        action='REMOVE_OBJECT',
        target='Remove the chair',
        strength=0.8,
        model='stable-diffusion-v2'
    )
    
    # Add an audio mute
    builder.add_audio_mute(
        '00:01:10:12', '00:01:12:05',
        '00:01:10:12', '00:01:12:05',
        description='Mute profanity'
    )
    
    # Add a caption replace
    builder.add_caption_replace(
        '00:03:00:00', '00:03:05:00',
        '00:03:00:00', '00:03:05:00',
        original_text='"What the hell?"',
        replacement='"What?"',
        description='Remove profanity from captions'
    )
    
    print("Created example.ai.edl")

