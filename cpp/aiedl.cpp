/**
 * AIEDL (AI Edit Decision List) C++ Implementation
 */

#include "aiedl.h"
#include <fstream>
#include <sstream>
#include <regex>
#include <algorithm>
#include <iomanip>

namespace aiedl {

// Timecode implementation
std::string Timecode::toString() const {
    std::ostringstream oss;
    oss << std::setfill('0') << std::setw(2) << hours << ":"
        << std::setw(2) << minutes << ":"
        << std::setw(2) << seconds << ":"
        << std::setw(2) << frames;
    return oss.str();
}

Timecode Timecode::fromString(const std::string& str) {
    Timecode tc;
    std::regex pattern(R"((\d{2}):(\d{2}):(\d{2}):(\d{2}))");
    std::smatch matches;
    
    if (std::regex_match(str, matches, pattern)) {
        tc.hours = std::stoi(matches[1].str());
        tc.minutes = std::stoi(matches[2].str());
        tc.seconds = std::stoi(matches[3].str());
        tc.frames = std::stoi(matches[4].str());
    }
    return tc;
}

bool Timecode::isValid() const {
    return hours >= 0 && hours <= 23 &&
           minutes >= 0 && minutes <= 59 &&
           seconds >= 0 && seconds <= 59 &&
           frames >= 0 && frames <= 29;
}

// Region implementation
bool Region::isValid() const {
    return x1 >= 0.0 && x1 <= 1.0 &&
           y1 >= 0.0 && y1 <= 1.0 &&
           x2 >= 0.0 && x2 <= 1.0 &&
           y2 >= 0.0 && y2 <= 1.0 &&
           x1 < x2 && y1 < y2;
}

// Parser implementation
AIEDLFile Parser::parse(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        throw std::runtime_error("Cannot open file: " + filename);
    }
    
    std::vector<std::string> lines;
    std::string line;
    while (std::getline(file, line)) {
        lines.push_back(line);
    }
    
    return parseFromString(lines);
}

AIEDLFile Parser::parseFromString(const std::string& content) {
    std::vector<std::string> lines;
    std::istringstream iss(content);
    std::string line;
    while (std::getline(iss, line)) {
        lines.push_back(line);
    }
    return parseFromString(lines);
}

AIEDLFile Parser::parseFromString(const std::vector<std::string>& lines) {
    AIEDLFile file;
    std::vector<Edit> edits;
    Edit current_edit;
    EditMetadata current_metadata;
    bool in_edit = false;
    
    for (size_t i = 0; i < lines.size(); ++i) {
        std::string line = lines[i];
        
        // Trim whitespace
        line.erase(0, line.find_first_not_of(" \t\r\n"));
        line.erase(line.find_last_not_of(" \t\r\n") + 1);
        
        // Skip empty lines and comments
        if (line.empty() || line[0] == '#') {
            continue;
        }
        
        // Parse header
        if (line.find("TITLE:") == 0) {
            file.title = line.substr(6);
            // Trim whitespace
            file.title.erase(0, file.title.find_first_not_of(" \t"));
            file.title.erase(file.title.find_last_not_of(" \t") + 1);
        } else if (line.find("FPS:") == 0) {
            std::string fps_str = line.substr(4);
            fps_str.erase(0, fps_str.find_first_not_of(" \t"));
            file.fps = std::stod(fps_str);
        } else if (line.find("AI_VERSION:") == 0) {
            file.ai_version = line.substr(11);
            file.ai_version.erase(0, file.ai_version.find_first_not_of(" \t"));
            file.ai_version.erase(file.ai_version.find_last_not_of(" \t") + 1);
        }
        // Parse edit line
        else if (std::regex_match(line, std::regex(R"(^\d{3}\s+[A-Z]{2})"))) {
            if (in_edit) {
                current_edit.metadata = current_metadata;
                edits.push_back(current_edit);
                current_metadata = EditMetadata();
            }
            
            current_edit = parseEditLine(line);
            in_edit = true;
        }
        // Parse metadata
        else if (in_edit && line[0] == '*') {
            parseMetadata(lines, i, current_metadata);
        }
    }
    
    // Add last edit
    if (in_edit) {
        current_edit.metadata = current_metadata;
        edits.push_back(current_edit);
    }
    
    file.edits = edits;
    return file;
}

