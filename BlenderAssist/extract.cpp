#include "extract.h"
#include "filehelper.h"

#include <Common/Base/Memory/System/Util/hkMemoryInitUtil.h>
#include <Common/Base/Reflection/Registry/hkDefaultClassNameRegistry.h>
#include <Common/Serialize/Version/hkVersionPatchManager.h>
#include <Common/Base/Reflection/hkInternalClassMember.h>

int extract(const hkStringBuf skl_in_sklb, const hkStringBuf anim_in_pap, const hkStringBuf sklb_out, const hkStringBuf pap_out) {
    PapFile papFile;
    papFile.read(anim_in_pap);

    SklbFile sklbFile;
    sklbFile.read(skl_in_sklb);

    papFile.writeHavok(pap_out);

    sklbFile.writeHavok(sklb_out);

    return 0;
}