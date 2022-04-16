#include "pack_anim.h"
#include "helper.h"
#include <iostream>
#include <cstdio>
#include <vector>
#include <string>

#include <Common/Serialize/Util/hkLoader.h>
#include <Common/Serialize/Util/hkSerializeUtil.h>
#include <Animation/Animation/Animation/Interleaved/hkaInterleavedUncompressedAnimation.h>
#include <Animation/Animation/Animation/SplineCompressed/hkaSplineCompressedAnimation.h>

void read(hkRefPtr<hkaInterleavedUncompressedAnimation> anim, hkRefPtr<hkaAnimationBinding> binding, hkRefPtr<hkaSkeleton> skl, hkIstream stream, bool checkIfOriginalBound) {
    int numOriginalFrames;
    int numAllTransforms;
    hkReal duration;

    stream.read(&numOriginalFrames, sizeof(int));
    numOriginalFrames += 1; // to account for t=0
    stream.read(&numAllTransforms, sizeof(int));
    stream.read(&duration, sizeof(hkReal));

    // Get all tracks

    std::vector<std::string> allTrackNames;

    for(int trackIdx = 0; trackIdx < numAllTransforms; trackIdx++) {
        char trackNameBuffer[240];
        stream.getline(trackNameBuffer, 240, '\0');
        std::string trackName(trackNameBuffer);
        allTrackNames.push_back(trackName);
    }

    // Which ones are actually in the skeleton

    std::vector<int> validTrackIndex;
    for(int trackIdx = 0; trackIdx < numAllTransforms; trackIdx++) {
        validTrackIndex.push_back(-1); // all not valid for now
    }

    printf("Check if bound: %d\n", checkIfOriginalBound);

    int numTransforms = 0; // number of valid transforms

    for(int boneIdx = 0; boneIdx < skl->m_bones.getSize(); boneIdx++) {
        if (checkIfOriginalBound && !getBound(boneIdx, binding)) { continue; } // this bone was never bound
        auto boneName = skl->m_bones[boneIdx].m_name;

        for(int trackIdx = 0; trackIdx < numAllTransforms; trackIdx++) {
            auto trackName = allTrackNames[trackIdx];

            if (trackName.compare(boneName.cString()) == 0) {
                validTrackIndex[trackIdx] = numTransforms;
                numTransforms++;
                break;
            }
        }
    }

    // Set up tracks

    printf("Number of original frames %d\n", numOriginalFrames);
    printf("Number of tracks %d (%d)\n", numTransforms, numAllTransforms);
    printf("Original number of tracks %d\n", binding->m_transformTrackToBoneIndices.getSize());

    anim->m_duration = duration;
    anim->m_annotationTracks.clear();
    anim->m_annotationTracks.setSize(0); //anim->m_annotationTracks.setSize(numTransforms);
    anim->m_numberOfFloatTracks = 0;
    anim->m_numberOfTransformTracks = numTransforms;
    anim->m_floats.setSize(0);
    anim->m_transforms.setSize(numTransforms * numOriginalFrames, hkQsTransform::getIdentity());

    // Set up bindings

    binding->m_transformTrackToBoneIndices.clear();
    binding->m_transformTrackToBoneIndices.setSize(numTransforms);

    for(int trackIdx = 0; trackIdx < numAllTransforms; trackIdx++) {
        auto idx = validTrackIndex[trackIdx];
        if (idx == -1) continue;
        auto trackName = allTrackNames[trackIdx];
        auto boneIdx = getBoneIdx(trackName, skl);
        binding->m_transformTrackToBoneIndices[idx] = boneIdx;
    }

    // Read frames

    for(int frameIdx = 0; frameIdx < numOriginalFrames; frameIdx++) {
        int offTransforms = frameIdx * numTransforms;

        for(int trackIdx = 0; trackIdx < numAllTransforms; trackIdx++) {
            auto idx = validTrackIndex[trackIdx];

            if(idx == -1) {
                hkQsTransformf dummyT;
                read(stream, dummyT);
            }
            else {
                read(stream, anim->m_transforms[idx + offTransforms]);
            }
        }
    }
}

