/**
 * AIEDL (AI Edit Decision List) JavaScript Implementation
 * 
 * Provides parsing, validation, and building functionality for AIEDL files.
 */

class Timecode {
    constructor(hours = 0, minutes = 0, seconds = 0, frames = 0) {
        this.hours = hours;
        this.minutes = minutes;
        this.seconds = seconds;
        this.frames = frames;
    }

    static fromString(str) {
        const match = str.match(/(\d{2}):(\d{2}):(\d{2}):(\d{2})/);
        if (!match) {
            throw new Error(`Invalid timecode format: ${str}`);
        }
        return new Timecode(
            parseInt(match[1], 10),
            parseInt(match[2], 10),
            parseInt(match[3], 10),
            parseInt(match[4], 10)
        );
    }

    toString() {
        return `${String(this.hours).padStart(2, '0')}:${String(this.minutes).padStart(2, '0')}:${String(this.seconds).padStart(2, '0')}:${String(this.frames).padStart(2, '0')}`;
    }

    isValid() {
        return this.hours >= 0 && this.hours <= 23 &&
               this.minutes >= 0 && this.minutes <= 59 &&
               this.seconds >= 0 && this.seconds <= 59 &&
               this.frames >= 0 && this.frames <= 29;
    }
}

class Region {
    constructor(x1 = 0, y1 = 0, x2 = 0, y2 = 0) {
        this.x1 = x1;
        this.y1 = y1;
        this.x2 = x2;
        this.y2 = y2;
    }

    isValid() {
        return this.x1 >= 0 && this.x1 <= 1.0 &&
               this.y1 >= 0 && this.y1 <= 1.0 &&
               this.x2 >= 0 && this.x2 <= 1.0 &&
               this.y2 >= 0 && this.y2 <= 1.0 &&
               this.x1 < this.x2 && this.y1 < this.y2;
    }
}

class EditMetadata {
    constructor() {
        this.from_clip_name = '';
        this.region = null;
        this.action = '';
        this.target = '';
        this.strength = 0;
        this.replacement = '';
        this.original_text = '';
        this.description = '';
        this.channel = 0;
        this.model = '';
    }

    hasRegion() {
        return this.region !== null && this.region.isValid();
    }

    hasStrength() {
        return this.strength > 0;
    }

    hasChannel() {
        return this.channel > 0;
    }
}

class Edit {
    constructor() {
        this.edit_number = '';
        this.reel = '';
        this.track = '';
        this.operation = '';
        this.timecodes = [];
        this.metadata = new EditMetadata();
    }
}

class AIEDLFile {
    constructor() {
        this.title = '';
        this.fps = 24.0;
        this.ai_version = '1.0';
        this.edits = [];
    }
}

class Parser {
    static parse(content) {
        const lines = content.split(/\r?\n/);
        const file = new AIEDLFile();
        const edits = [];
        let currentEdit = null;
        let currentMetadata = null;

        for (let i = 0; i < lines.length; i++) {
            let line = lines[i].trim();

            // Skip empty lines and comments
            if (!line || line.startsWith('#')) {
                continue;
            }

            // Parse header
            if (line.startsWith('TITLE:')) {
                file.title = line.substring(6).trim();
            } else if (line.startsWith('FPS:')) {
                file.fps = parseFloat(line.substring(4).trim());
            } else if (line.startsWith('AI_VERSION:')) {
                file.ai_version = line.substring(11).trim();
            }
            // Parse edit line
            else if (/^\d{3}\s+[A-Z]{2}/.test(line)) {
                if (currentEdit) {
                    currentEdit.metadata = currentMetadata;
                    edits.push(currentEdit);
                }
                currentEdit = this.parseEditLine(line);
                currentMetadata = new EditMetadata();
            }
            // Parse metadata
            else if (currentEdit && line.startsWith('*')) {
                this.parseMetadata(line, currentMetadata);
            }
        }

        // Add last edit
        if (currentEdit) {
            currentEdit.metadata = currentMetadata;
            edits.push(currentEdit);
        }

        file.edits = edits;
        return file;
    }