Edit Parser::parseEditLine(const std::string& line) {
    Edit edit;
    std::istringstream iss(line);
    std::vector<std::string> parts;
    std::string part;
    
    while (iss >> part) {
        parts.push_back(part);
    }
    
    if (parts.size() >= 6) {
        edit.edit_number = parts[0];
        edit.reel = parts[1];
        edit.track = parts[2];
        edit.operation = parts[3];
        
        for (size_t i = 4; i < parts.size() && i < 8; ++i) {
            edit.timecodes.push_back(Timecode::fromString(parts[i]));
        }
    }
    
    return edit;
}

void Parser::parseMetadata(const std::vector<std::string>& lines, size_t& index, EditMetadata& metadata) {
    std::string line = lines[index];
    
    if (line.find("* FROM CLIP NAME:") == 0) {
        metadata.from_clip_name = line.substr(18);
        metadata.from_clip_name.erase(0, metadata.from_clip_name.find_first_not_of(" \t"));
    } else if (line.find("* REGION:") == 0) {
        metadata.region = parseRegion(line.substr(9));
    } else if (line.find("* ACTION:") == 0) {
        std::string action = line.substr(9);
        size_t comment_pos = action.find('#');
        if (comment_pos != std::string::npos) {
            action = action.substr(0, comment_pos);
        }
        action.erase(0, action.find_first_not_of(" \t"));
        action.erase(action.find_last_not_of(" \t") + 1);
        metadata.action = action;
    } else if (line.find("* TARGET:") == 0) {
        metadata.target = line.substr(9);
        metadata.target.erase(0, metadata.target.find_first_not_of(" \t"));
    } else if (line.find("* STRENGTH:") == 0) {
        std::string strength_str = line.substr(11);
        strength_str.erase(0, strength_str.find_first_not_of(" \t"));
        metadata.strength = std::stod(strength_str);
    } else if (line.find("* REPLACEMENT:") == 0) {
        metadata.replacement = line.substr(14);
        metadata.replacement.erase(0, metadata.replacement.find_first_not_of(" \t"));
    } else if (line.find("* ORIGINAL_TEXT:") == 0) {
        metadata.original_text = line.substr(16);
        metadata.original_text.erase(0, metadata.original_text.find_first_not_of(" \t"));
    } else if (line.find("* DESCRIPTION:") == 0) {
        metadata.description = line.substr(14);
        metadata.description.erase(0, metadata.description.find_first_not_of(" \t"));
    } else if (line.find("* CHANNEL:") == 0) {
        std::string channel_str = line.substr(10);
        channel_str.erase(0, channel_str.find_first_not_of(" \t"));
        metadata.channel = std::stoi(channel_str);
    } else if (line.find("* MODEL:") == 0) {
        metadata.model = line.substr(8);
        metadata.model.erase(0, metadata.model.find_first_not_of(" \t"));
        metadata.model.erase(metadata.model.find_last_not_of(" \t") + 1);
    }
}

Region Parser::parseRegion(const std::string& str) {
    Region region;
    std::regex pattern(R"(x1:([\d.]+),\s*y1:([\d.]+),\s*x2:([\d.]+),\s*y2:([\d.]+))");
    std::smatch matches;
    
    std::string clean_str = str;
    clean_str.erase(0, clean_str.find_first_not_of(" \t()"));
    clean_str.erase(clean_str.find_last_not_of(" \t)") + 1);
    
    if (std::regex_search(clean_str, matches, pattern)) {
        region.x1 = std::stod(matches[1].str());
        region.y1 = std::stod(matches[2].str());
        region.x2 = std::stod(matches[3].str());
        region.y2 = std::stod(matches[4].str());
    }
    
    return region;
}

