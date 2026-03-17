/**
 * Example usage of AIEDL JavaScript library
 */

// For Node.js
const AIEDL = require('./aiedl.js');
const { Parser, Builder, Validator, Timecode, Region } = AIEDL;

// Create a new AIEDL file
const builder = new Builder('example.ai.edl', 'Example Movie', 24.0);

// Add a video cut
const sourceIn = new Timecode(0, 0, 0, 0);
const sourceOut = new Timecode(0, 0, 5, 0);
const recordIn = new Timecode(0, 0, 10, 0);
const recordOut = new Timecode(0, 0, 15, 0);

builder.addVideoCut(sourceIn, sourceOut, recordIn, recordOut, 'Scene1');

// Add a video inpaint
const inpaintIn = new Timecode(0, 0, 12, 0);
const inpaintOut = new Timecode(0, 0, 14, 0);
const region = new Region(0.1, 0.2, 0.3, 0.4);

builder.addVideoInpaint(inpaintIn, inpaintOut, region, 'REMOVE_OBJECT', 'Remove chair', 0.8);
// For reproducible generative output, add "* SEED: <integer>" to the INPAINT metadata.

// Add an audio mute
const muteIn = new Timecode(0, 1, 10, 12);
const muteOut = new Timecode(0, 1, 12, 5);

builder.addAudioMute(muteIn, muteOut, muteIn, muteOut, 'Mute profanity');

// Add a caption replace
const captionIn = new Timecode(0, 3, 0, 0);
const captionOut = new Timecode(0, 3, 5, 0);

builder.addCaptionReplace(captionIn, captionOut, captionIn, captionOut,
                          '"What the hell?"', '"What?"', 'Remove profanity from captions');

// Save file (Node.js)
const fs = require('fs');
fs.writeFileSync('example.ai.edl', builder.toString(), 'utf8');
console.log('Created example.ai.edl');

// Parse and validate
const content = fs.readFileSync('example.ai.edl', 'utf8');
const file = Parser.parse(content);
const validator = new Validator(true);
const result = validator.validate(file);

if (result.isValid) {
    console.log('File is valid!');
    console.log(`Found ${file.edits.length} edits`);
} else {
    console.log('Validation failed:');
    for (const error of result.errors) {
        console.log(`  Error: ${error.message}`);
    }
}

