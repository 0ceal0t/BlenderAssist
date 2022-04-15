#include "pack_skel.h"
#include "filehelper.h"
#include <iostream>
#include <cstdio>
#include <vector>
#include <string>

#include <Common/Base/Memory/System/Util/hkMemoryInitUtil.h>
#include <Common/Base/System/Io/IStream/hkIStream.h>
#include <Common/Base/Reflection/Registry/hkDefaultClassNameRegistry.h>
#include <Common/Serialize/Util/hkRootLevelContainer.h>
#include <Common/Serialize/Util/hkLoader.h>
#include <Common/Serialize/Util/hkSerializeUtil.h>
#include <Common/Serialize/Version/hkVersionPatchManager.h>
#include <Common/Base/Reflection/hkInternalClassMember.h>

#include <Animation/Animation/hkaAnimationContainer.h>
#include <Animation/Animation/Animation/Interleaved/hkaInterleavedUncompressedAnimation.h>
#include <Animation/Animation/Animation/SplineCompressed/hkaSplineCompressedAnimation.h>

int pack_skel(const hkStringBuf bin_in, const hkStringBuf skl_in_sklb, const hkStringBuf skl_out_sklb) {
    SklbFile sklbFile;
    sklbFile.read(skl_in_sklb);

    auto baseDir = dirnameOf(skl_out_sklb.cString());

    auto original_skl_temp = concat(baseDir, "original_skl_temp.hkx");
    sklbFile.writeHavok(original_skl_temp);

    auto new_skl_temp = concat(baseDir, "new_skl_temp.hkx");
    //auto res = packHavok(anim_idx_str, bin_in, original_skl_temp, original_anim_temp, new_anim_temp); // TODO

    sklbFile.replaceHavok(new_skl_temp);
    sklbFile.writeSklb(skl_out_sklb);

    deleteFile(original_skl_temp);
    deleteFile(new_skl_temp);

    //return res;
    return 0;
}