// Builder implementation
Builder::Builder(const std::string& filename, const std::string& title, double fps, const std::string& ai_version)
    : filename_(filename), title_(title), fps_(fps), ai_version_(ai_version), edit_counter_(0) {
    writeHeader();
}

Builder::~Builder() {
    close();
}

void Builder::writeHeader() {
    std::ofstream file(filename_, std::ios::out);
    if (!file.is_open()) {
        throw std::runtime_error("Cannot open file for writing: " + filename_);
    }
    
    file << "TITLE: " << title_ << "\n";
    file << "FPS: " << fps_ << "\n";
    file << "AI_VERSION: " << ai_version_ << "\n";
    file << "\n";
}

int Builder::getNextEditNumber() {
    return ++edit_counter_;
}

void Builder::writeEdit(const Edit& edit) {
    std::ofstream file(filename_, std::ios::app);
    if (!file.is_open()) {
        throw std::runtime_error("Cannot open file for writing: " + filename_);
    }
    
    file << edit.edit_number << "  " << std::left << std::setw(8) << edit.reel
         << " " << std::setw(5) << edit.track << " " << std::setw(9) << edit.operation;
    
    for (const auto& tc : edit.timecodes) {
        file << " " << tc.toString();
    }
    file << "\n";
    
    const auto& meta = edit.metadata;
    if (!meta.from_clip_name.empty()) {
        file << "* FROM CLIP NAME: " << meta.from_clip_name << "\n";
    }
    if (meta.hasRegion()) {
        file << "* REGION: (x1:" << meta.region.x1 << ", y1:" << meta.region.y1
             << ", x2:" << meta.region.x2 << ", y2:" << meta.region.y2 << ")\n";
    }
    if (!meta.action.empty()) {
        file << "* ACTION: " << meta.action << "\n";
    }
    if (!meta.target.empty()) {
        file << "* TARGET: " << meta.target << "\n";
    }
    if (meta.hasStrength()) {
        file << "* STRENGTH: " << meta.strength << "\n";
    }
    if (!meta.replacement.empty()) {
        file << "* REPLACEMENT: " << meta.replacement << "\n";
    }
    if (!meta.original_text.empty()) {
        file << "* ORIGINAL_TEXT: " << meta.original_text << "\n";
    }
    if (!meta.description.empty()) {
        file << "* DESCRIPTION: " << meta.description << "\n";
    }
    if (meta.hasChannel()) {
        file << "* CHANNEL: " << meta.channel << "\n";
    }
    if (meta.hasModel()) {
        file << "* MODEL: " << meta.model << "\n";
    }
    
    file << "\n";
}

int Builder::addVideoCut(const Timecode& source_in, const Timecode& source_out,
                        const Timecode& record_in, const Timecode& record_out,
                        const std::string& clip_name) {
    Edit edit;
    edit.edit_number = std::to_string(getNextEditNumber());
    if (edit.edit_number.length() == 1) edit.edit_number = "00" + edit.edit_number;
    else if (edit.edit_number.length() == 2) edit.edit_number = "0" + edit.edit_number;
    edit.reel = "AX";
    edit.track = "V";
    edit.operation = "C";
    edit.timecodes = {source_in, source_out, record_in, record_out};
    if (!clip_name.empty()) {
        edit.metadata.from_clip_name = clip_name;
    }
    writeEdit(edit);
    edits_.push_back(edit);
    return edit_counter_;
}

int Builder::addVideoInpaint(const Timecode& source_in, const Timecode& source_out,
                            const Region& region, const std::string& action,
                            const std::string& target, double strength, const std::string& model) {
    Edit edit;
    edit.edit_number = std::to_string(getNextEditNumber());
    if (edit.edit_number.length() == 1) edit.edit_number = "00" + edit.edit_number;
    else if (edit.edit_number.length() == 2) edit.edit_number = "0" + edit.edit_number;
    edit.reel = "AI";
    edit.track = "V";
    edit.operation = "INPAINT";
    edit.timecodes = {source_in, source_out};
    edit.metadata.region = region;
    edit.metadata.action = action;
    if (!target.empty()) edit.metadata.target = target;
    if (strength > 0.0) edit.metadata.strength = strength;
    if (!model.empty()) edit.metadata.model = model;
    writeEdit(edit);
    edits_.push_back(edit);
    return edit_counter_;
}

