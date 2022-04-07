#include "hklib/hk_base.hpp"
#include "internal/hk_rootlevelcontainer.hpp"
#include "havok_xml.hpp"

#include <fstream>
using namespace std;

#define _SILENCE_EXPERIMENTAL_FILESYSTEM_DEPRECATION_WARNING
#include <experimental/filesystem>

void SaveEnvData(xmlEnvironment *env, const std::string &fileName) {
    auto fullPath = std::experimental::filesystem::absolute(fileName).generic_string();
    auto pathInfo = std::experimental::filesystem::path(fullPath);
    auto outputFolder = pathInfo.parent_path().generic_string();
    auto outputFilename = pathInfo.filename().generic_string();

    xmlEnvironmentVariable asset;
    asset.name = "asset";
    asset.value = outputFilename;
    env->storage.push_back(asset);

    xmlEnvironmentVariable assetFolder;
    assetFolder.name = "assetFolder";
    assetFolder.value = outputFolder;
    env->storage.push_back(assetFolder);

    xmlEnvironmentVariable assetPath;
    assetPath.name = "assetPath";
    assetPath.value = fullPath;
    env->storage.push_back(assetPath);

    xmlEnvironmentVariable out;
    out.name = "out";
    out.value = outputFilename;
    env->storage.push_back(out);

    xmlEnvironmentVariable outFolder;
    outFolder.name = "outFolder";
    outFolder.value = outputFolder;
    env->storage.push_back(outFolder);

    xmlEnvironmentVariable outPath;
    outPath.name = "outPath";
    outPath.value = fullPath;
    env->storage.push_back(outPath);
}

void ProcessAnimation(xmlAnimationBinding *binds, xmlInterleavedAnimation *anim, fstream &stream) {
    anim->animType = HK_INTERLEAVED_ANIMATION;

    int numOriginalFrames;
    int numTransforms;
    float duration;

    stream.read((char*)&numOriginalFrames, sizeof(int));
    stream.read((char*)&numTransforms, sizeof(int));
    stream.read((char*)&duration, sizeof(float));

    printf("Number of original frames %d\n", numOriginalFrames);
    printf("Number of tracks %d\n", numTransforms);

    anim->duration = duration;
    anim->annotations.reserve(numTransforms);

    for(int trackIdx = 0; trackIdx < numTransforms; trackIdx++) {
        binds->transformTrackToBoneIndices.push_back(trackIdx);

        char buf[240];
        stream.getline(buf, 240, '\0');

        xmlInterleavedAnimation::transform_container *aCont = new xmlInterleavedAnimation::transform_container;
        aCont->reserve(numOriginalFrames);

        for(int frame = 0; frame < numOriginalFrames + 1; frame++) {
            hkQTransform transform;

            Vector4A16 translation;
            Vector4A16 rotation;
            Vector4A16 scale;

            stream.read((char*)&translation, sizeof(Vector4A16));
            stream.read((char*)&rotation, sizeof(Vector4A16));
            stream.read((char*)&scale, sizeof(Vector4A16));

            transform.translation = translation;
            transform.rotation = rotation;
            transform.scale = scale;

            aCont->push_back(transform);
        }

        if (aCont->size() == 1) {
            for (auto &t : *aCont) {
                aCont->push_back(aCont->at(0));
            }
        }

        anim->transforms.emplace_back(aCont);

        xmlAnnotationTrack annot;
        annot.name = buf;
        anim->annotations.push_back(annot);
    }
}

int main(int argc, const char** argv) {
    auto inFile = argv[1];
    auto outFile = argv[2];

    xmlHavokFile hkFile = {};
    auto *cont = hkFile.NewClass<xmlRootLevelContainer>();
    auto *aniCont = hkFile.NewClass<xmlAnimationContainer>();
    xmlEnvironment *envData = hkFile.NewClass<xmlEnvironment>();

    cont->AddVariant(aniCont);
    cont->AddVariant(envData);
    SaveEnvData(envData, outFile); // TODO: ???

    auto *binding = hkFile.NewClass<xmlAnimationBinding>();
    auto *anim = hkFile.NewClass<xmlInterleavedAnimation>();
    binding->animation = anim;
    aniCont->animations.push_back(binding->animation);
    aniCont->bindings.push_back(binding);

    binding->skeletonName = "c0101_0:mdl:n_root";

    fstream inStream( inFile, ios::in | ios::out | ios::binary );
    ProcessAnimation(binding, anim, inStream);
    hkFile.ToXML(std::to_string(outFile), hkToolset(HK2014));
    inStream.close();

    return 0;
}