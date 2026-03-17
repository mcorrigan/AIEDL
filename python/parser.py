import re

def parse_edl_with_ai(filename):
    """
    Parse an AIEDL (AI Edit Decision List) file.
    
    Returns a list of edit dictionaries, each containing:
    - edit_number: The edit sequence number
    - reel: The reel/type identifier (AX, AI, etc.)
    - track: The track type (V, A1, S, etc.)
    - operation: The operation type (C, INPAINT, MUTE, REPLACE, MODIFY, etc.)
    - timecodes: List of timecodes [source_in, source_out, record_in, record_out]
    - metadata: Dictionary of metadata fields (REGION, ACTION, TARGET, etc.)
    """
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    edits = []
    current_edit = {}
    metadata = {}
    
    for line in lines:
        original_line = line
        line = line.strip()
        if not line or line.startswith('#'):  # Skip empty lines and comments
            continue
            
        # Parse header metadata
        if line.startswith('TITLE'):
            continue
        elif line.startswith('FPS'):
            continue
        elif line.startswith('AI_VERSION'):
            continue
        
        # Parse edit line: "001  AX       V     C        00:00:00:00 00:00:05:00 00:00:10:00 00:00:15:00"
        # Check if line starts with 3 digits followed by spaces and 2 uppercase letters
        if re.match(r'^\d{3}\s+[A-Z]{2}', line):
            if current_edit:
                current_edit['metadata'] = metadata.copy()  # Create a copy of metadata
                edits.append(current_edit)
            
            # Parse the edit line
            parts = line.split()
            # Need at least: edit_number, reel, track, operation, and at least one timecode (6 parts minimum)
            if len(parts) >= 6:
                current_edit = {
                    'edit_number': parts[0],
                    'reel': parts[1],
                    'track': parts[2],
                    'operation': parts[3],
                    'timecodes': parts[4:8] if len(parts) >= 8 else parts[4:]
                }
                metadata = {}  # Reset metadata for new edit
        
        # Parse metadata fields (only if we have a current edit)
        elif current_edit and line.startswith('* FROM CLIP NAME'):
            metadata['from_clip_name'] = line.split(':', 1)[1].strip() if ':' in line else ''
        elif current_edit and line.startswith('* REGION'):
            region_str = line.split(':', 1)[1].strip().split('#')[0].strip()  # Remove comments
            # Parse region format: (x1:.1, y1:.2, x2:.3, y2:.4)
            # Convert to dictionary format
            region_dict = {}
            region_str = region_str.strip('()')
            for part in region_str.split(','):
                part = part.strip()
                if ':' in part:
                    key, value = part.split(':')
                    region_dict[key.strip()] = float(value.strip())
            metadata['region'] = region_dict
        elif current_edit and line.startswith('* ACTION'):
            metadata['action'] = line.split(':', 1)[1].strip().split('#')[0].strip()
        elif current_edit and line.startswith('* TARGET'):
            metadata['target'] = line.split(':', 1)[1].strip()
        elif current_edit and line.startswith('* STRENGTH'):
            metadata['strength'] = float(line.split(':', 1)[1].strip())
        elif current_edit and line.startswith('* REPLACEMENT'):
            metadata['replacement'] = line.split(':', 1)[1].strip()
        elif current_edit and line.startswith('* ORIGINAL_TEXT'):
            metadata['original_text'] = line.split(':', 1)[1].strip()
        elif current_edit and line.startswith('* DESCRIPTION'):
            metadata['description'] = line.split(':', 1)[1].strip()
        elif current_edit and line.startswith('* CHANNEL'):
            metadata['channel'] = int(line.split(':', 1)[1].strip())
        elif current_edit and line.startswith('* MODEL'):
            metadata['model'] = line.split(':', 1)[1].strip()
        elif current_edit and line.startswith('* SEED'):
            metadata['seed'] = int(line.split(':', 1)[1].strip().split('#')[0].strip())
    
    # Add the last edit
    if current_edit:
        current_edit['metadata'] = metadata.copy()  # Create a copy of metadata
        edits.append(current_edit)
    
    return edits

# Example usage
if __name__ == '__main__':
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sample_file = os.path.join(script_dir, 'sample.ai.edl')
    edl_data = parse_edl_with_ai(sample_file)
    print(f"Parsed {len(edl_data)} edits:")
    for i, edit in enumerate(edl_data, 1):
        print(f"\nEdit {i}: {edit['edit_number']} - {edit['reel']} {edit['track']} {edit['operation']}")
        print(f"  Timecodes: {edit['timecodes']}")
        if edit['metadata']:
            print(f"  Metadata: {edit['metadata']}")