int packHavok(const hkStringBuf anim_idx_str, const hkStringBuf bin_in, const hkStringBuf skl_in, const hkStringBuf anim_in, const hkStringBuf anim_out, const hkStringBuf check_if_bound_str) {
    int anim_idx = std::stoi(anim_idx_str.cString());
    bool checkIfOriginalBound = std::stoi(check_if_bound_str.cString()) == 1;

    hkRootLevelContainer* skl_root_container;
    hkRootLevelContainer* anim_root_container;

    auto loader = new hkLoader();

    hkIstream stream(bin_in);
    hkOstream out_stream(anim_out);

    skl_root_container = loader->load(skl_in);
    auto* skl_container = reinterpret_cast<hkaAnimationContainer*>(skl_root_container->findObjectByType(hkaAnimationContainerClass.getName()));
    auto skl = skl_container->m_skeletons[0];

    anim_root_container = loader->load(anim_in);
    auto* anim_container = reinterpret_cast<hkaAnimationContainer*>(anim_root_container->findObjectByType(hkaAnimationContainerClass.getName()));

    auto anim_ptr = anim_container->m_animations[anim_idx];
    auto binding_ptr = anim_container->m_bindings[anim_idx];
    auto binding = hkRefPtr<hkaAnimationBinding>(binding_ptr);

    // ========================

    hkRefPtr<hkaInterleavedUncompressedAnimation> storeAnim = new hkaInterleavedUncompressedAnimation();

    hkaSplineCompressedAnimation::TrackCompressionParams tparams;
    hkaSplineCompressedAnimation::AnimationCompressionParams aparams;
    //tparams.m_rotationTolerance = 0.001f;
    //tparams.m_rotationQuantizationType = hkaSplineCompressedAnimation::TrackCompressionParams::THREECOMP40;

    read(storeAnim, binding, skl, stream, checkIfOriginalBound);

    auto final_anim = new hkaSplineCompressedAnimation( *storeAnim.val(), tparams, aparams );
    binding->m_animation = final_anim;
    anim_container->m_animations[anim_idx] = final_anim;

    auto anim = hkRefPtr<hkaAnimation>(anim_ptr);

    // ========================

    auto res = hkSerializeUtil::saveTagfile(anim_root_container, hkRootLevelContainer::staticClass(), out_stream.getStreamWriter(), nullptr, hkSerializeUtil::SAVE_DEFAULT);
    if (res.isSuccess()) {
        return 0;
    } else {
        std::cout << "\n\nAn error occurred while saving the HKX...\n";
        return 1;
    }
}

int pack_anim(const hkStringBuf anim_idx_str, const hkStringBuf bin_in, const hkStringBuf skl_in_sklb, const hkStringBuf anim_in_pap, const hkStringBuf anim_out_pap, const hkStringBuf check_if_bound_str) {
    PapFile papFile;
    papFile.read(anim_in_pap);

    SklbFile sklbFile;
    sklbFile.read(skl_in_sklb);

    auto baseDir = dirnameOf(anim_out_pap.cString());

    auto original_anim_temp = concat(baseDir, "original_anim_temp.hkx");
    papFile.writeHavok(original_anim_temp);

    auto original_skl_temp = concat(baseDir, "original_skl_temp.hkx");
    sklbFile.writeHavok(original_skl_temp);

    auto new_anim_temp = concat(baseDir, "new_anim_temp.hkx");
    auto res = packHavok(anim_idx_str, bin_in, original_skl_temp, original_anim_temp, new_anim_temp, check_if_bound_str);

    papFile.replaceHavok(new_anim_temp);
    papFile.writePap(anim_out_pap);

    deleteFile(original_anim_temp);
    deleteFile(original_skl_temp);
    deleteFile(new_anim_temp);

    return res;
}