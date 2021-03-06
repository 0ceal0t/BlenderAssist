#include "helper.h"

void read(hkIstream& stream, hkQsTransform& transform) {
    hkVector4 translation;
    hkQuaternion rotation;
    hkVector4 scale;

    stream.read(&translation, sizeof(hkVector4));
    stream.read(&rotation.m_vec, sizeof(hkVector4));
    stream.read(&scale, sizeof(hkVector4));

    transform.setTranslation(translation);
    transform.setRotation(rotation);
    transform.setScale(scale);
}

int getBoneIdx(std::string trackName, hkRefPtr<hkaSkeleton> skl) {
    for(int boneIdx = 0; boneIdx < skl->m_bones.getSize(); boneIdx++) {
        auto boneName = skl->m_bones[boneIdx].m_name.cString();
        if (trackName == boneName) {
            return boneIdx;
        }
    }
    return -1;
}

bool getBound(int boneIdx, hkRefPtr<hkaAnimationBinding> binding) {
    for(int i = 0; i < binding->m_transformTrackToBoneIndices.getSize(); i++) {
        if(binding->m_transformTrackToBoneIndices[i] == boneIdx) {
            return true;
        }
    }
    return false;
}

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

        headerType2 = (headerVersion == 0x31333030);

        if (!headerType2) { // Header 1
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

void SklbFile::writeSklb(hkStringBuf filename) {
    ofstream stream(filename, ios::binary);
    if (stream.is_open()) {
        writeFromVector(preHavok, stream, preHavokSize);
        writeFromVector(havok, stream, havokSize);

        stream.close();
    }
    else {
        printf("Could not open stream %s\n", filename.cString());
    }
}

void SklbFile::replaceHavok(hkStringBuf filename) {
    havokSize = fileSize(filename);
    ifstream stream(filename, ios::binary);
    if (stream.is_open()) {
        readIntoVector(havok, stream, havokSize);

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

std::string dirnameOf(const std::string& fname) {
    size_t pos = fname.find_last_of("\\/");
    return (std::string::npos == pos)
           ? ""
           : fname.substr(0, pos);
}

hkStringBuf concat(std::string baseDirStr, std::string fileName) {
    hkStringBuf baseDir(baseDirStr.c_str());
    if (baseDir.getLength() == 0) {
        baseDir.append(fileName.c_str());
        return baseDir;
    }

    baseDir.append("\\");
    baseDir.append(fileName.c_str());
    return baseDir;
}