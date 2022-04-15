#include "extract.h"
#include "helper.h"

#include <Common/Base/Memory/System/Util/hkMemoryInitUtil.h>
#include <Common/Base/Reflection/Registry/hkDefaultClassNameRegistry.h>
#include <Common/Serialize/Version/hkVersionPatchManager.h>
#include <Common/Base/Reflection/hkInternalClassMember.h>

int extract(const hkStringBuf skl_in_sklb, const hkStringBuf anim_in_pap, const hkStringBuf sklb_out, const hkStringBuf pap_out) {
    SklbFile sklbFile;
    sklbFile.read(skl_in_sklb);
    sklbFile.writeHavok(sklb_out);

    if(anim_in_pap.getLength() > 0 && pap_out.getLength() > 0) { // Only extract skeleton
        PapFile papFile;
        papFile.read(anim_in_pap);
        papFile.writeHavok(pap_out);
    }

    return 0;
}