int Builder::addAudioMute(const Timecode& source_in, const Timecode& source_out,
                         const Timecode& record_in, const Timecode& record_out,
                         const std::string& description, int channel, const std::string& track) {
    Edit edit;
    edit.edit_number = std::to_string(getNextEditNumber());
    if (edit.edit_number.length() == 1) edit.edit_number = "00" + edit.edit_number;
    else if (edit.edit_number.length() == 2) edit.edit_number = "0" + edit.edit_number;
    edit.reel = "AX";
    edit.track = track;
    edit.operation = "MUTE";
    edit.timecodes = {source_in, source_out, record_in, record_out};
    edit.metadata.description = description;
    if (channel > 0) edit.metadata.channel = channel;
    writeEdit(edit);
    edits_.push_back(edit);
    return edit_counter_;
}

int Builder::addAudioReplace(const Timecode& source_in, const Timecode& source_out,
                            const Timecode& record_in, const Timecode& record_out,
                            const std::string& replacement, const std::string& description,
                            const std::string& track) {
    Edit edit;
    edit.edit_number = std::to_string(getNextEditNumber());
    if (edit.edit_number.length() == 1) edit.edit_number = "00" + edit.edit_number;
    else if (edit.edit_number.length() == 2) edit.edit_number = "0" + edit.edit_number;
    edit.reel = "AX";
    edit.track = track;
    edit.operation = "REPLACE";
    edit.timecodes = {source_in, source_out, record_in, record_out};
    edit.metadata.replacement = replacement;
    edit.metadata.description = description;
    writeEdit(edit);
    edits_.push_back(edit);
    return edit_counter_;
}

int Builder::addCaptionReplace(const Timecode& source_in, const Timecode& source_out,
                               const Timecode& record_in, const Timecode& record_out,
                               const std::string& original_text, const std::string& replacement,
                               const std::string& description) {
    Edit edit;
    edit.edit_number = std::to_string(getNextEditNumber());
    if (edit.edit_number.length() == 1) edit.edit_number = "00" + edit.edit_number;
    else if (edit.edit_number.length() == 2) edit.edit_number = "0" + edit.edit_number;
    edit.reel = "AX";
    edit.track = "S";
    edit.operation = "REPLACE";
    edit.timecodes = {source_in, source_out, record_in, record_out};
    edit.metadata.original_text = original_text;
    edit.metadata.replacement = replacement;
    edit.metadata.description = description;
    writeEdit(edit);
    edits_.push_back(edit);
    return edit_counter_;
}

int Builder::addCaptionMute(const Timecode& source_in, const Timecode& source_out,
                            const Timecode& record_in, const Timecode& record_out,
                            const std::string& description) {
    Edit edit;
    edit.edit_number = std::to_string(getNextEditNumber());
    if (edit.edit_number.length() == 1) edit.edit_number = "00" + edit.edit_number;
    else if (edit.edit_number.length() == 2) edit.edit_number = "0" + edit.edit_number;
    edit.reel = "AX";
    edit.track = "S";
    edit.operation = "MUTE";
    edit.timecodes = {source_in, source_out, record_in, record_out};
    edit.metadata.description = description;
    writeEdit(edit);
    edits_.push_back(edit);
    return edit_counter_;
}

int Builder::addCaptionModify(const Timecode& source_in, const Timecode& source_out,
                              const Timecode& record_in, const Timecode& record_out,
                              const std::string& original_text, const std::string& replacement,
                              const std::string& description) {
    Edit edit;
    edit.edit_number = std::to_string(getNextEditNumber());
    if (edit.edit_number.length() == 1) edit.edit_number = "00" + edit.edit_number;
    else if (edit.edit_number.length() == 2) edit.edit_number = "0" + edit.edit_number;
    edit.reel = "AX";
    edit.track = "S";
    edit.operation = "MODIFY";
    edit.timecodes = {source_in, source_out, record_in, record_out};
    edit.metadata.original_text = original_text;
    edit.metadata.replacement = replacement;
    edit.metadata.description = description;
    writeEdit(edit);
    edits_.push_back(edit);
    return edit_counter_;
}