    static parseEditLine(line) {
        const parts = line.split(/\s+/);
        const edit = new Edit();

        if (parts.length >= 6) {
            edit.edit_number = parts[0];
            edit.reel = parts[1];
            edit.track = parts[2];
            edit.operation = parts[3];

            for (let i = 4; i < parts.length && i < 8; i++) {
                edit.timecodes.push(Timecode.fromString(parts[i]));
            }
        }

        return edit;
    }

    static parseMetadata(line, metadata) {
        if (line.startsWith('* FROM CLIP NAME:')) {
            metadata.from_clip_name = line.substring(18).trim();
        } else if (line.startsWith('* REGION:')) {
            metadata.region = this.parseRegion(line.substring(9).trim());
        } else if (line.startsWith('* ACTION:')) {
            let action = line.substring(9).trim();
            const commentIndex = action.indexOf('#');
            if (commentIndex !== -1) {
                action = action.substring(0, commentIndex).trim();
            }
            metadata.action = action;
        } else if (line.startsWith('* TARGET:')) {
            metadata.target = line.substring(9).trim();
        } else if (line.startsWith('* STRENGTH:')) {
            metadata.strength = parseFloat(line.substring(11).trim());
        } else if (line.startsWith('* REPLACEMENT:')) {
            metadata.replacement = line.substring(14).trim();
        } else if (line.startsWith('* ORIGINAL_TEXT:')) {
            metadata.original_text = line.substring(16).trim();
        } else if (line.startsWith('* DESCRIPTION:')) {
            metadata.description = line.substring(14).trim();
        } else if (line.startsWith('* CHANNEL:')) {
            metadata.channel = parseInt(line.substring(10).trim(), 10);
        } else if (line.startsWith('* MODEL:')) {
            metadata.model = line.substring(8).trim();
        }
    }

    static parseRegion(str) {
        const match = str.match(/x1:([\d.]+),\s*y1:([\d.]+),\s*x2:([\d.]+),\s*y2:([\d.]+)/);
        if (match) {
            return new Region(
                parseFloat(match[1]),
                parseFloat(match[2]),
                parseFloat(match[3]),
                parseFloat(match[4])
            );
        }
        return new Region();
    }
}

class Builder {
    constructor(filename, title, fps = 24.0, aiVersion = '1.0') {
        this.filename = filename;
        this.title = title;
        this.fps = fps;
        this.aiVersion = aiVersion;
        this.editCounter = 0;
        this.edits = [];
        this.content = '';

        this.writeHeader();
    }

    writeHeader() {
        this.content = `TITLE: ${this.title}\n`;
        this.content += `FPS: ${this.fps}\n`;
        this.content += `AI_VERSION: ${this.aiVersion}\n`;
        this.content += '\n';
    }

    getNextEditNumber() {
        return ++this.editCounter;
    }

    formatEditNumber(num) {
        return String(num).padStart(3, '0');
    }

    writeEdit(edit) {
        let line = `${edit.edit_number}  ${edit.reel.padEnd(8)} ${edit.track.padEnd(5)} ${edit.operation.padEnd(9)}`;
        for (const tc of edit.timecodes) {
            line += ` ${tc.toString()}`;
        }
        this.content += line + '\n';

        const meta = edit.metadata;
        if (meta.from_clip_name) {
            this.content += `* FROM CLIP NAME: ${meta.from_clip_name}\n`;
        }
        if (meta.hasRegion()) {
            this.content += `* REGION: (x1:${meta.region.x1}, y1:${meta.region.y1}, x2:${meta.region.x2}, y2:${meta.region.y2})\n`;
        }
        if (meta.action) {
            this.content += `* ACTION: ${meta.action}\n`;
        }
        if (meta.target) {
            this.content += `* TARGET: ${meta.target}\n`;
        }
        if (meta.hasStrength()) {
            this.content += `* STRENGTH: ${meta.strength}\n`;
        }
        if (meta.replacement) {
            this.content += `* REPLACEMENT: ${meta.replacement}\n`;
        }
        if (meta.original_text) {
            this.content += `* ORIGINAL_TEXT: ${meta.original_text}\n`;
        }
        if (meta.description) {
            this.content += `* DESCRIPTION: ${meta.description}\n`;
        }
        if (meta.hasChannel()) {
            this.content += `* CHANNEL: ${meta.channel}\n`;
        }
        if (meta.model) {
            this.content += `* MODEL: ${meta.model}\n`;
        }

        this.content += '\n';
    }

