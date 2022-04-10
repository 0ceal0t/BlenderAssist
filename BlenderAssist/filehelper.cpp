#include "filehelper.h"

void writeInt(vector<char>& buffer, int position, int value) {
    auto bytes = static_cast<char*>(static_cast<void*>(&value));
    for(int i = 0; i < sizeof(int); i++) {
        buffer[position + i] = bytes[i];
    }
}

std::streampos fileSize( const char* filePath ){
    std::streampos fsize = 0;
    std::ifstream file( filePath, std::ios::binary );

    fsize = file.tellg();
    file.seekg( 0, std::ios::end );
    fsize = file.tellg() - fsize;
    file.close();

    return fsize;
}

void readIntoVector(vector<char>& vec, ifstream &stream, int count) {
    vec.clear();
    vec.reserve(count);
    for(int i = 0; i < count; i++) {
        char c;
        stream.read((char*)&c, 1);
        vec.push_back(c);
    }
}

void writeFromVector(vector<char>& vec, ofstream& stream, int count) {
    for(int i = 0; i < count; i++) {
        stream.write(&vec[i], 1);
    }
}

// ============================

void SklbFile::read(hkStringBuf filename) {
    int fullSize = fileSize(filename.cString());

    ifstream stream(filename, ios::binary);
    if (stream.is_open()) {
        int headerVersion;
        int havokOffset;

        stream.clear();
        stream.seekg(4, ios::beg);
        stream.read((char*)&headerVersion, 4);

        if (headerVersion != 0x31333030) { // Header 1
            short int offset2;

            // Only 2 bytes for this header format
            stream.clear();
            stream.seekg(10, ios::beg);
            stream.read((char*)&offset2, 2);

            havokOffset = offset2;
        }
        else { // Header 2
            stream.clear();
            stream.seekg(12, ios::beg);
            stream.read((char*)&havokOffset, 4);
        }

        preHavokSize = havokOffset;
        havokSize = fullSize - preHavokSize;

        stream.clear();
        stream.seekg (0, ios::beg);
        readIntoVector(preHavok, stream, preHavokSize);

        stream.clear();
        stream.seekg(havokOffset, ios::beg);
        readIntoVector(havok, stream, havokSize);

        stream.close();
    }
    else {
        printf("Could not open stream %s\n", filename.cString());
    }
}

void SklbFile::writeHavok(hkStringBuf filename) {
    ofstream stream(filename, ios::binary);
    if (stream.is_open()) {
        writeFromVector(havok, stream, havokSize);

        stream.close();
    }
    else {
        printf("Could not open stream %s\n", filename.cString());
    }
}

// ============================

void PapFile::read(hkStringBuf filename) {
    int fullSize = fileSize(filename.cString());

    ifstream stream(filename, ios::binary);
    if (stream.is_open()) {
        int havokOffset;
        int timelineOffset;

        stream.clear();
        stream.seekg(18, ios::beg);
        stream.read((char*)&havokOffset, 4);

        stream.clear();
        stream.seekg(22, ios::beg);
        stream.read((char*)&timelineOffset, 4);

        preHavokSize = havokOffset;
        havokSize = timelineOffset - havokOffset;
        postHavokSize = fullSize - timelineOffset;

        stream.clear();
        stream.seekg (0, ios::beg);
        readIntoVector(preHavok, stream, preHavokSize);

        stream.clear();
        stream.seekg(havokOffset, ios::beg);
        readIntoVector(havok, stream, havokSize);

        stream.clear();
        stream.seekg(timelineOffset, ios::beg);
        readIntoVector(postHavok, stream, postHavokSize);

        stream.close();
    }
    else {
        printf("Could not open stream %s\n", filename.cString());
    }
}

void PapFile::writeHavok(hkStringBuf filename) {
    ofstream stream(filename, ios::binary);
    if (stream.is_open()) {
        writeFromVector(havok, stream, havokSize);

        stream.close();
    }
    else {
        printf("Could not open stream %s\n", filename.cString());
    }
}

void PapFile::writePap(hkStringBuf filename) {
    ofstream stream(filename, ios::binary);
    if (stream.is_open()) {
        writeFromVector(preHavok, stream, preHavokSize);
        writeFromVector(havok, stream, havokSize);
        writeFromVector(postHavok, stream, postHavokSize);

        stream.close();
    }
    else {
        printf("Could not open stream %s\n", filename.cString());
    }
}

void PapFile::replaceHavok(hkStringBuf filename) {
    havokSize = fileSize(filename);
    ifstream stream(filename, ios::binary);
    if (stream.is_open()) {
        readIntoVector(havok, stream, havokSize);
        auto newTimelineOffset = 26 + 40 + havokSize;
        writeInt(preHavok, 22, newTimelineOffset);

        stream.close();
    }
    else {
        printf("Could not open stream %s\n", filename.cString());
    }
}

// ==========================

void deleteFile(hkStringBuf path) {
    std::remove(path);
}