void Builder::close() {
    // File is already written incrementally, nothing to do
}

// Validator implementation
ValidationResult Validator::validate(const std::string& filename) {
    try {
        AIEDLFile file = Parser::parse(filename);
        return validate(file);
    } catch (const std::exception& e) {
        result_.is_valid = false;
        result_.errors.push_back(ValidationError(e.what()));
        return result_;
    }
}

ValidationResult Validator::validate(const AIEDLFile& file) {
    result_ = ValidationResult();
    
    validateHeader(file);
    
    for (size_t i = 0; i < file.edits.size(); ++i) {
        validateEdit(file.edits[i], i);
    }
    
    result_.is_valid = result_.errors.empty();
    return result_;
}

void Validator::validateHeader(const AIEDLFile& file) {
    if (strict_) {
        if (file.title.empty()) {
            result_.errors.push_back(ValidationError("Missing required header: TITLE"));
        }
        if (file.fps <= 0 || file.fps > 120) {
            result_.errors.push_back(ValidationError("FPS value out of valid range (0-120)"));
        }
        if (file.ai_version != "1.0") {
            result_.warnings.push_back("AI_VERSION is " + file.ai_version + ", expected 1.0");
        }
    }
}

void Validator::validateEdit(const Edit& edit, size_t index) {
    if (edit.edit_number.length() != 3) {
        result_.errors.push_back(ValidationError("Edit number must be 3 digits: " + edit.edit_number));
    }
    
    if (!isValidReel(edit.reel)) {
        result_.errors.push_back(ValidationError("Invalid reel type: " + edit.reel));
    }
    
    if (!isValidTrack(edit.track)) {
        result_.errors.push_back(ValidationError("Invalid track type: " + edit.track));
    }
    
    if (!isValidOperation(edit.operation, edit.track)) {
        result_.errors.push_back(ValidationError("Invalid operation '" + edit.operation + "' for track '" + edit.track + "'"));
    }
    
    for (const auto& tc : edit.timecodes) {
        validateTimecode(tc);
    }
    
    validateMetadata(edit);
}

void Validator::validateTimecode(const Timecode& tc) {
    if (!tc.isValid()) {
        result_.errors.push_back(ValidationError("Invalid timecode: " + tc.toString()));
    }
}

void Validator::validateMetadata(const Edit& edit) {
    if (edit.operation == "INPAINT") {
        if (!edit.metadata.hasRegion()) {
            result_.errors.push_back(ValidationError("INPAINT operation requires REGION metadata"));
        }
        if (edit.metadata.action.empty()) {
            result_.errors.push_back(ValidationError("INPAINT operation requires ACTION metadata"));
        }
        if (edit.metadata.hasStrength() && (edit.metadata.strength < 0.0 || edit.metadata.strength > 1.0)) {
            result_.errors.push_back(ValidationError("STRENGTH must be between 0.0 and 1.0"));
        }
    }
}

bool Validator::isValidReel(const std::string& reel) const {
    return reel == "AX" || reel == "AI";
}

bool Validator::isValidTrack(const std::string& track) const {
    if (track == "V" || track == "S") return true;
    if (track.length() == 2 && track[0] == 'A') {
        int num = std::stoi(track.substr(1));
        return num >= 1 && num <= 32;
    }
    return false;
}

bool Validator::isValidOperation(const std::string& operation, const std::string& track) const {
    if (track == "V") {
        return operation == "C" || operation == "INPAINT";
    } else if (track[0] == 'A') {
        return operation == "MUTE" || operation == "REPLACE";
    } else if (track == "S") {
        return operation == "REPLACE" || operation == "MUTE" || operation == "MODIFY";
    }
    return false;
}

} // namespace aiedl