    addVideoCut(sourceIn, sourceOut, recordIn, recordOut, clipName = '') {
        const edit = new Edit();
        edit.edit_number = this.formatEditNumber(this.getNextEditNumber());
        edit.reel = 'AX';
        edit.track = 'V';
        edit.operation = 'C';
        edit.timecodes = [sourceIn, sourceOut, recordIn, recordOut];
        if (clipName) {
            edit.metadata.from_clip_name = clipName;
        }
        this.writeEdit(edit);
        this.edits.push(edit);
        return this.editCounter;
    }

    addVideoInpaint(sourceIn, sourceOut, region, action, target = '', strength = 0, model = '') {
        const edit = new Edit();
        edit.edit_number = this.formatEditNumber(this.getNextEditNumber());
        edit.reel = 'AI';
        edit.track = 'V';
        edit.operation = 'INPAINT';
        edit.timecodes = [sourceIn, sourceOut];
        edit.metadata.region = region;
        edit.metadata.action = action;
        if (target) edit.metadata.target = target;
        if (strength > 0) edit.metadata.strength = strength;
        if (model) edit.metadata.model = model;
        this.writeEdit(edit);
        this.edits.push(edit);
        return this.editCounter;
    }

    addAudioMute(sourceIn, sourceOut, recordIn, recordOut, description, channel = 0, track = 'A1') {
        const edit = new Edit();
        edit.edit_number = this.formatEditNumber(this.getNextEditNumber());
        edit.reel = 'AX';
        edit.track = track;
        edit.operation = 'MUTE';
        edit.timecodes = [sourceIn, sourceOut, recordIn, recordOut];
        edit.metadata.description = description;
        if (channel > 0) edit.metadata.channel = channel;
        this.writeEdit(edit);
        this.edits.push(edit);
        return this.editCounter;
    }

    addAudioReplace(sourceIn, sourceOut, recordIn, recordOut, replacement, description, track = 'A1') {
        const edit = new Edit();
        edit.edit_number = this.formatEditNumber(this.getNextEditNumber());
        edit.reel = 'AX';
        edit.track = track;
        edit.operation = 'REPLACE';
        edit.timecodes = [sourceIn, sourceOut, recordIn, recordOut];
        edit.metadata.replacement = replacement;
        edit.metadata.description = description;
        this.writeEdit(edit);
        this.edits.push(edit);
        return this.editCounter;
    }

    addCaptionReplace(sourceIn, sourceOut, recordIn, recordOut, originalText, replacement, description) {
        const edit = new Edit();
        edit.edit_number = this.formatEditNumber(this.getNextEditNumber());
        edit.reel = 'AX';
        edit.track = 'S';
        edit.operation = 'REPLACE';
        edit.timecodes = [sourceIn, sourceOut, recordIn, recordOut];
        edit.metadata.original_text = originalText;
        edit.metadata.replacement = replacement;
        edit.metadata.description = description;
        this.writeEdit(edit);
        this.edits.push(edit);
        return this.editCounter;
    }

    addCaptionMute(sourceIn, sourceOut, recordIn, recordOut, description) {
        const edit = new Edit();
        edit.edit_number = this.formatEditNumber(this.getNextEditNumber());
        edit.reel = 'AX';
        edit.track = 'S';
        edit.operation = 'MUTE';
        edit.timecodes = [sourceIn, sourceOut, recordIn, recordOut];
        edit.metadata.description = description;
        this.writeEdit(edit);
        this.edits.push(edit);
        return this.editCounter;
    }

    addCaptionModify(sourceIn, sourceOut, recordIn, recordOut, originalText, replacement, description) {
        const edit = new Edit();
        edit.edit_number = this.formatEditNumber(this.getNextEditNumber());
        edit.reel = 'AX';
        edit.track = 'S';
        edit.operation = 'MODIFY';
        edit.timecodes = [sourceIn, sourceOut, recordIn, recordOut];
        edit.metadata.original_text = originalText;
        edit.metadata.replacement = replacement;
        edit.metadata.description = description;
        this.writeEdit(edit);
        this.edits.push(edit);
        return this.editCounter;
    }

