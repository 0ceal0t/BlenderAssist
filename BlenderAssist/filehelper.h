#ifndef BLENDERASSIST_FILEHELPER_H
#define BLENDERASSIST_FILEHELPER_H

#include <Common/Base/hkBase.h>
#include <Common/Base/Container/String/hkStringBuf.h>
#include <iostream>
#include <cstdio>
#include <vector>
#include <fstream>

using namespace std;

class SklbFile{
private:
    bool headerType2;
    vector<char> preHavok;
    vector<char> havok;

    int preHavokSize;
    int havokSize;
public:
    void read(hkStringBuf filename);
    void writeHavok(hkStringBuf filename);
    void writeSklb(hkStringBuf filename);
    void replaceHavok(hkStringBuf filename);
};

class PapFile{
private:
    vector<char> preHavok;
    vector<char> havok;
    vector<char> postHavok;

    int preHavokSize;
    int havokSize;
    int postHavokSize;
public:
    void read(hkStringBuf filename);
    void writeHavok(hkStringBuf filename);
    void writePap(hkStringBuf filename);
    void replaceHavok(hkStringBuf filename);
};

void deleteFile(hkStringBuf path);
std::string dirnameOf(const std::string& fname);
hkStringBuf concat(std::string baseDirStr, std::string fileName);

#endif //BLENDERASSIST_FILEHELPER_H