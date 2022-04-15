#include "pack_skel.h"
#include "helper.h"
#include <iostream>
#include <cstdio>
#include <vector>
#include <string>

#include <Common/Serialize/Util/hkLoader.h>
#include <Common/Serialize/Util/hkSerializeUtil.h>

void read(hkRefPtr<hkaSkeleton> skl, hkIstream stream) {
    int numBones;
    stream.read(&numBones, sizeof(int));

    for(int i = 0; i < numBones; i++) {
        char boneNameBuffer[240];
        stream.getline(boneNameBuffer, 240, '\0');
        std::string boneName(boneNameBuffer);

        char boneParentBuffer[240];
        stream.getline(boneParentBuffer, 240, '\0');
        std::string boneParent(boneParentBuffer);

        auto boneIdx = getBoneIdx(boneName, skl);
        auto newBone = boneIdx == -1;

        if (newBone) {
            printf("New bone: %s\n", boneName.c_str());

            skl->m_bones.expandOne();
            skl->m_parentIndices.expandOne();
            skl->m_referencePose.expandOne();

            boneIdx = skl->m_bones.getSize() - 1;

            hkStringBuf nameBuf(boneNameBuffer, boneName.length());
            skl->m_bones[boneIdx].m_name = nameBuf;
            skl->m_bones[boneIdx].m_lockTranslation = false;
        }

        int boneParentIdx = -1;
        if (boneParent.compare("None") != 0) {
            boneParentIdx = getBoneIdx(boneParent, skl);
        }

        if(!newBone) {
            printf("Idx: %d Old parent %d New parent %d / %s\n", boneIdx, skl->m_parentIndices[boneIdx], boneParentIdx, boneName.c_str());
        }

        skl->m_parentIndices[boneIdx] = boneParentIdx;

        read(stream, skl->m_referencePose[boneIdx]);
    }
}

int packHavok(const hkStringBuf bin_in, const hkStringBuf skl_in, const hkStringBuf skel_out) {
    hkRootLevelContainer* skl_root_container;

    auto loader = new hkLoader();

    hkIstream stream(bin_in);
    hkOstream out_stream(skel_out);

    skl_root_container = loader->load(skl_in);
    auto* skl_container = reinterpret_cast<hkaAnimationContainer*>(skl_root_container->findObjectByType(hkaAnimationContainerClass.getName()));
    auto skl = skl_container->m_skeletons[0];

    read(skl, stream);

    auto res = hkSerializeUtil::saveTagfile(skl_root_container, hkRootLevelContainer::staticClass(), out_stream.getStreamWriter(), nullptr, hkSerializeUtil::SAVE_DEFAULT);
    if (res.isSuccess()) {
        return 0;
    } else {
        std::cout << "\n\nAn error occurred while saving the HKX...\n";
        return 1;
    }
}

int pack_skel(const hkStringBuf bin_in, const hkStringBuf skl_in_sklb, const hkStringBuf skl_out_sklb) {
    SklbFile sklbFile;
    sklbFile.read(skl_in_sklb);

    auto baseDir = dirnameOf(skl_out_sklb.cString());

    auto original_skl_temp = concat(baseDir, "original_skl_temp.hkx");
    sklbFile.writeHavok(original_skl_temp);

    auto new_skl_temp = concat(baseDir, "new_skl_temp.hkx");
    auto res = packHavok(bin_in, original_skl_temp, new_skl_temp);

    sklbFile.replaceHavok(new_skl_temp);
    sklbFile.writeSklb(skl_out_sklb);

    deleteFile(original_skl_temp);
    deleteFile(new_skl_temp);

    return res;
}