    toString() {
        return this.content;
    }

    // For Node.js: write to file
    save(callback) {
        if (typeof require !== 'undefined') {
            const fs = require('fs');
            fs.writeFile(this.filename, this.content, 'utf8', callback);
        } else {
            throw new Error('File system operations not available in browser environment');
        }
    }
}

class ValidationError extends Error {
    constructor(message, lineNumber = -1) {
        super(message);
        this.lineNumber = lineNumber;
    }
}

class Validator {
    constructor(strict = true) {
        this.strict = strict;
    }

    validate(file) {
        const result = {
            isValid: true,
            errors: [],
            warnings: []
        };

        if (typeof file === 'string') {
            // If file is a string, parse it first
            try {
                file = Parser.parse(file);
            } catch (e) {
                result.isValid = false;
                result.errors.push(new ValidationError(e.message));
                return result;
            }
        }

        this.validateHeader(file, result);
        
        for (let i = 0; i < file.edits.length; i++) {
            this.validateEdit(file.edits[i], i, result);
        }

        result.isValid = result.errors.length === 0;
        return result;
    }

    validateHeader(file, result) {
        if (this.strict) {
            if (!file.title) {
                result.errors.push(new ValidationError('Missing required header: TITLE'));
            }
            if (file.fps <= 0 || file.fps > 120) {
                result.errors.push(new ValidationError('FPS value out of valid range (0-120)'));
            }
            if (file.ai_version !== '1.0') {
                result.warnings.push(`AI_VERSION is ${file.ai_version}, expected 1.0`);
            }
        }
    }

    validateEdit(edit, index, result) {
        if (edit.edit_number.length !== 3) {
            result.errors.push(new ValidationError(`Edit number must be 3 digits: ${edit.edit_number}`));
        }

        if (!this.isValidReel(edit.reel)) {
            result.errors.push(new ValidationError(`Invalid reel type: ${edit.reel}`));
        }

        if (!this.isValidTrack(edit.track)) {
            result.errors.push(new ValidationError(`Invalid track type: ${edit.track}`));
        }

        if (!this.isValidOperation(edit.operation, edit.track)) {
            result.errors.push(new ValidationError(`Invalid operation '${edit.operation}' for track '${edit.track}'`));
        }

        for (const tc of edit.timecodes) {
            if (!tc.isValid()) {
                result.errors.push(new ValidationError(`Invalid timecode: ${tc.toString()}`));
            }
        }

        this.validateMetadata(edit, result);
    }

    validateMetadata(edit, result) {
        if (edit.operation === 'INPAINT') {
            if (!edit.metadata.hasRegion()) {
                result.errors.push(new ValidationError('INPAINT operation requires REGION metadata'));
            }
            if (!edit.metadata.action) {
                result.errors.push(new ValidationError('INPAINT operation requires ACTION metadata'));
            }
            if (edit.metadata.hasStrength() && (edit.metadata.strength < 0 || edit.metadata.strength > 1)) {
                result.errors.push(new ValidationError('STRENGTH must be between 0.0 and 1.0'));
            }
        }
    }

    isValidReel(reel) {
        return reel === 'AX' || reel === 'AI';
    }

    isValidTrack(track) {
        if (track === 'V' || track === 'S') return true;
        if (track.length === 2 && track[0] === 'A') {
            const num = parseInt(track.substring(1), 10);
            return num >= 1 && num <= 32;
        }
        return false;
    }

    isValidOperation(operation, track) {
        if (track === 'V') {
            return operation === 'C' || operation === 'INPAINT';
        } else if (track[0] === 'A') {
            return operation === 'MUTE' || operation === 'REPLACE';
        } else if (track === 'S') {
            return operation === 'REPLACE' || operation === 'MUTE' || operation === 'MODIFY';
        }
        return false;
    }
}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        Parser,
        Builder,
        Validator,
        Timecode,
        Region,
        EditMetadata,
        Edit,
        AIEDLFile,
        ValidationError
    };
}

// Export for ES6 modules
if (typeof window !== 'undefined') {
    window.AIEDL = {
        Parser,
        Builder,
        Validator,
        Timecode,
        Region,
        EditMetadata,
        Edit,
        AIEDLFile,
        ValidationError
    };
}

