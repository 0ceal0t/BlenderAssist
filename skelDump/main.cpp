#include <iostream>
#include <cstdio>

#include <Common/Base/hkBase.h>
#include <Common/Base/Memory/System/Util/hkMemoryInitUtil.h>
#include <Common/Base/System/Io/IStream/hkIStream.h>
#include <Common/Base/Reflection/Registry/hkDefaultClassNameRegistry.h>
#include <Common/Serialize/Util/hkRootLevelContainer.h>
#include <Common/Serialize/Util/hkLoader.h>
#include <Common/Serialize/Util/hkSerializeUtil.h>
#include <Common/Serialize/Version/hkVersionPatchManager.h>
#include <Common/Base/Reflection/hkInternalClassMember.h>
#include <Common/Serialize/Util/hkSerializeDeprecated.h>
#include <Animation/Animation/Rig/hkaSkeletonUtils.h>
#include <Animation/Animation/Animation/SplineCompressed/hkaSplineCompressedAnimation.h>

#include <Animation/Animation/hkaAnimationContainer.h>
#include <shellapi.h>
#include <locale>
#include <codecvt>

#include "Common/Base/System/Init/PlatformInit.cxx"

#include <iostream>
#include <fstream>
#include <string>
using namespace std;

static void HK_CALL errorReport(const char* msg, void* userContext)
{
    using namespace std;
    printf("%s", msg);
}

void init() {
    PlatformInit();
    hkMemoryRouter* memoryRouter = hkMemoryInitUtil::initDefault(hkMallocAllocator::m_defaultMallocAllocator, hkMemorySystem::FrameInfo(1024 * 1024));
    hkBaseSystem::init(memoryRouter, errorReport);
    PlatformFileSystemInit();
    hkSerializeDeprecatedInit::initDeprecated();
}

inline std::string convert_from_wstring(const std::wstring &wstr)
{
    std::wstring_convert<std::codecvt_utf8_utf16<wchar_t>, wchar_t> conv;
    return conv.to_bytes(wstr);
}

int main(int argc, const char** argv) {
    int nargc = 0;
    wchar_t** nargv;

    auto command_line = GetCommandLineW();
    if (command_line == nullptr)
    {
        printf("Fatal error.");
        return 1;
    }
    nargv = CommandLineToArgvW(command_line, &nargc);
    if (nargv == nullptr)
    {
        printf("Fatal error.");
        return 1;
    }

    hkStringBuf hkt;
    hkStringBuf skel_hkt;
    hkStringBuf skel_out;

    hkRootLevelContainer* skel_root_container;

    skel_hkt = convert_from_wstring(nargv[1]).c_str();
    skel_out = convert_from_wstring(nargv[2]).c_str();

    init();
    auto loader = new hkLoader();

    skel_root_container = loader->load(skel_hkt);
    auto* skl_container = reinterpret_cast<hkaAnimationContainer*>(skel_root_container->findObjectByType(hkaAnimationContainerClass.getName()));

    printf("Skeletons %d\n", skl_container->m_skeletons.getSize());

    if (skl_container->m_skeletons.getSize() == 0) return 0;

    ofstream skelFile(skel_out);

    if(skelFile.is_open())
    {
        for(int i = 0; i < skl_container->m_skeletons[0]->m_bones.getSize(); i++) {
            skelFile << skl_container->m_skeletons[0]->m_bones[i].m_name;
            skelFile << "\n";
        }
        skelFile.close();
    }

    return 0;
}

#include <Common/Base/keycode.cxx>

#undef HK_FEATURE_PRODUCT_AI
//#undef HK_FEATURE_PRODUCT_ANIMATION
#undef HK_FEATURE_PRODUCT_CLOTH
#undef HK_FEATURE_PRODUCT_DESTRUCTION_2012
#undef HK_FEATURE_PRODUCT_DESTRUCTION
#undef HK_FEATURE_PRODUCT_BEHAVIOR
#undef HK_FEATURE_PRODUCT_PHYSICS_2012
#undef HK_FEATURE_PRODUCT_SIMULATION
#undef HK_FEATURE_PRODUCT_PHYSICS

#define HK_SERIALIZE_MIN_COMPATIBLE_VERSION 201130r1

#include <Common/Base/Config/hkProductFeatures.cxx>